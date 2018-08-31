# -*- coding: utf-8 -*-
"""
Created on Thu Apr 26 15:06:49 2018

@author: guemruekcue
"""

from pyomo.environ import SolverFactory
from pyomo.core import *
from itertools import product

class DynamicMaximizePV():
    
    def __init__(self,scenarioParameters,ess_soc_domain,decision_domain,solver):
        """
        ess_soc_domain=[30,40,50,60,70] etc percentage
        decision_domain=[-20,-10,0,10,20]

        """
        self.solver=solver
        self.objective=1
        
        # Time parameters
        self.T=scenarioParameters['T']  #Total number of time steps: Optimization horizon
        self.dT=24*60*60/self.T      #Size of one time step: in seconds
        
        #Time invariant parameters
        self.PV_Inv_Max_Power       =scenarioParameters['PV_Inv_Max_Power']
        self.P_Grid_Max_Export_Power=scenarioParameters['P_Grid_Max_Export_Power']
        self.ESS_Min_SoC            =scenarioParameters['ESS_Min_SoC']
        self.ESS_Max_SoC            =scenarioParameters['ESS_Max_SoC']
        self.ESS_Capacity           =scenarioParameters['ESS_Capacity']
        self.ESS_Max_Charge_Power   =scenarioParameters['ESS_Max_Charge_Power']
        self.ESS_Max_Discharge_Power=scenarioParameters['ESS_Max_Discharge_Power']
        
        #Forecasts
        self.P_Load_Forecast =scenarioParameters['P_Load_Forecast']
        self.Q_Load_Forecast =scenarioParameters['Q_Load_Forecast']
        self.P_PV_Forecast   =scenarioParameters['P_PV_Forecast']
        self.Price_Forecast  =scenarioParameters['Price_Forecast']
            
        #Real-time data
        #self.ESS_SoC_Value =scenarioParameters.ESS_SoC_Value
        
        
        #Indices
        self.timeIndexSet=list(range(0,self.T))      #Will be represented as t
        self.valueIndexSet=list(range(0,self.T+1))     #Will be represented as t  
        self.stateIndexSet=ess_soc_domain
        
        #Initialize empty lookup tables
        keylistforValue    =[(t,s) for t,s in product(self.valueIndexSet,self.stateIndexSet)]
        keylistforDecisions=[(t,s) for t,s in product(self.timeIndexSet ,self.stateIndexSet)]
        
        self.Value   =dict.fromkeys(keylistforValue)
        self.Decision=dict.fromkeys(keylistforDecisions)
    
        for t,s in product(self.timeIndexSet ,self.stateIndexSet):
            self.Decision[t,s]={'P_PV':None,'Q_PV':None,'P_Grid':None,'Q_Grid':None,'P_ESS':None,'FinalSoC':None}
        
        #No inherent value of end state cases
        for s in self.stateIndexSet:
            self.Value[self.T,s]=0
        
        self.ess_decision_domain=decision_domain

    
    def optimaldecisioncalculator(self,timestep,initialsoc):
        """
        Solves the optimization problem for a particular initial state at the time step
        """
        model = ConcreteModel()

        feasible_Pess=[]
        parameters_Pess={}
        for P_ESS in self.ess_decision_domain:
            if min(self.stateIndexSet)<=P_ESS+initialsoc<=max(self.stateIndexSet):
                feasible_Pess.append(P_ESS)
                parameters_Pess[P_ESS]=P_ESS    
        model.decision_ess=Set(initialize=feasible_Pess)
        model.Decision=Var(model.decision_ess,within=Binary)
        
        model.P_PV=Var(bounds=(0,self.P_PV_Forecast[timestep]))
        model.Q_PV=Var(bounds=(0,self.P_PV_Forecast[timestep]))
        model.P_ESS=Var(bounds=(-self.ESS_Max_Charge_Power,self.ESS_Max_Discharge_Power))
        model.P_GRID=Var(bounds=(-self.P_Grid_Max_Export_Power,10000))   
        model.Q_GRID=Var(bounds=(-self.P_Grid_Max_Export_Power,10000))
        
        def pess(model):
            return model.P_ESS==-sum(model.Decision[x]*x for x in model.decision_ess)/100*self.ESS_Capacity*3600/self.dT
        model.const_p_ess=Constraint(rule=pess)

        def combinatorics(model):
            return sum(model.Decision[x] for x in model.decision_ess)==1
        model.const_com=Constraint(rule=combinatorics)
        
        def delta_soc(model):
            return self.ESS_Min_SoC<=initialsoc/100-model.P_ESS*self.dT/self.ESS_Capacity/3600<=self.ESS_Max_SoC
        model.const_soc=Constraint(rule=delta_soc)
        
        def p_demandmeeting(model):
            return self.P_Load_Forecast[timestep]==model.P_PV+model.P_ESS+model.P_GRID
        model.const_p_demand=Constraint(rule=p_demandmeeting)

        def q_demandmeeting(model):
            return self.Q_Load_Forecast[timestep]==model.Q_PV+model.Q_GRID
        model.const_q_demand=Constraint(rule=q_demandmeeting)

        def pv_const(model):
            return self.P_PV_Forecast[timestep]>=model.P_PV*model.P_PV+model.Q_PV*model.Q_PV
        model.const_pv_gen=Constraint(rule=pv_const)
        
        def objrule1(model):
            return model.P_PV*model.P_PV+model.Q_PV*model.Q_PV+sum(model.Decision[x]*self.Value[timestep+1,initialsoc+x] for x in model.decision_ess)
        model.obj=Objective(rule=objrule1,sense=maximize)        
 
        #model.pprint()
        self.solver.solve(model)
        
        P_PV=model.P_PV()
        Q_PV=model.Q_PV()
        P_ESS=model.P_ESS()
        P_GRID=model.P_GRID()
        Q_GRID=model.Q_GRID()
            
        finalsoc=initialsoc+sum(model.Decision[x]()*x for x in model.decision_ess)
        V=model.obj()
                   
        return P_ESS,P_PV,Q_PV,P_GRID,Q_GRID,finalsoc,V       
    
    def findstateoptimals(self,timestep):
        """
        Solves the optimizaton problem for every initial states at the time step
        """
        #print("Time step",timestep)
        for ini_soc in self.stateIndexSet:
            results=self.optimaldecisioncalculator(timestep,ini_soc)
            
            self.Decision[timestep,ini_soc]['P_ESS'] =results[0]
            self.Decision[timestep,ini_soc]['P_PV']  =results[1]
            self.Decision[timestep,ini_soc]['Q_PV'] =results[2]
            self.Decision[timestep,ini_soc]['P_Grid']=results[3]
            self.Decision[timestep,ini_soc]['Q_Grid']=results[4]
            self.Decision[timestep,ini_soc]['FinalSoC']=results[5]
        
            self.Value[timestep,ini_soc]=results[6]
            
    def wholeMapCalculation(self):
        """
        Calculates the optimal values of whole map
        """
        for timestep in reversed(self.timeIndexSet):
            self.findstateoptimals(timestep)
            
    def calculateOptimalTrajectory(self,ESS_SoC_Value):
        """
        Solves the dynamic program to draw the optimal operation trajectory for a given real time SoC data 
        """
        self.wholeMapCalculation()
        self.P_PV=[]
        self.Q_PV=[]
        self.P_ESS=[]
        self.P_Grid=[]
        self.Q_Grid=[]
    
        for t in self.timeIndexSet:      
            if t==0:
                initialstate=int(ESS_SoC_Value)
            else:
                initialstate=int(finalstate)

            self.P_PV.append(self.Decision[t,initialstate]['P_PV'])
            self.Q_PV.append(self.Decision[t,initialstate]['Q_PV'])
            self.P_ESS.append(self.Decision[t,initialstate]['P_ESS'])
            self.P_Grid.append(self.Decision[t,initialstate]['P_Grid'])
            self.Q_Grid.append(self.Decision[t,initialstate]['Q_Grid'])
            finalstate=self.Decision[t,initialstate]['FinalSoC']
         

if __name__=="__main__":
    
    opt1=SolverFactory('glpk',executable="C:/Users/guemruekcue/Anaconda3/pkgs/glpk-4.63-vc14_0/Library/bin/glpsol")
    opt2= SolverFactory("ipopt", executable="C:/Users/guemruekcue/Anaconda3/pkgs/ipopt-3.11.1-2/Library/bin/ipopt")
    opt3= SolverFactory("bonmin", executable="C:/cygwin/home/bonmin/Bonmin-1.8.6/build/bin/bonmin")
  
    import time


    scenario_24Ts={}
    scenario_24Ts['T']=24
    scenario_24Ts['PV_Inv_Max_Power']= 10.0
    scenario_24Ts['P_Grid_Max_Export_Power']= 10.0
    scenario_24Ts['ESS_Min_SoC']=0.25
    scenario_24Ts['ESS_Max_SoC']=0.95
    scenario_24Ts['ESS_Capacity']= 9.6   #kWh
    scenario_24Ts['ESS_Max_Charge_Power']= 6.2   #kW
    scenario_24Ts['ESS_Max_Discharge_Power']= 6.2   #kW
    
    #Forecasts  
    scenario_24Ts['Q_Load_Forecast']=dict.fromkeys(range(24),0.00)
    scenario_24Ts['P_Load_Forecast']={0:   0.057,
                                     1:   0.0906,
                                     2:   0.0906,
                                     3:   0.070066667,
                                     4:	0.077533333,
                                     5:	0.0906,
                                     6:	0.0906,
                                     7:	0.10935,
                                     8:	0.38135,
                                     9:	1.473716667,
                                     10:	0.988183333,
                                     11:	2.4413,
                                     12:	0.4216,
                                     13:	0.21725,
                                     14:	0.4536,
                                     15:	0.4899,
                                     16:	0.092466667,
                                     17:	0.088733333,
                                     18:	0.0906,
                                     19:	0.47475,
                                     20:	0.48255,
                                     21:	1.051866667,
                                     22:	1.296316667,
                                     23:	0.200733333}
        
    scenario_24Ts['P_PV_Forecast']={ 0: 0,
                                     1:	0,
                                     2:	0,
                                     3:	0,
                                     4:	0,
                                     5:	0,
                                     6:	0,
                                     7:	0,
                                     8:	1.13248512,
                                     9:	3.016735616,
                                     10:	4.823979947,
                                     11:	6.329861639,
                                     12:	7.06663104,
                                     13:	7.42742784,
                                     14:	7.420178035,
                                     15:	7.077290784,
                                     16:	5.99361984,
                                     17:	4.036273408,
                                     18:	1.462618829,
                                     19:	0,
                                     20:	0,
                                     21:	0,
                                     22:	0,
                                     23:	0} 
       
    scenario_24Ts['Price_Forecast']={0 :  34.61,
                                    1 :  33.28,
                                    2 :  33.03,
                                    3 :  32.93,
                                    4 :  31.96,
                                    5 :  33.67,
                                    6 :  40.45,
                                    7 :  47.16,
                                    8 :  47.68,
                                    9 :  46.23,
                                    10:  43.01,
                                    11:  39.86,
                                    12:  37.64,
                                    13:  37.14,
                                    14:  39.11,
                                    15:  41.91,
                                    16:  44.11,
                                    17:  48.02,
                                    18:  51.65,
                                    19:  48.73,
                                    20:  43.56,
                                    21:  38.31,
                                    22:  37.66,
                                    23:  36.31}  
    
    #Constructing an instance of optimzation model
    ess_soc_domain=[20,30,40,50,60,70,80,90]   
    decision_domain=list(range(-60,70,10))
    dynprog_opt3=DynamicMaximizePV(scenario_24Ts,ess_soc_domain,decision_domain,opt3)
    
    start_time=time.time()
    dynprog_opt3.calculateOptimalTrajectory(40)    
    end_time=time.time()
    print("Computation time:",end_time-start_time,"seconds")

    with open('dynamic_MaximizePV.csv','w') as file:
        for ts in range(dynprog_opt3.T):
            file.write(str(dynprog_opt3.P_PV[ts]))
            file.write(",")
            file.write(str(dynprog_opt3.P_ESS[ts]))
            file.write(",")
            file.write(str(dynprog_opt3.P_Grid[ts]))
            file.write('\n')

