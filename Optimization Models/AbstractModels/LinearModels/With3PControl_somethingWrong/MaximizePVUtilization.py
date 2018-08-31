# -*- coding: utf-8 -*-
"""
Created on Wed Apr 11 16:35:50 2018

@author: guemruekcue
"""


from pyomo.environ import SolverFactory
from pyomo.opt import SolverStatus, TerminationCondition
from pyomo.core import *
import pandas as pd

class MaximizePVUtilization():
    """
    Class for the abstract optimization model
    Objective: Maximization of utilized PV potential (minimization of non utilized PV potential)
    Solvers  : "bonmin","ipopt"
    """
    
    def __init__(self):
    
        model = AbstractModel()
    
        model.T=Set()                                                   #Index Set for time steps of optimization horizon
        model.T_SoC=Set()                                               #SoC of the ESSs at the end of optimization horizon are also taken into account
        
        
        ##################################       PARAMETERS            #################################
        ################################################################################################                                               
        
        model.dT=Param(within=PositiveIntegers)                         #Number of seconds in one time step
        
        #model.Price_Forecast=Param(model.T)                             #Electric price forecast     
        model.P_PV=Param(model.T,within=NonNegativeReals)      #PV PMPP forecast    
        
        model.ESS_Min_SoC=Param(within=PositiveReals)           #Minimum SoC of ESSs
        model.ESS_Max_SoC=Param(within=PositiveReals)           #Maximum SoC of ESSs
        model.ESS_SoC_Value=Param(within=PositiveReals)         #SoC value of ESSs at the begining of optimization horizon
        model.ESS_Capacity=Param(within=PositiveReals)          #Storage Capacity of ESSs
        model.ESS_Max_Charge_Power=Param(within=PositiveReals)  #Max Charge Power of ESSs
        model.ESS_Max_Discharge_Power=Param(within=PositiveReals)#Max Discharge Power of ESSs
        model.ESS_Charging_Eff=Param(within=PositiveReals)      #Charging efficiency of ESSs
        model.ESS_Discharging_Eff=Param(within=PositiveReals)   #Discharging efficiency of ESSs
        
        model.P_Grid_Max_Export_Power=Param(within=NonNegativeReals)    #Max active power export
        model.Q_Grid_Max_Export_Power=Param(within=NonNegativeReals)    #Max reactive power export
        
        model.PV_Inv_Max_Power=Param(within=PositiveReals)              #PV inverter capacity
           
    
        #Active and reactive power demand at each phases
        model.P_Load_R=Param(model.T,within=NonNegativeReals)           #Active power demand of R phase
        model.P_Load_S=Param(model.T,within=NonNegativeReals)           #Active power demand of S phase
        model.P_Load_T=Param(model.T,within=NonNegativeReals)           #Active power demand of T phase      
        model.Q_Load_R=Param(model.T,within=Reals)                      #Reactive power demand of R phase
        model.Q_Load_S=Param(model.T,within=Reals)                      #Reactive power demand of S phase
        model.Q_Load_T=Param(model.T,within=Reals)                      #Reactive power demand of T phase
          
        ################################################################################################
        
        ##################################       VARIABLES             #################################
        ################################################################################################
        
    
        model.P_Grid_R_Output=Var(model.T,within=Reals)                #Active power exchange with grid at R phase 
        model.P_Grid_S_Output=Var(model.T,within=Reals)                #Active power exchange with grid at S phase
        model.P_Grid_T_Output=Var(model.T,within=Reals)                #Active power exchange with grid at S phase
        model.P_Grid_Output=Var(model.T,within=Reals)
        model.Q_Grid_Output_R=Var(model.T,within=Reals)                #Reactive power exchange with grid at R phase
        model.Q_Grid_Output_S=Var(model.T,within=Reals)                #Reactive power exchange with grid at S phase
        model.Q_Grid_Output_T=Var(model.T,within=Reals)                #Reactive power exchange with grid at T phase
        model.Q_Grid_Output=Var(model.T,within=Reals)
    
        model.P_ER_R=Var(model.T,within=Reals)         #Active power output of ER's R phase
        model.P_ER_S=Var(model.T,within=Reals)         #Active power output of ER's S phase
        model.P_ER_T=Var(model.T,within=Reals)         #Active power output of ER's T phase
        model.P_ER=Var(model.T,within=Reals)            #Total active power output of ER
        
        model.Q_ER_R=Var(model.T,within=Reals)         #Reactive power output of ER's R phase
        model.Q_ER_S=Var(model.T,within=Reals)         #Reactive power output of ER's S phase
        model.Q_ER_T=Var(model.T,within=Reals)         #Reactive power output of ER's T phase
        model.Q_ER=Var(model.T,within=Reals)            #Total reactive power output of ER
            
        model.P_PV_Output=Var(model.T,within=NonNegativeReals,bounds=(0,model.PV_Inv_Max_Power)) #Power output of PV inverter
        model.P_ESS_Output = Var(model.T,within=Reals,bounds=(-model.ESS_Max_Charge_Power, model.ESS_Max_Discharge_Power))        
        model.SoC_ESS=Var(model.T_SoC,within=NonNegativeReals,bounds=(model.ESS_Min_SoC,model.ESS_Max_SoC))    
        ################################################################################################
                       
        ###########################################################################
        #######                         CONSTRAINTS                         #######

        #P load constraints
        def con_rule_Pdem_R(model,t):
            return model.P_Load_R[t]==model.P_ER_R[t]+ model.P_Grid_R_Output[t]
        def con_rule_Pdem_S(model,t):
            return model.P_Load_S[t]==model.P_ER_S[t]+ model.P_Grid_S_Output[t] 
        def con_rule_Pdem_T(model,t):
            return model.P_Load_T[t]==model.P_ER_T[t]+ model.P_Grid_T_Output[t]     
        
        #Q load constraints
        def con_rule_Qdem_R(model,t):
            return model.Q_Load_R[t]==model.Q_ER_R[t]+ model.Q_Grid_Output_R[t]  
        def con_rule_Qdem_S(model,t):
            return model.Q_Load_S[t]==model.Q_ER_S[t]+ model.Q_Grid_Output_S[t] 
        def con_rule_Qdem_T(model,t):
            return model.Q_Load_T[t]==model.Q_ER_T[t]+ model.Q_Grid_Output_T[t] 
        
        #PV constraints
        def con_rule_pv_potential(model,t):
            return model.P_PV_Output[t]<= model.P_PV[t]
                
        #Import/Export constraints
        def con_rule_grid_P(model,t):
            return model.P_Grid_Output[t]==model.P_Grid_R_Output[t]+model.P_Grid_S_Output[t]+model.P_Grid_T_Output[t]
        def con_rule_grid_P_inv(model,t):
            return model.P_Grid_Output[t]>=-model.P_Grid_Max_Export_Power
        def con_rule_grid_Q(model,t):
            return model.Q_Grid_Output[t]==model.Q_Grid_Output_R[t]+model.Q_Grid_Output_S[t]+model.Q_Grid_Output_T[t]
        def con_rule_grid_Q_inv(model,t):
            return model.Q_Grid_Output[t]>=-model.Q_Grid_Max_Export_Power

  
        def con_rule_socBalance(model,t):
            return model.SoC_ESS[t+1]==model.SoC_ESS[t] - model.P_ESS_Output[t]*model.dT/model.ESS_Capacity/3600    
        def con_rule_iniSoC(model):
            return model.SoC_ESS[0]==model.ESS_SoC_Value
        
        #Energy router (virtual) constraints
        def energyrouter_p(model,t):
            return model.P_ER[t]==model.P_ER_R[t]+model.P_ER_S[t]+model.P_ER_T[t]
        def energyrouter_q(model,t):
            return model.Q_ER[t]==model.Q_ER_R[t]+model.Q_ER_S[t]+model.Q_ER_T[t]        
        def energyrouter_io(model,t):
            er_feedin=(model.P_PV_Output[t]+model.P_ESS_Output[t])*(model.P_PV_Output[t]+model.P_ESS_Output[t])
            return er_feedin*er_feedin==model.P_ER[t]*model.P_ER[t]+model.Q_ER[t]*model.Q_ER[t]
       
        model.con_Pdem_R=Constraint(model.T,rule=con_rule_Pdem_R)
        model.con_Pdem_S=Constraint(model.T,rule=con_rule_Pdem_S)
        model.con_Pdem_T=Constraint(model.T,rule=con_rule_Pdem_T)  
        model.con_Qdem_R=Constraint(model.T,rule=con_rule_Qdem_R)
        model.con_Qdem_S=Constraint(model.T,rule=con_rule_Qdem_S)
        model.con_Qdem_T=Constraint(model.T,rule=con_rule_Qdem_T)
        
        model.con_pv_pmax=Constraint(model.T,rule=con_rule_pv_potential)
        
        model.con_grid_P=Constraint(model.T,rule=con_rule_grid_P)
        model.con_grid_inv_P=Constraint(model.T,rule=con_rule_grid_P_inv)
        model.con_grid_Q=Constraint(model.T,rule=con_rule_grid_Q)
        model.con_grid_inv_Q=Constraint(model.T,rule=con_rule_grid_Q_inv)
        
        model.con_ess_soc=Constraint(model.T,rule=con_rule_socBalance)
        model.con_ess_Inisoc=Constraint(rule=con_rule_iniSoC)
        
        model.con_er_p =Constraint(model.T,rule=energyrouter_p)
        model.con_er_q =Constraint(model.T,rule=energyrouter_q)
        model.con_er_io=Constraint(model.T,rule=energyrouter_io)
        
        ###########################################################################
        #######                         OBJECTIVE                           #######
        ###########################################################################
        def obj_rule(model):  
            return sum(model.P_PV[t]-model.P_PV_Output[t] for t in model.T)
        model.obj=Objective(rule=obj_rule, sense = minimize)


        #model.pprint()
        self.model=model
    

def calculateOptimalTrajectory(abstractmodel,data_file,solver):
    """
    Solves the optimization problem for given data_file
    """
    instance=abstractmodel.create_instance(data_file)

    try:
        results=solver.solve(instance)
        if (results.solver.status == SolverStatus.ok):
            term_status=results.solver.termination_condition.key
            P_ESS=instance.P_ESS_Output[0]()
        else:
            term_status=results.solver.termination_condition.key
            P_ESS=None  
            
    except:
        term_status="Could not execute the optimization"
        P_ESS=None 
    
    print(term_status)
    
    P_ER_R=[]
    P_ER_S=[]
    P_ER_T=[]
    Q_ER_R=[]
    Q_ER_S=[]
    Q_ER_T=[]
    P_GRID_R=[]
    P_GRID_S=[]
    P_GRID_T=[]
    Q_GRID_R=[]
    Q_GRID_S=[]
    Q_GRID_T=[]
    P_Load_R=[]
    P_Load_S=[]
    P_Load_T=[]
    Q_Load_R=[]
    Q_Load_S=[]
    Q_Load_T=[]
    
    Forecast_PV=[]
    P_PV=[]
    
    P_ESS=[]
    SOC=[]
    
    P_GRID=[]
    Q_GRID=[]
      
    for t in instance.T:
       
        P_ER_R.append(instance.P_ER_R[t]())
        P_Load_R.append(instance.P_Load_R[t])
        P_GRID_R.append(instance.P_Grid_R_Output[t]())
        Q_ER_R.append(instance.Q_ER_R[t]())
        Q_Load_R.append(instance.Q_Load_R[t])
        Q_GRID_R.append(instance.Q_Grid_Output_R[t]())
        
        P_ER_S.append(instance.P_ER_S[t]())
        P_Load_S.append(instance.P_Load_S[t])
        P_GRID_S.append(instance.P_Grid_S_Output[t]())
        Q_ER_S.append(instance.Q_ER_S[t]())
        Q_Load_S.append(instance.Q_Load_S[t])
        Q_GRID_S.append(instance.Q_Grid_Output_S[t]())
        
        P_ER_T.append(instance.P_ER_T[t]())
        P_Load_T.append(instance.P_Load_T[t])
        P_GRID_T.append(instance.P_Grid_T_Output[t]())
        Q_ER_T.append(instance.Q_ER_T[t]())
        Q_Load_T.append(instance.Q_Load_T[t])
        Q_GRID_T.append(instance.Q_Grid_Output_T[t]())
                      
        Forecast_PV.append(instance.P_PV[t])
        P_PV.append(instance.P_PV_Output[t]())
        P_ESS.append(instance.P_ESS_Output[t]())
        SOC.append(instance.SoC_ESS[t]())
        
        P_GRID.append(instance.P_Grid_Output[t]())
        Q_GRID.append(instance.Q_Grid_Output[t]())
        
        
        
        
    summaryDict_R={'PLoad':P_Load_R,'P_ER':P_ER_R,'P_Grid':P_GRID_R,
                   'QLoad':Q_Load_R,'Q_ER':Q_ER_R,'Q_Grid':Q_GRID_R,}    
    summaryDict_PV={'Forecast':Forecast_PV,'P':P_PV}
    summaryDict_ESS={'P':P_ESS,'SoC':SOC}
    summaryDict_GRID={'P':P_GRID,'P_R':P_GRID_R,'P_S':P_GRID_S,'P_T':P_GRID_T,
                      'Q':Q_GRID,'Q_R':Q_GRID_R,'Q_S':Q_GRID_S,'Q_T':Q_GRID_T}
    
    summary_R=pd.DataFrame(data=summaryDict_R)
    summary_PV=pd.DataFrame(data=summaryDict_PV)
    summary_ESS=pd.DataFrame(data=summaryDict_ESS)
    summary_GRID=pd.DataFrame(data=summaryDict_GRID)
    
    return summary_R,summary_PV,summary_ESS,summary_GRID
        
if __name__=="__main__":
    
    #Building the optimization model
    optimizationmodel=MaximizePVUtilization()
    opt1=SolverFactory('glpk',executable="C:/Users/guemruekcue/Anaconda3/pkgs/glpk-4.63-vc14_0/Library/bin/glpsol")
    opt2= SolverFactory("ipopt", executable="C:/Users/guemruekcue/Anaconda3/pkgs/ipopt-3.11.1-2/Library/bin/ipopt")
    opt3= SolverFactory("bonmin", executable="C:/cygwin/home/bonmin/Bonmin-1.8.6/build/bin/bonmin")
    
    #opt2.options["max_iter"]=5000
    
    
    
    #Loading the data file
    import os
    import time
    project_dir=os.path.dirname(__file__)
    data_file=project_dir+'/Scenario_10.dat'
        
    #Constructing an instance of optimzation model
    start_time=time.time()
    summaryR_phase,summary_PV,summary_ESS,summary_GRID=calculateOptimalTrajectory(optimizationmodel.model,data_file,opt2)
    end_time=time.time()
    print("Computation time:",end_time-start_time,"seconds")
    
    results_NA=[summaryR_phase,summary_PV,summary_ESS,summary_GRID]
        

    