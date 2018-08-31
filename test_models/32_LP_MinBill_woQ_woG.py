# -*- coding: utf-8 -*-
"""
Created on Thu Aug  2 15:02:25 2018

@author: guemruekcue
"""

from pyomo.core import *

class Model:
    model = AbstractModel()

    model.N=Set()                                                   #Index Set for energy storage system devices
    model.T=Set()                                                   #Index Set for time steps of optimization horizon
    model.T_SoC=Set()                                               #SoC of the ESSs at the end of optimization horizon are also taken into account
    
    
    ##################################       PARAMETERS            #################################
    ################################################################################################                                               
    
    model.dT=Param(within=PositiveIntegers)                         #Number of seconds in one time step
    
    model.P_Load_Forecast=Param(model.T,within=NonNegativeReals)    #Active power demand forecast
    #TODO: Assign a default
    
    model.P_PV_Forecast=Param(model.T,within=NonNegativeReals)      #PV PMPP forecast
    model.PV_Inv_Max_Power=Param(within=PositiveReals)              #PV inverter capacity
    
    model.ESS_Min_SoC=Param(model.N,within=PositiveReals)           #Minimum SoC of ESSs
    model.ESS_Max_SoC=Param(model.N,within=PositiveReals)           #Maximum SoC of ESSs
    model.ESS_SoC_Value=Param(model.N,within=PositiveReals)         #SoC value of ESSs at the begining of optimization horizon
    model.ESS_Capacity=Param(model.N,within=PositiveReals)          #Storage Capacity of ESSs
    model.ESS_Max_Charge_Power=Param(model.N,within=PositiveReals)  #Max Charge Power of ESSs
    model.ESS_Max_Discharge_Power=Param(model.N,within=PositiveReals)#Max Discharge Power of ESSs
    model.ESS_Charging_Eff=Param(model.N,within=PositiveReals)      #Charging efficiency of ESSs
    model.ESS_Discharging_Eff=Param(model.N,within=PositiveReals)   #Discharging efficiency of ESSs
    
    model.P_Grid_Max_Export_Power=Param(within=NonNegativeReals)    #Max active power export
    
    model.Price_Forecast=Param(model.T)                             #Electric price forecast
    
    ################################################################################################
    
    ##################################       VARIABLES             #################################
    ################################################################################################
    model.P_PV_Output=Var(model.T,within=NonNegativeReals,bounds=(0,model.PV_Inv_Max_Power))                                    #Active power output of PV
    
    def ESS_Power_Bounds(model,n,t):
       return (-model.ESS_Max_Charge_Power[n], model.ESS_Max_Discharge_Power[n])
    model.P_ESS_Output = Var(model.N,model.T,within=Reals,bounds=ESS_Power_Bounds)
    
    def ESS_SOC_Bounds(model,n,t):
        return (model.ESS_Min_SoC[n], model.ESS_Max_SoC[n])
    model.SoC_ESS=Var(model.N,model.T_SoC,within=NonNegativeReals,bounds=ESS_SOC_Bounds)
            
    model.P_Grid_Output=Var(model.T,within=Reals,bounds=(-model.P_Grid_Max_Export_Power,100000))                                 #Active power exchange with grid  
    ################################################################################################
    
           
    ###########################################################################
    #######                         CONSTRAINTS                         #######
    #######                Rule1: P_power demand meeting                #######
    #######                Rule2: PV power limitation                   #######
    #######                Rule3: State of charge consistency           #######
    #######                Rule4: Initial State of charge               #######
    ###########################################################################
    def con_rule1(model,t):
        return model.P_Load_Forecast[t]==model.P_PV_Output[t]+ model.P_Grid_Output[t] + sum(model.P_ESS_Output[n,t] for n in model.N)  
    def con_rule2(model,t):
        return 0<=model.P_PV_Output[t]<=model.P_PV_Forecast[t]
    def con_rule3(model,n,t):
        return model.SoC_ESS[n,t+1]==model.SoC_ESS[n,t] - model.P_ESS_Output[n,t]*model.dT/model.ESS_Capacity[n]
    def con_rule4(model,n):
        return model.SoC_ESS[n,0]==model.ESS_SoC_Value[n]
  
    model.con1=Constraint(model.T,rule=con_rule1)
    model.con2=Constraint(model.T,rule=con_rule2)
    model.con3=Constraint(model.N,model.T,rule=con_rule3)
    model.con4=Constraint(model.N,rule=con_rule4)
    
    ###########################################################################
    #######                         OBJECTIVE                           #######
    ###########################################################################
    def obj_rule(model):  
        return sum(model.Price_Forecast[t]*model.P_Grid_Output[t] for t in model.T)
    model.obj=Objective(rule=obj_rule, sense = minimize)