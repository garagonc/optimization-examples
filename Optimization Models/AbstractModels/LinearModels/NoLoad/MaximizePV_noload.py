# -*- coding: utf-8 -*-
"""
Created on Thu Aug 30 17:21:46 2018

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
    
    def __init__(self,iniSoC):#,iniSoC,iniVal):
    
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
        model.ESS_SoC_Value=iniSoC         #SoC value of ESSs at the begining of optimization horizon
        model.ESS_Capacity=Param(within=PositiveReals)          #Storage Capacity of ESSs
        model.ESS_Max_Charge_Power=Param(within=PositiveReals)  #Max Charge Power of ESSs
        model.ESS_Max_Discharge_Power=Param(within=PositiveReals)#Max Discharge Power of ESSs
        model.ESS_Charging_Eff=Param(within=PositiveReals)      #Charging efficiency of ESSs
        model.ESS_Discharging_Eff=Param(within=PositiveReals)   #Discharging efficiency of ESSs
        
        model.P_Grid_Max_Export_Power=Param(within=NonNegativeReals)    #Max active power export
        model.Q_Grid_Max_Export_Power=Param(within=NonNegativeReals)    #Max reactive power export
        
        model.PV_Inv_Max_Power=Param(within=PositiveReals)              #PV inverter capacity
        ################################################################################################
        
        ##################################       VARIABLES             #################################
        ################################################################################################
        
    
        model.P_Grid_R_Output=Var(model.T,within=Reals)                #Active power exchange with grid at R phase 
        model.P_Grid_S_Output=Var(model.T,within=Reals)                #Active power exchange with grid at S phase
        model.P_Grid_T_Output=Var(model.T,within=Reals)                #Active power exchange with grid at S phase
        model.P_Grid_Output=Var(model.T,within=Reals)
        model.Q_Grid_R_Output=Var(model.T,within=Reals)                #Reactive power exchange with grid at R phase
        model.Q_Grid_S_Output=Var(model.T,within=Reals)                #Reactive power exchange with grid at S phase
        model.Q_Grid_T_Output=Var(model.T,within=Reals)                #Reactive power exchange with grid at T phase
        model.Q_Grid_Output=Var(model.T,within=Reals)
            
        model.P_PV_Output = Var(model.T,within=NonNegativeReals,bounds=(0,model.PV_Inv_Max_Power)) #initialize=iniVal)
        model.P_ESS_Output= Var(model.T,within=Reals,bounds=(-model.ESS_Max_Charge_Power, model.ESS_Max_Discharge_Power))#,initialize=iniSoC)        
        model.SoC_ESS     = Var(model.T_SoC,within=NonNegativeReals,bounds=(model.ESS_Min_SoC,model.ESS_Max_SoC))    
        ################################################################################################
                       
        ###########################################################################
        #######                         CONSTRAINTS                         #######
        
        #PV constraints
        def con_rule_pv_potential(model,t):
            return model.P_PV_Output[t]<= model.P_PV[t]
                
        #Import/Export constraints
        def con_rule_grid_P(model,t):
            return model.P_Grid_Output[t]==model.P_Grid_R_Output[t]+model.P_Grid_S_Output[t]+model.P_Grid_T_Output[t]
        def con_rule_grid_P_inv(model,t):
            return model.P_Grid_Output[t]>=-model.P_Grid_Max_Export_Power
        def con_rule_grid_Q(model,t):
            return model.Q_Grid_Output[t]==model.Q_Grid_R_Output[t]+model.Q_Grid_S_Output[t]+model.Q_Grid_T_Output[t]
        def con_rule_grid_Q_inv(model,t):
            return model.Q_Grid_Output[t]>=-model.Q_Grid_Max_Export_Power
  
        #ESS SoC balance
        def con_rule_socBalance(model,t):
            return model.SoC_ESS[t+1]==model.SoC_ESS[t] - model.P_ESS_Output[t]*model.dT/model.ESS_Capacity/3600    
        def con_rule_iniSoC(model):
            return model.SoC_ESS[0]==model.ESS_SoC_Value
        
        #Generation-feed in balance
        def con_rule_generation_feedin(model,t):
            return model.P_Grid_Output[t]*model.P_Grid_Output[t]+model.Q_Grid_Output[t]*model.Q_Grid_Output[t]==(model.P_PV_Output[t]+model.P_ESS_Output[t])*(model.P_PV_Output[t]+model.P_ESS_Output[t])       
             
        model.con_pv_pmax=Constraint(model.T,rule=con_rule_pv_potential)
        
        model.con_grid_P=Constraint(model.T,rule=con_rule_grid_P)
        model.con_grid_inv_P=Constraint(model.T,rule=con_rule_grid_P_inv)
        model.con_grid_Q=Constraint(model.T,rule=con_rule_grid_Q)
        model.con_grid_inv_Q=Constraint(model.T,rule=con_rule_grid_Q_inv)
        
        model.con_ess_soc=Constraint(model.T,rule=con_rule_socBalance)
        model.con_ess_Inisoc=Constraint(rule=con_rule_iniSoC)
        
        model.con_gen_feedin=Constraint(model.T,rule=con_rule_generation_feedin)
      
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
    #instance.pprint()
    
    results=solver.solve(instance)
    term_status=results.solver.termination_condition.key
    P_ESS=instance.P_ESS_Output[0]()
    resultsDF=recordresults(instance)
        
    print("Termination_status:",term_status)
      
    return term_status,P_ESS,resultsDF


def recordresults(instance):
    
    results_dict={}
    results_dict['01 PV Forecast']=[]
    results_dict['02 PV Generation']=[]
    results_dict['03 ESS Discharge']=[]
    results_dict['04 S Power to Grid']=[]
    results_dict['05 ESS SoC']=[]
    results_dict['06 P Power to Grid']=[]
    results_dict['07 P_Grid_R']=[]
    results_dict['08 P_Grid_S']=[]
    results_dict['09 P_Grid_T']=[]
    results_dict['10 Q Power to Grid']=[]
    results_dict['11 Q_Grid_R']=[]
    results_dict['12 Q_Grid_S']=[]
    results_dict['13 Q_Grid_T']=[]    
    
    
    for t in instance.T:
        results_dict['01 PV Forecast'].append(instance.P_PV[t])
        results_dict['02 PV Generation'].append(instance.P_PV_Output[t]())
        results_dict['03 ESS Discharge'].append(instance.P_ESS_Output[t]())
        results_dict['04 S Power to Grid'].append((instance.P_Grid_Output[t]()**2+instance.Q_Grid_Output[t]()**2)**0.5)
        results_dict['05 ESS SoC'].append(instance.SoC_ESS[t]())
        results_dict['06 P Power to Grid'].append(instance.P_Grid_Output[t]())
        results_dict['07 P_Grid_R'].append(instance.P_Grid_R_Output[t]())
        results_dict['08 P_Grid_S'].append(instance.P_Grid_S_Output[t]())
        results_dict['09 P_Grid_T'].append(instance.P_Grid_T_Output[t]())
        results_dict['10 Q Power to Grid'].append(instance.Q_Grid_Output[t]())
        results_dict['11 Q_Grid_R'].append(instance.Q_Grid_R_Output[t]())
        results_dict['12 Q_Grid_S'].append(instance.Q_Grid_S_Output[t]())
        results_dict['13 Q_Grid_T'].append(instance.Q_Grid_T_Output[t]())           
        
    results=pd.DataFrame(results_dict)
    
    return results
        
#if __name__=="__main__":
    

solver1= SolverFactory("ipopt", executable="C:/Users/guemruekcue/Anaconda3/pkgs/ipopt-3.11.1-2/Library/bin/ipopt")
solver2 = SolverFactory("bonmin", executable="C:/cygwin/home/bonmin/Bonmin-1.8.6/build/bin/bonmin")
#Loading the data file
import os
import time
project_dir=os.path.dirname(__file__)
data_file=project_dir+'/Scenario_10AM_noload.dat'

#%%
soclevels=[]
termst=[]
p_ess=[]
p_pv=[]
p_export=[]

 
for SoC in range(20,86):
    iniSoC=SoC/100
    print("Initial SoC",iniSoC)

    myabstractmodel=MaximizePVUtilization(iniSoC)
    term_status,P_ESS,resultsDF=calculateOptimalTrajectory(myabstractmodel.model,data_file,solver1)
    
    soclevels.append(iniSoC)
    termst.append(term_status)
    p_ess.append(P_ESS)

resdct={"TerminationSt":termst,"P_ESS":p_ess,
        "P_PV":resultsDF['02 PV Generation'][0],"P_Grid":resultsDF['06 P Power to Grid'][0],"Q_Grid":resultsDF['10 Q Power to Grid'][0]}

resDF=pd.DataFrame(resdct,index=soclevels)
writer = pd.ExcelWriter('IniSoC_Pess.xlsx')
resDF.to_excel(writer,"Results")
writer.save()

    