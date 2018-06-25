# -*- coding: utf-8 -*-
"""
Created on Tue Jun 12 12:43:59 2018

@author: guemruekcue
"""

from pyomo.environ import SolverFactory
from pyomo.core import *
from itertools import product
import time

#%%
class SystemParameters():
    
    def __init__(self,opt_horizon,ess_capacity,vir_capacity):

        self.T=opt_horizon              #Optimization horizon
        self.ess_capacity=ess_capacity  #capacity of energy storage system: kWh 
        self.vir_capacity=vir_capacity  #capacity of virtual EV battery

class DPParameters():
    
    def __init__(self,ess_soc_domain,virtual_soc_domain,solver,ess_decision,vir_decision,max_nb_of_cars,unitconsumption):
        
        self.ess_soc_domain=ess_soc_domain
        self.vir_soc_domain=virtual_soc_domain
        
        self.ess_decision_domain=ess_decision
        self.vir_decision_domain=vir_decision
        
        self.max_nb_of_cars=max_nb_of_cars
        self.unitconsumption=unitconsumption

class RTDataClass():
    
    def __init__(self,actual_ess_soc,actual_vir_soc,carsAway):
        
        self.ess_soc=actual_ess_soc
        self.vir_soc=actual_vir_soc
        self.carsAway=carsAway

class MinimizeImport():
    
    def __init__(self,systemParameters,dpParameters,load_forecast,pv_forecast,pdfs,solver,coef1,coef2):

        self.solver=solver       
        self.coef1=coef1
        self.coef2=coef2
        
        # Time parameters
        self.T=systemParameters.T  #Total number of time steps: Optimization horizon

        #Battery capacities
        
        self.ess_capacity=systemParameters.ess_capacity 
        self.vir_capacity=systemParameters.vir_capacity 
        
        #Forecasts
        self.P_Load_Forecast =load_forecast
        self.P_PV_Forecast   =pv_forecast
            
        #Indices
        self.time_decision_IndexSet=list(range(0,self.T))      
        self.time_value_IndexSet=list(range(0,self.T+1))  
        self.ess_soc_IndexSet=dpParameters.ess_soc_domain
        self.vir_soc_IndexSet=dpParameters.vir_soc_domain
        
        #Initialize empty lookup tables
        keylistforValue    =[(t,s_ess,s_vir) for t,s_ess,s_vir in product(self.time_value_IndexSet   ,self.ess_soc_IndexSet,self.vir_soc_IndexSet)]
        keylistforDecisions=[(t,s_ess,s_vir) for t,s_ess,s_vir in product(self.time_decision_IndexSet,self.ess_soc_IndexSet,self.vir_soc_IndexSet)]
        
        self.Value   =dict.fromkeys(keylistforValue)
        self.Decision=dict.fromkeys(keylistforDecisions)
    
        for t,s_ess,s_vir in product(self.time_decision_IndexSet,self.ess_soc_IndexSet,self.vir_soc_IndexSet):
            self.Decision[t,s_ess,s_vir]={'PV':None,'Grid':None,'ESS':None,'Virtual_Battery':None}

        for t,s_ess,s_vir in product(self.time_value_IndexSet,self.ess_soc_IndexSet,self.vir_soc_IndexSet):
            if t<self.T:
                self.Value[t,s_ess,s_vir]=None
            else:
                if s_vir>=0:
                    self.Value[t,s_ess,s_vir]=0         #No inherent value of end states if soc of virtual battery is greater than 0
                else:
                    self.Value[t,s_ess,s_vir]=-s_vir    #Value of end states if soc of virtual battery is less than 0 equals to the deficit soc
                
        #Pdfs of driving probabilities
        self.pdfs=pdfs
        #Max number of driving car at during one time step
        self.max_nb_of_cars=dpParameters.max_nb_of_cars
        #How much SoC of virtual battery is consumed when one car drives for an hour
        self.unitconsumption=dpParameters.unitconsumption
        
        #Charge-discharge decision domain for ESS
        self.ess_decision_domain=dpParameters.ess_decision_domain
        
        #Charge decision domain for virtual battery
        self.vir_decision_domain=dpParameters.vir_decision_domain

    def probcalculate(self,timestep,initialSoC,chargePower,finalSoC):
        
        drivePower=initialSoC+chargePower-finalSoC
        nb_drivingCar=int(drivePower/self.unitconsumption)
        
        if (timestep,nb_drivingCar) in self.pdfs.keys():
            probability=self.pdfs[timestep,nb_drivingCar]
        else:
            probability=0
        
        return probability  
        
    def optimaldecisioncalculator(self,timestep,ini_ess_soc,ini_vir_soc):
        """
        Solves the optimization problem for a particular initial state at the time step
        """
        
        #print("Initial state",ini_ess_soc,ini_vir_soc)
        model = ConcreteModel()
        #coef1=1
        #coef2=3

        feasible_Pess=[]
        parameters_Pess={}
        for P_ESS in self.ess_decision_domain:
            if min(self.ess_soc_IndexSet)<=P_ESS+ini_ess_soc<=max(self.ess_soc_IndexSet):
                feasible_Pess.append(P_ESS)
                parameters_Pess[P_ESS]=P_ESS    
        model.decision_ess=Set(initialize=feasible_Pess)
        model.power_ess=Param(model.decision_ess,initialize=parameters_Pess)
              
        feasible_Pvir=[]
        parameters_Pvir={}
        for P_EV in self.vir_decision_domain:
            if P_EV+ini_vir_soc<=max(self.vir_soc_IndexSet):
                feasible_Pvir.append(P_EV)
                parameters_Pvir[P_EV]=P_EV      
        model.decision_vir=Set(initialize=feasible_Pvir) 
        model.power_vir=Param(model.decision_vir,initialize=parameters_Pvir)
       
        #expected_drive=sum([self.pdfs[timestep,n]*n*self.unitconsumption for n in range(0,self.max_nb_of_cars+1)])
        expected_drive=self.max_nb_of_cars*self.unitconsumption
        deficit=-(ini_vir_soc-expected_drive) if ini_vir_soc-expected_drive<0 else 0
        model.deficit=Param(initialize=deficit)
        
        #Combined decision        
        model.Decision=Var(model.decision_ess,model.decision_vir,within=Binary)
   
        model.P_PV=Var(bounds=(0,self.P_PV_Forecast[timestep]))
        model.P_GRID=Var(bounds=(0,10000)) 

        def demandmeeting(model):
            dynamic_expr=sum(model.Decision[p1,p2]*model.power_ess[p1]/100*self.ess_capacity+model.Decision[p1,p2]*model.power_vir[p2]/100*self.vir_capacity for p1,p2 in product(model.decision_ess,model.decision_vir))
            return self.P_Load_Forecast[timestep]+dynamic_expr==model.P_PV+model.P_GRID
        model.const_demand=Constraint(rule=demandmeeting)
            
        def combinatorics(model):
            return 1==sum(model.Decision[p1,p2] for p1,p2 in product(model.decision_ess,model.decision_vir))
        model.const_integer=Constraint(rule=combinatorics)
     
        def objrule1(model):
            future_value=0
            for p_ess in model.decision_ess:
                fin_ess_soc=ini_ess_soc+p_ess                
                for p_vir in model.decision_vir:   #each decision
                    
                    expected_value=0    #Expected value of taking decision combination (p_ess,p_vir)
                    
                    for fin_vir_soc in self.vir_soc_IndexSet:    #each end state of virtual battery
                        prob=self.probcalculate(timestep,ini_vir_soc,p_vir,fin_vir_soc)
                        expected_value+=prob*self.Value[timestep+1,fin_ess_soc,fin_vir_soc]

                    future_value+=model.Decision[p_ess,p_vir]*expected_value                                      
            
            return self.coef1*model.P_GRID+self.coef2*model.deficit+future_value
        model.obj=Objective(rule=objrule1,sense=minimize)        
                    
        result=self.solver.solve(model)
        
        P_PV=model.P_PV()
        P_GRID=model.P_GRID()
        
        for p1,p2 in product(model.decision_ess,model.decision_vir):            
            if model.Decision[p1,p2]()==1:
                P_ESS=p1
                P_VIR=p2
            
        V=model.obj()
                   
        return P_PV,P_GRID,P_ESS,P_VIR,V     
    
    def findstateoptimals(self,timestep):
        """
        Solves the optimizaton problem for every initial states at the time step
        """
        #print("Time step",timestep)
        for ini_ess_soc,ini_vir_soc in product(self.ess_soc_IndexSet,self.vir_soc_IndexSet):
            results=self.optimaldecisioncalculator(timestep,ini_ess_soc,ini_vir_soc)
            
            self.Decision[timestep,ini_ess_soc,ini_vir_soc]['PV']  =results[0]
            self.Decision[timestep,ini_ess_soc,ini_vir_soc]['Grid']=results[1]
            self.Decision[timestep,ini_ess_soc,ini_vir_soc]['ESS']=results[2]
            self.Decision[timestep,ini_ess_soc,ini_vir_soc]['Virtual_Battery']=results[3]
            self.Value[timestep,ini_ess_soc,ini_vir_soc]=results[4]        
            
    def wholeMapCalculation(self):
        """
        Calculates the optimal values of whole map
        """
        start=time.time()
        for timestep in reversed(self.time_decision_IndexSet):
            self.findstateoptimals(timestep)
        end=time.time()
        #print("Full execution:",end-start)
        
    def control_action(self,initial_ess_soc_value,initial_vir_soc_value):
        
        self.wholeMapCalculation()
        
        p_pv=self.Decision[0,initial_ess_soc_value,initial_vir_soc_value]['PV']
        p_grid=self.Decision[0,initial_ess_soc_value,initial_vir_soc_value]['Grid']
        p_ess=self.Decision[0,initial_ess_soc_value,initial_vir_soc_value]['ESS']/100*self.ess_capacity
        p_vir=self.Decision[0,initial_ess_soc_value,initial_vir_soc_value]['Virtual_Battery']/100*self.vir_capacity
        
        return p_pv,p_grid,p_ess,p_vir
         
#%%
if __name__ == "__main__":    
    
    opt1=SolverFactory('glpk',executable="C:/Users/guemruekcue/Anaconda3/pkgs/glpk-4.63-vc14_0/Library/bin/glpsol")
    opt2= SolverFactory("ipopt", executable="C:/Users/guemruekcue/Anaconda3/pkgs/ipopt-3.11.1-2/Library/bin/ipopt")
    opt3= SolverFactory("bonmin", executable="C:/cygwin/home/bonmin/Bonmin-1.8.6/build/bin/bonmin")
      
    from StatisticalAnalysis.analysispy import stats
    
    opt_horizon=24
    ess_capacity=80
    virtual_capacity=100
    systParam=SystemParameters(opt_horizon,ess_capacity,virtual_capacity)
    
    
    ess_soc_domain=range(0,110,10)
    virtual_soc_domain=range(0,105,5)
    ess_decision=range(-30,30,10)
    vir_decision=range(0,25,5)
    maxnbofcars=8
    unitconsumption=5
    dpParam=DPParameters(ess_soc_domain,virtual_soc_domain,opt1,ess_decision,vir_decision,maxnbofcars,unitconsumption)
    
    
    
    p_Load_Forecast={0:   0.57,1:   0.906,2:   0.906,3:   0.70066667,4:	0.77533333,5:	0.906,6:	0.906,7:	1.00935,
                     8:	3.8135,9:	14.73716667,10:	9.88183333,11:	24.413,12:	4.216,13:	2.1725,14:	4.536,15:	4.899,
                     16:	0.92466667,17:	0.88733333,18:	0.906,19:	4.7475,20:	4.8255,21:	10.51866667,22:	12.96316667,23:	2.00733333}
    
    p_PV_Forecast={  0:   0,1:	0,2:	0,3:	0,4:	0,5:	0,6:	0,7:	0,8:	11.3248512,9:	30.16735616,10:	48.23979947,
                     11:	63.29861639,12:	70.6663104,13:	74.2742784,14:	74.20178035,15:	70.77290784,16:	59.9361984,
                     17:	40.36273408,18:	14.62618829,19:	0,20:	0,21:	0,22:	0,23:	0} 
    pdfs=stats
    
    carparkopt=MinimizeImport(systParam,dpParam,p_Load_Forecast,p_PV_Forecast,pdfs,opt1)   
    print(carparkopt.control_action(30,40))
    decisions=carparkopt.Decision
    values=carparkopt.Value

