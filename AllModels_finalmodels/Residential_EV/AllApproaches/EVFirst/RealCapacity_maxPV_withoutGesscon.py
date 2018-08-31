# -*- coding: utf-8 -*-
"""
Created on Tue Jul 31 11:09:23 2018

@author: guemruekcue
"""

from itertools import product
import time
import numpy as np
import os
import pandas as pd
from itertools import chain
from functions import import_statistics
from pyomo.environ import SolverFactory
from pyomo.core import *


class MaximizePV():
    
    def __init__(self,timeresolution,horizon,solver,
                 ev_capacity,ev_soc_domain,ev_decision_domain,unitconsumption,
                 markovModel,ev_minSoC,dropPenalty,
                 forecast_load,forecast_pv,forecast_price,
                 ess_max_charge,ess_max_discharge,grid_max_export,pv_max_generation,
                 ess_capacity,ess_minSoC,ess_maxSoC,
                 ess_iniSoC,ev_iniSoC,ev_iniPos):
        """
        param timeresolution: integer
            Number of seconds in one time step
        param horizon: integer 
            Total number of time steps= Optimization horizon
        param solver: SolverFactory
            Optimization solver: Glpk or Bonmin
        param ev_capacity   : float 
            Capacity of EV Battery Capacity: kWh        
        param unitconsumption: Integer
            Assumption on how much capacity of EV battery will be spent if one car drives during one hour: %
        param markovModel: Dictionary
            Markov transition matrices
        param ev_decision_domain : range
            Defines the possible decisions for EV charging : % change in SoC level of EV
        >>>Example
            ev_decision_domain=[0,5,10]
            >>> Charger can charge 5% or 10% of EV during time step
        param ev_soc_domain : range
            For resolution of states, defines the possible SoC levels for EV : %            
        >>>Example
            ev_soc_domain=[0,5,15,....,100]
            >>> DP states are combination of position and ev_soc 
            >>> i.e. at ts=12 having away state and ev_soc=40%
        param markovModel: dictionary
            Inhomogenous markov model for state transitions between home-away states
        param ev_minSoC: float
            Allowed minimum SoC of EV battery
        param dropPenalty: float
            Penalty rate for dropping below allowed min EV SoC: 1/kWh
        param local_em_weight: float
            Penalty rate for local EM target (Minimize curtailed PV): 1/kWh
        param global_em_weight: float 
            Penalty rate for global EM target (Deviation from DSO command): 1/kWh
        param forecast_load: dict 
            Active power forecast for upcoming prediction horizon (entries:kW)
        param forecast_pv: dict
            Maximum power generation acc. weather prediction for upcoming prediction horizon (entries:kW)
        param forecast_price: dict
            Price forecast for upcoming prediction horizon (entries:EUR/MWh)
        param dso_command: dict
            DSO command for ESS operation for upcoming prediction horizon (entries kW)
        param ess_max_charge:    float
            ESS maximum charge power: kW
        param ess_max_discharge: float
            ESS maximum discharge power: kW
        param grid_max_export:   float
            Maximum export(feed-in) to grid :kW
        param pv_max_generation: float 
            PV inverter capacity: kW
        param ess_capacity: kWh
            ESS energy capacity
        param ess_minSoC: float
            Minimum allowed SoC for ESS 
        param ess_maxSoC: float
            Maximum allowed SoC for ESS
        param ess_iniSoC: float
            Initial SoC of ESS
        param ev_iniSoC: float
            Initial SoC of EV battery
        param ev_iniPos: integer 
            Initial position of EV
            1: Home
            0: Away
        """
        self.dT=timeresolution  #in seconds
        self.T=horizon
        self.solver=solver       
        
        self.ev_capacity=ev_capacity*3600                               #EV battery capacity in kWs
        self.consumptionAssumption=int(unitconsumption/3600*self.dT)    #How much SoC of EV battery is assumed to be consumed when one car drives for one time step length
        self.ev_minSoC=int(ev_minSoC*100)       #Allowed minimum EV battery SoC %
        self.unitDropPenalty=dropPenalty/3600   #Penalty for compensation of 1kW-sec in case dropping below allowed minimum EV SoC         
        self.max_car_atHome=1
                      
        self.markovModel=markovModel           #Inhomogenous markov model: dict        
        self.max_car_atHome=1                  #Max number of cars at home one time step
        
        #Decision domain for EV Battery charging
        self.ev_decision_domain=ev_decision_domain
        
        #States
        self.ev_soc_states=ev_soc_domain
        self.ev_pos_states=range(2)
        
        #Initialize empty lookup tables
        keylistforValue    =[(t,s_ev,s_pos) for t,s_ev,s_pos in product(list(range(0,self.T+1)),self.ev_soc_states,self.ev_pos_states)]
        keylistforDecisions=[(t,s_ev,s_pos) for t,s_ev,s_pos in product(list(range(0,self.T))  ,self.ev_soc_states,self.ev_pos_states)]
        
        self.Value   =dict.fromkeys(keylistforValue)
        self.Decision=dict.fromkeys(keylistforDecisions)
    
        for t,s_ev,s_pos in product(list(range(0,self.T))  ,self.ev_soc_states,self.ev_pos_states):
            self.Decision[t,s_ev,s_pos]={'EV':None}
            self.Value[t,s_ev,s_pos]=None

        for s_ev,s_pos in product(self.ev_soc_states,self.ev_pos_states):
            self.Value[self.T,s_ev,s_pos]=1.0
            
            
        #Parameters for ESS optimization       
        self.P_Load_Forecast=forecast_load
        self.P_PV_Forecast=forecast_pv
        self.Price_Forecast=forecast_price
        
        self.ESS_Max_Charge=ess_max_charge
        self.ESS_Max_Discharge=ess_max_discharge
        self.Max_Export=grid_max_export
        self.Max_PVGen=pv_max_generation
        
        self.ESS_Capacity=ess_capacity*3600     #ESS capacity in kWs
        self.ESS_Min_SoC=ess_minSoC
        self.ESS_Max_SoC=ess_maxSoC
        
        self.ESS_Ini_SoC=ess_iniSoC
        self.EV_Ini_SoC=ev_iniSoC
        self.EV_Ini_POS=ev_iniPos
        
    def optimaldecisioncalculator(self,timestep,ini_ev_soc,ini_pos):
        """
        Solves the optimization problem for a particular initial state (ev_soc and position) at the time step
        """
        #Solve the optimization problem only if the car is at home
        if ini_pos==1:
       
            model = ConcreteModel()
            
            feasible_Pev=[]            #Feasible charge powers to VAC under the given conditions
            parameters_Pev={}                      
            for p_EV in self.ev_decision_domain:         #When decided charging with P_ESS   
                if p_EV+ini_ev_soc<=max(self.ev_soc_states): #if the final vac_SoC is below the upper domain limit
                    feasible_Pev.append(p_EV)                  #then append P_VAC as one of the feasible vac decisions
                    parameters_Pev[p_EV]=p_EV      
            model.decision_ev=Set(initialize=feasible_Pev) 
            
            #Combined decision        
            model.Decision=Var(model.decision_ev,within=Binary)
            model.P_EV=Var(within=NonNegativeReals)
            
            def combinatorics(model):
                #only one of the feasible decisions can be taken
                return 1==sum(model.Decision[p] for p in model.decision_ev)
            model.const_integer=Constraint(rule=combinatorics)
            
            def chargepower(model):
                if ini_pos==1:
                    return model.P_EV==sum(model.Decision[p]*p for p in model.decision_ev)
                else:
                    return model.P_EV==0.0
            model.const_chargepw=Constraint(rule=chargepower)
    
         
            def objrule1(model):
                future_value=0
    
                for p_ev in model.decision_ev:   #If EV is charged with one of the feasible decision 'p_ev'
                 
                    fin_ev_soc=p_ev+ini_ev_soc   #Transition between EV SOC states are deterministic when the car is at home now
                    
                    valueOf_home=self.Value[timestep+1,fin_ev_soc,1]    #Value of having fin_ev_soc and home position in next time interval    
                    valueOf_away=self.Value[timestep+1,fin_ev_soc,0]    #Value of having fin_ev_soc and away position in next time interval
                    
                    #Expected future value= probability of swiching to home state*value of having home state
                    #                       +probability of swiching to away state*value of having away state
                    expected_future_value=self.markovModel[timestep,1,1]*valueOf_home+self.markovModel[timestep,1,0]*valueOf_away
    
                    future_value+=model.Decision[p_ev]*expected_future_value    #Adding the expected_future cost of taking 'p_ev' decision when initial condition is 'ini_ev_soc' and home state                                      
            
                return future_value #No immediate cost of decision

            model.obj=Objective(rule=objrule1) 
            self.solver.solve(model)       
            P_EV=model.P_EV()
            V=model.obj()
                
        #def objrule0(model):
        elif ini_pos==0:
            future_value=0                
            expected_future_value=0    #Expected value of taking decision p_ev
                
            final_ev_soc=ini_ev_soc-self.max_car_atHome*self.consumptionAssumption #The car reaches to 'final_ev' by driving during one time interval
            fin_ev_soc=final_ev_soc if final_ev_soc>=self.ev_minSoC else self.ev_minSoC
            
            #Extra penalty for dropping below predefined ev_minSoC limit
            #The case after dropping below ev_minSoC will be integrated as if they dropped to ev_minSoC%
            penalty_for_negative_soc_home=(self.ev_minSoC-final_ev_soc)/100*self.unitDropPenalty*self.ev_capacity+self.Value[timestep+1,int(self.ev_minSoC),1] if final_ev_soc<self.ev_minSoC else 0
            penalty_for_negative_soc_away=(self.ev_minSoC-final_ev_soc)/100*self.unitDropPenalty*self.ev_capacity+self.Value[timestep+1,int(self.ev_minSoC),0] if final_ev_soc<self.ev_minSoC else 0
            
            #value of reaching 'fin_ev_soc' at next time step
            valueOf_home=self.Value[timestep+1,fin_ev_soc,1]+penalty_for_negative_soc_home    #Value of having fin_ev_soc and home position in next time interval    
            valueOf_away=self.Value[timestep+1,fin_ev_soc,0]+penalty_for_negative_soc_away    #Value of having fin_ev_soc and away position in next time interval               
                
            expected_future_value= self.markovModel[timestep,0,1]*valueOf_home+self.markovModel[timestep,0,0]*valueOf_away               
        #return expected_future_value #No immediate cost of decision
            P_EV=0.0
            V=expected_future_value
               
        return P_EV,V                     

    def solve_dynamicprogram(self):  #Whole map calculation for dynamic programming
        """
        Calculates the optimal values of whole map
        """
        start=time.time()
        for timestep in reversed(range(0,self.T)):
            #Solves the optimizaton problem for every initial states at the time step
            for ini_ev_soc,position in product(self.ev_soc_states,self.ev_pos_states):
                results=self.optimaldecisioncalculator(timestep,ini_ev_soc,position)
                
                self.Decision[timestep,ini_ev_soc,position]['EV']=results[0]/100*self.ev_capacity/self.dT
                self.Value[timestep,ini_ev_soc,position]=results[1]
        end=time.time()
        print("Dynamic programming execution:",end-start)

    def nexthour_expectation(self,timestep,iniSoC,iniPos):
        """
        iniSoC: initial SoC  0< integer <100
        iniPos: initial Position integer in {0,1}
        """
        
        #Transition probabilities between states
        p_00=self.markovModel[timestep+1,0,0]     #Probability of switching from away to away state
        p_01=self.markovModel[timestep+1,0,1]
        p_10=self.markovModel[timestep+1,1,0]
        p_11=self.markovModel[timestep+1,1,1]
      
        if iniPos==0:
            fin_SoC=iniSoC-self.consumptionAssumption
            finSoC=min(self.ev_soc_states, key=lambda x:abs(x-fin_SoC))           
            val_from_pmf=np.random.choice(2,1,p=[p_00,p_01])    #Sampling from markov chain to estimate next hour's position
            finPos=val_from_pmf[0]                
        if iniPos==1:
            fin_SoC=iniSoC+self.Decision[timestep,iniSoC,1]['EV']*self.dT/self.ev_capacity*100
            finSoC=min(self.ev_soc_states, key=lambda x:abs(x-fin_SoC))           
            val_from_pmf=np.random.choice(2,1,p=[p_10,p_11])
            finPos=val_from_pmf[0]

        return finSoC,finPos   
                    
    def estimate_ev_charging(self,startSoC,startPos):
        """
        calculates expected trajectories for EV position, EV SoC, EV charging profile
        """
        starttraj=time.time()
             
        position_trajectory={0:startPos}
        soc_trajectory     ={0:startSoC}
        self.solve_dynamicprogram()
        chargePow_trajectory={0:self.Decision[0,startSoC,startPos]['EV']}                           
        
        for t in range(1,self.T):            
            SoC_at_t,Pos_at_t=self.nexthour_expectation(t-1,soc_trajectory[t-1],position_trajectory[t-1])           
            position_trajectory[t]=Pos_at_t
            soc_trajectory[t]=SoC_at_t            
            chargePow_trajectory[t]=self.Decision[t,SoC_at_t,Pos_at_t]['EV']
        
        endtraj=time.time()       
        print("Complete trajectory calculated in:",endtraj-starttraj)
               
        self.results_EV_position_estimiation=position_trajectory
        self.results_EV_soc_estimation      =soc_trajectory
        self.results_EV_charging_estimation =chargePow_trajectory
        
        
    def optimize_full_EM(self):
        
        print("Optimizer started")
        ini_EV_pos=self.EV_Ini_POS
        ini_EV_soc=min(self.ev_soc_states, key=lambda x:abs(x-self.EV_Ini_SoC*100))
        self.estimate_ev_charging(ini_EV_soc,ini_EV_pos)
                     
        model = ConcreteModel()
        model.T=RangeSet(0,self.T-1)     #Index Set for time steps of optimization horizon
        model.T_SoC=RangeSet(0,self.T)   #SoC of the ESSs at the end of optimization horizon are also taken into account
        model.dT=Param(initialize=self.dT)                             #Number of seconds in one time step
        
        ##################################       PARAMETERS            #################################
        ################################################################################################                                                             
        model.P_EV_Forecast=Param(model.T,initialize=self.results_EV_charging_estimation)   #EV charge power forecast    
        model.P_Load_Forecast=Param(model.T,initialize=self.P_Load_Forecast)                #Active power demand forecast        
        model.P_PV_Forecast=Param(model.T,initialize=self.P_PV_Forecast)                    #PV PMPP forecast        
        model.Price_Forecast=Param(model.T,initialize=self.Price_Forecast)                  #Electricity price forecast
        
        model.ESS_Max_Charge_Power=Param(initialize=self.ESS_Max_Charge)        #Max Charge Power of ESSs
        model.ESS_Max_Discharge_Power=Param(initialize=self.ESS_Max_Discharge)  #Max Discharge Power of ESSs        
        model.P_Grid_Max_Export_Power=Param(initialize=self.Max_Export)         #Max active power export
        model.PV_Inv_Max_Power=Param(initialize=self.Max_PVGen)                 #PV inverter capacity
               
        model.ESS_Min_SoC=Param(initialize=self.ESS_Min_SoC)           #Minimum SoC of ESSs
        model.ESS_Max_SoC=Param(initialize=self.ESS_Max_SoC)           #Maximum SoC of ESSs
        model.ESS_SoC_Value=Param(initialize=self.ESS_Ini_SoC)         #SoC value of ESSs at the begining of optimization horizon
        model.ESS_Capacity=Param(initialize=self.ESS_Capacity)         #Storage Capacity of ESSs       
        ################################################################################################
        
        ##################################       VARIABLES             #################################
        ################################################################################################                    
        model.P_PV_Output=Var(model.T,within=NonNegativeReals,bounds=(0,model.PV_Inv_Max_Power))
        model.P_Grid_Output=Var(model.T,within=Reals,bounds=(-model.P_Grid_Max_Export_Power,100000)) 
        model.P_ESS_Output = Var(model.T,within=Reals,bounds=(-model.ESS_Max_Charge_Power, model.ESS_Max_Discharge_Power))
        model.SoC_ESS=Var(model.T_SoC,within=NonNegativeReals,bounds=(model.ESS_Min_SoC, model.ESS_Max_SoC))
        #model.Deviation=Var(model.T,within=Reals)
        ################################################################################################
                      
        ###########################################################################
        #######                         CONSTRAINTS                         #######
        #######                Rule1: P_power demand meeting                #######
        #######                Rule2: PV power limitation                   #######
        #######                Rule3: State of charge consistency           #######
        #######                Rule4: Initial State of charge               #######
        ###########################################################################
        def con_rule1(model,t):
            return model.P_Load_Forecast[t]+model.P_EV_Forecast[t]==model.P_PV_Output[t]+ model.P_Grid_Output[t] + model.P_ESS_Output[t]  
        def con_rule2(model,t):
            return 0<=model.P_PV_Output[t]<=model.P_PV_Forecast[t]
        def con_rule3(model,t):
            return model.SoC_ESS[t+1]==model.SoC_ESS[t] - model.P_ESS_Output[t]*model.dT/model.ESS_Capacity
        def con_rule4(model):
            return model.SoC_ESS[0]==model.ESS_SoC_Value
        #def con_rule5(model,t):
        #    return model.Deviation[t]==model.P_ESS_Output[t]-model.ESS_Command[t]
      
        model.con1=Constraint(model.T,rule=con_rule1)
        model.con2=Constraint(model.T,rule=con_rule2)
        model.con3=Constraint(model.T,rule=con_rule3)
        model.con4=Constraint(rule=con_rule4)
        
        ###########################################################################
        #######                         OBJECTIVE                           #######
        ###########################################################################
        def obj_rule(model):  
            return sum(model.P_PV_Forecast[t]-model.P_PV_Output[t] for t in model.T)
        model.obj=Objective(rule=obj_rule, sense = minimize)    
        
        results=self.solver.solve(model)

        optimal={}
        optimal["P_Grid"]=model.P_Grid_Output[0]()
        optimal["P_PV"]  =model.P_PV_Output[0]()
        optimal["P_ESS"] =model.P_ESS_Output[0]()
        optimal["P_EV"]  =-model.P_EV_Forecast[0]
        
        print("ESS operation optimized")
        
        return optimal
    
                
#%%
if __name__ == "__main__":
    EVFirst_dir=os.path.dirname(__file__)
    AllAproaches_dir=os.path.dirname(EVFirst_dir)
    Inputs_dir=os.path.join(AllAproaches_dir,'Inputs')
    Forecast_inp=Inputs_dir+'\Forecasts_60M.xlsx'
    Markov_inp=Inputs_dir+'\Markov_60M.csv'
    DSO_inp=Inputs_dir+'\GessCon_60M.xlsx'
    xl= pd.ExcelFile(Forecast_inp)
    xl_dso=pd.ExcelFile(DSO_inp)
    forecasts  = xl.parse("0")
    dso_commands = xl_dso.parse("0")
    
    
    #DP parameters
    timeresolution=3600
    horizon=24
    #theSolver= SolverFactory("ipopt", executable="C:/Users/guemruekcue/Anaconda3/pkgs/ipopt-3.11.1-2/Library/bin/ipopt")
    theSolver= SolverFactory("bonmin", executable="C:/cygwin/home/bonmin/Bonmin-1.8.6/build/bin/bonmin")
    ev_capacity=40
    evSoCdomain=range(0,105,5)
    evDecisionDomain=range(0,25,5)
    unitconsumption=10  #10% SoC per hour
    markovModel=import_statistics(Markov_inp,'00:00')
    ev_minSoC=0.2
    dropPenalty=1   #1/kWh
    
    
    #Local optimization parameter
    
    forecast_load=dict(enumerate(forecasts['Load'].values.tolist()))
    forecast_pv=dict(enumerate(forecasts['PV'].values.tolist()))
    forecast_price=dict(enumerate(forecasts['Price'].values.tolist()))
    ess_max_charge=0.62
    ess_max_discharge=0.62
    grid_max_export=10
    pv_max_generation=1.5
    ess_capacity=0.675
    ess_minSoC=0.2
    ess_maxSoC=1.0
    
    ess_iniSoC=0.4
    ev_iniSoC=0.2
    ev_iniPos=1
        
        
    EMOptimizer=MaximizePV(timeresolution,horizon,theSolver,
                                      ev_capacity,evSoCdomain,evDecisionDomain,unitconsumption,
                                      markovModel,ev_minSoC,dropPenalty,
                                      forecast_load,forecast_pv,forecast_price,
                                      ess_max_charge,ess_max_discharge,grid_max_export,pv_max_generation,
                                      ess_capacity,ess_minSoC,ess_maxSoC,
                                      ess_iniSoC,ev_iniSoC,ev_iniPos)
    #%%
    decisions=EMOptimizer.optimize_full_EM()


