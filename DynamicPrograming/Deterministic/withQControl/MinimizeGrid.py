# -*- coding: utf-8 -*-
"""
Created on Mon Apr 30 15:41:00 2018

@author: guemruekcue
"""

from pyomo.environ import SolverFactory
from pyomo.core import *
from itertools import product

class DynamicMinimizeGrid():
    
    def __init__(self,scenarioParameters,ess_soc_domain,solver):
        """
        soc_disretization:  Defines the number of states
            e.g. ess_soc_domain=[30,40,50,60,70]

        """
        self.solver=solver
        self.objective=0
        
        # Time parameters
        self.T=scenarioParameters.T  #Total number of time steps: Optimization horizon
        self.dT=24*60*60/self.T      #Size of one time step: in seconds
        
        #Time invariant parameters
        self.PV_Inv_Max_Power       =scenarioParameters.PV_Inv_Max_Power
        self.P_Grid_Max_Export_Power=scenarioParameters.P_Grid_Max_Export_Power
        self.ESS_Min_SoC            =scenarioParameters.ESS_Min_SoC
        self.ESS_Max_SoC            =scenarioParameters.ESS_Max_SoC
        self.ESS_Capacity           =scenarioParameters.ESS_Capacity
        self.ESS_Max_Charge_Power   =scenarioParameters.ESS_Max_Charge_Power
        self.ESS_Max_Discharge_Power=scenarioParameters.ESS_Max_Discharge_Power
        
        #Forecasts
        self.P_Load_Forecast =scenarioParameters.P_Load_Forecast
        self.Q_Load_Forecast =scenarioParameters.Q_Load_Forecast
        self.P_PV_Forecast   =scenarioParameters.P_PV_Forecast
        self.Price_Forecast  =scenarioParameters.Price_Forecast
            
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
            self.Decision[t,s]={'P_PV':None,'Q_PV':None,'P_Grid':None,'Q_Grid':None,'ESS':None,'FinalSoC':None}
        
        #No inherent value of end state cases
        for s in self.stateIndexSet:
            self.Value[self.T,s]=0
        
        #Narrowing down the solution space by removing the infeasible range of final states
        self.feasibleSoCRange=dict.fromkeys(self.stateIndexSet)        
        for iniSoC in self.feasibleSoCRange.keys():
            
            max_Final_SoC=iniSoC+self.ESS_Max_Charge_Power/self.ESS_Capacity*100 
            min_Final_SoC=iniSoC-self.ESS_Max_Discharge_Power/self.ESS_Capacity*100
        
            feasibleRange=list(filter(lambda x: max_Final_SoC>=x >=min_Final_SoC, self.stateIndexSet))
            self.feasibleSoCRange[iniSoC]=feasibleRange
    
    def optimaldecisioncalculator(self,timestep,initialsoc):
        """
        Solves the optimization problem for a particular initial state at the time step
        """
        model = ConcreteModel()
        model.states=Set(initialize=self.feasibleSoCRange[initialsoc])  

        finalsocdict={}
        for state in self.feasibleSoCRange[initialsoc]:
            finalsocdict[state]=state
    
        model.finalsoc=Param(model.states,initialize=finalsocdict)
        
        model.whichfinalstate=Var(model.states,within=Binary)
   
        model.P_PV=Var(bounds=(0,self.P_PV_Forecast[timestep]))
        model.Q_PV=Var(bounds=(0,self.P_PV_Forecast[timestep]))
        model.P_ESS=Var(bounds=(-self.ESS_Max_Charge_Power,self.ESS_Max_Discharge_Power))
        model.P_GRID=Var(bounds=(-self.P_Grid_Max_Export_Power,10000))   
        model.Q_GRID=Var(bounds=(-self.P_Grid_Max_Export_Power,10000))

        def p_demandmeeting(model):
            return self.P_Load_Forecast[timestep]==model.P_PV+model.P_ESS+model.P_GRID
        model.const_p_demand=Constraint(rule=p_demandmeeting)

        def q_demandmeeting(model):
            return self.Q_Load_Forecast[timestep]==model.Q_PV+model.Q_GRID
        model.const_q_demand=Constraint(rule=q_demandmeeting)

        def pv_const(model):
            return self.P_PV_Forecast[timestep]==model.P_PV*model.P_PV+model.Q_PV*model.Q_PV
        model.const_pv_gen=Constraint(rule=pv_const)
        
        def delta_soc(model):
            return sum(model.whichfinalstate[state]*model.finalsoc[state] for state in model.states)==initialsoc-model.P_ESS/self.ESS_Capacity*100
        model.const_soc=Constraint(rule=delta_soc)
        
        def combinatorics(model):
            return sum(model.whichfinalstate[state] for state in model.states)==1
        model.const_com=Constraint(rule=combinatorics)

        def objrule0(model):
            return model.P_GRID*model.P_GRID+model.Q_GRID*model.Q_GRID+sum(model.whichfinalstate[state]*self.Value[timestep+1,state] for state in model.states)        
        def objrule1(model):
            return model.P_PV*model.P_PV+model.Q_PV*model.Q_PV+sum(model.whichfinalstate[state]*self.Value[timestep+1,state] for state in model.states)
        def objrule2(model):
            return self.Price_Forecast[timestep]*model.P_GRID+sum(model.whichfinalstate[state]*self.Value[timestep+1,state] for state in model.states)
        
        if self.objective==0:
            model.obj=Objective(rule=objrule0,sense=minimize)
        elif self.objective==1:
            model.obj=Objective(rule=objrule1,sense=maximize)        
        elif self.objective==2:
            model.obj=Objective(rule=objrule2,sense=minimize)  
        
        self.solver.solve(model)
        
        P_PV=model.P_PV()
        Q_PV=model.Q_PV()
        P_ESS=model.P_ESS()
        P_GRID=model.P_GRID()
        Q_GRID=model.Q_GRID()
            
        finalsoc=sum(model.whichfinalstate[state]()*model.finalsoc[state] for state in model.states)
        V=model.obj()
                   
        return P_PV,Q_PV,P_ESS,P_GRID,Q_GRID,V,finalsoc       
    
    def findstateoptimals(self,timestep):
        """
        Solves the optimizaton problem for every initial states at the time step
        """
        print("Time step",timestep)
        for ini_soc in self.stateIndexSet:
            results=self.optimaldecisioncalculator(timestep,ini_soc)
            
            self.Decision[timestep,ini_soc]['P_PV']  =results[0]
            self.Decision[timestep,ini_soc]['Q_PV']  =results[1]
            self.Decision[timestep,ini_soc]['ESS'] =results[2]
            self.Decision[timestep,ini_soc]['P_Grid']=results[3]
            self.Decision[timestep,ini_soc]['Q_Grid']=results[4]
            self.Decision[timestep,ini_soc]['FinalSoC']=results[6]
        
            self.Value[timestep,ini_soc]=results[5]
            
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
            self.P_ESS.append(self.Decision[t,initialstate]['ESS'])
            self.P_Grid.append(self.Decision[t,initialstate]['P_Grid'])
            self.Q_Grid.append(self.Decision[t,initialstate]['Q_Grid'])
            finalstate=self.Decision[t,initialstate]['FinalSoC']
         

if __name__=="__main__":
    
    opt1=SolverFactory('glpk',executable="C:/Users/guemruekcue/Anaconda3/pkgs/glpk-4.63-vc14_0/Library/bin/glpsol")
    opt2= SolverFactory("ipopt", executable="C:/Users/guemruekcue/Anaconda3/pkgs/ipopt-3.11.1-2/Library/bin/ipopt")
    opt3= SolverFactory("bonmin", executable="C:/cygwin/home/bonmin/Bonmin-1.8.6/build/bin/bonmin")
  
    import time
    from Deterministic.withQControl.ScenarioClass import scenario_24Ts
    
    #Constructing an instance of optimzation model
    ess_soc_domain=[20,30,40,50,60,70,80,90]   
    dynprog_opt3=DynamicMinimizeGrid(scenario_24Ts,ess_soc_domain,opt3)
    
    start_time=time.time()
    dynprog_opt3.calculateOptimalTrajectory(40)    
    end_time=time.time()
    print("Computation time:",end_time-start_time,"seconds")

    with open('dynamic2_MinimizeGrid.csv','w') as file:
        for ts in range(dynprog_opt3.T):
            file.write(str(dynprog_opt3.P_PV[ts]))
            file.write(",")
            file.write(str(dynprog_opt3.P_ESS[ts]))
            file.write(",")
            file.write(str(dynprog_opt3.P_Grid[ts]))
            file.write(",")
            file.write(str(dynprog_opt3.Q_PV[ts]))
            file.write(",")
            file.write(str(dynprog_opt3.Q_Grid[ts]))
            file.write('\n')

