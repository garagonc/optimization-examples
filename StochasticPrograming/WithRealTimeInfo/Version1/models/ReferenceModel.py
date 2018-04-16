# -*- coding: utf-8 -*-
"""
Created on Mon Mar 19 07:55:37 2018

@author: guemruekcue
"""

from pyomo.core import *

#
# Model
#

model = AbstractModel()

#
# Parameters
#
"""
model.stageNumber=Param(within=PositiveIntegers)
def stages_rule_(model):
    return set(range(1, model.stageNumber()+1))
model.stage=Set(initialize=stages_rule)
"""
model.Stages=Set(initialize=['InitialStage','FutureStage'])
model.T = Set()
model.T_SoC=Set()

model.weightGrid=Param(initialize=0.6)
model.weightEV=Param(initialize=0.4)

model.dT=Param(within=PositiveIntegers)




#Time Invariant parameters
model.PV_Inv_Max_Power=Param(within=PositiveReals)
model.P_Grid_Max_Export_Power=Param(within=NonNegativeReals)
model.ESS_Min_SoC=Param(within=NonNegativeReals)
model.ESS_Max_SoC=Param(within=PositiveReals)
model.ESS_Capacity = Param(within=PositiveReals)
model.ESS_Max_Charge_Power= Param(within=PositiveReals)
model.ESS_Max_Discharge_Power= Param(within=PositiveReals)
#model.ESS_Charging_Eff=Param(model.N,within=PositiveReals)      
#model.ESS_Discharging_Eff=Param(model.N,within=PositiveReals) 
model.EV_Min_SoC=Param(within=NonNegativeReals)
model.EV_Max_SoC=Param(within=PositiveReals)
model.EV_Capacity = Param(within=PositiveReals)
model.EV_Max_Charge_Power= Param(within=PositiveReals)
#model.EV_Charging_Eff=Param(model.N,within=PositiveReals)    
#model.EV_Discharging_Eff=Param(model.N,within=PositiveReals)  


#Real time data
model.ESS_SoC_Value=Param(within=NonNegativeReals)
model.EV_SoC_Value=Param(within=NonNegativeReals)
model.P_PV_Value=Param(within=NonNegativeReals)
model.P_Load_Value=Param(within=NonNegativeReals)
model.Price_Value=Param(within=Reals)


#Supposedly deterministic future paramters
model.P_Load_Forecast = Param(model.T,within=NonNegativeReals)
model.P_PV_Forecast = Param(model.T,within=NonNegativeReals)
model.Price_Forecast = Param(model.T, within=NonNegativeReals)

#Stochastic future parameters
model.EV_ParkAtHome_Forecast = Param(model.T,within=Binary)
model.EV_ParkAway_Forecast   = Param(model.T,within=Binary) #Inferred from above two
model.P_EV_DriveDemand       = Param(model.T,within=NonNegativeReals)

################################################################################################
##################################       VARIABLES             #################################
#############               First stage decision variables        #############
model.P_PV_Output_ini   =Var(within=NonNegativeReals,bounds=(0,model.PV_Inv_Max_Power))
model.P_Grid_Output_ini =Var(within=NonNegativeReals,bounds=(-model.P_Grid_Max_Export_Power,100000))
model.P_ESS_Output_ini  =Var(within=Reals,bounds=(-model.ESS_Max_Charge_Power,model.ESS_Max_Discharge_Power))
model.P_EV_Charge_ini   =Var(within=NonNegativeReals,bounds=(0,model.ESS_Max_Charge_Power))    #V2G neglected

#############               Recourse Stage Variables              #############
model.P_PV_Output   =Var(model.T,within=NonNegativeReals,bounds=(0,model.PV_Inv_Max_Power))                                    #Active power output of PV
model.P_Grid_Output =Var(model.T,within=Reals,bounds=(-model.P_Grid_Max_Export_Power,100000)) 
model.P_ESS_Output  =Var(model.T,within=Reals,bounds=(-model.ESS_Max_Charge_Power,model.ESS_Max_Discharge_Power))

#V2G neglected: Discharge takes place only when car drives
model.P_EV_Charge_AtHome   =Var(model.T,within=NonNegativeReals,bounds=(0,model.ESS_Max_Charge_Power))    
model.P_EV_Charge_Away     =Var(model.T,within=NonNegativeReals,bounds=(0,model.ESS_Max_Charge_Power))     

#############               State variables                       #############
model.SoC_ESS                    =Var(model.T_SoC,within=NonNegativeReals,bounds=(model.ESS_Min_SoC,model.ESS_Max_SoC))
model.SoC_EV                     =Var(model.T_SoC,within=NonNegativeReals,bounds=(model.EV_Min_SoC,model.EV_Max_SoC)) 
model.Absolute_P_Grid_Exchange   =Var(model.T,within=NonNegativeReals)

#############               Stage cost variables                 ##############
model.InitialStageCost=Var(within=NonNegativeReals)
model.FutureStageCost =Var(within=NonNegativeReals)
##################################################################################################

##################################################################################################
##################################       CONSTRAINTS             #################################
#############               Generation side constraints          ##############
def _ini_pv_constraint(model):
    return model.P_PV_Output_ini<=model.P_PV_Value
model.iniPVConstraint=Constraint(rule=_ini_pv_constraint)

def _future_pv_constraint(model,t):
    return 0.0<=model.P_PV_Output[t]<=model.P_PV_Forecast[t]
model.PVConstraint=Constraint(model.T,rule=_future_pv_constraint)


#############               Demand side constraints              ##############
def _ini_demand_meeting(model):
    return model.P_Load_Value+model.P_EV_Charge_ini== model.P_PV_Output_ini + model.P_ESS_Output_ini + model.P_Grid_Output_ini
model.iniDemandConstraint=Constraint(rule=_ini_demand_meeting)

def _future_demand_meeting(model,t):
    return model.P_Load_Forecast[t]+model.P_EV_Charge_AtHome[t]== model.P_PV_Output[t] + model.P_ESS_Output[t] + model.P_Grid_Output[t]
model.DemandConstraint=Constraint(model.T,rule=_future_demand_meeting)

#############               EV charge constraints                ##############
def _ev_charging_athome(model,t):
    return 0.0<=model.P_EV_Charge_AtHome[t]<=model.EV_ParkAtHome_Forecast[t]*model.EV_Max_Charge_Power
model.EV_ChargeAtHome=Constraint(model.T,rule=_ev_charging_athome)

def _ev_charging_away(model,t):
    return 0.0<=model.P_EV_Charge_Away[t]<=model.EV_ParkAway_Forecast[t]*model.EV_Max_Charge_Power
model.EV_ChargeAway=Constraint(model.T,rule=_ev_charging_away)

#############           State variable calculations              ##############
def state_of_charge_ess_firstTs(model):
        return model.SoC_ESS[1]==model.ESS_SoC_Value - model.P_ESS_Output_ini*model.dT/(model.ESS_Capacity*3600) 
model.ESS_SOC_firstTS_Constraint=Constraint(rule=state_of_charge_ess_firstTs)

def state_of_charge_ev_firstTs(model):
        return model.SoC_EV[1]==model.EV_SoC_Value  + model.P_EV_Charge_ini*model.dT/(model.EV_Capacity*3600)
model.EV_SOC_firstTS_Constraint=Constraint(rule=state_of_charge_ev_firstTs)

def state_of_charge_ess(model,t):   
    return model.SoC_ESS[t+1]==model.SoC_ESS[t] - model.P_ESS_Output[t]*model.dT/(model.ESS_Capacity*3600)
model.ESS_SOCConstraint=Constraint(model.T,rule=state_of_charge_ess)

#########################################
def state_of_charge_ev(model,t):
    return model.SoC_EV[t+1]==model.SoC_EV[t] + (model.P_EV_Charge_AtHome[t]+model.P_EV_Charge_Away[t]-model.P_EV_DriveDemand[t])*model.dT/(model.EV_Capacity*3600)
model.EV_SOCConstraint=Constraint(model.T,rule=state_of_charge_ev)

def ComputeAbsoluteFutureImport(model,t):
    #return model.Absolute_of_P_Grid_Output[t]==abs(model.P_Grid_Output[t])
    return model.Absolute_P_Grid_Exchange[t]*model.Absolute_P_Grid_Exchange[t]==model.P_Grid_Output[t]*model.P_Grid_Output[t]
model.AbsoluteFutureImportConstraint = Constraint(model.T,rule=ComputeAbsoluteFutureImport)
  
#############               State cost calculations              ##############
def ComputeInitialStageCost_rule(model):
    #return model.InitialStageCost==abs(model.P_Grid_Output_ini)
    return model.InitialStageCost*model.InitialStageCost==model.P_Grid_Output_ini*model.P_Grid_Output_ini
model.InitialStageCost_Contraint = Constraint(rule=ComputeInitialStageCost_rule)

def ComputeFutureStageCost_rule(model):
    return model.FutureStageCost==sum(model.Absolute_P_Grid_Exchange[t]+model.P_EV_Charge_Away[t] for t in model.T)
model.FutureStageCost_Contraint = Constraint(rule=ComputeFutureStageCost_rule)
##################################################################################################

##################################################################################################
##################################       OBJECTIVE             #################################
def total_cost_rule(model):
    return model.InitialStageCost + model.FutureStageCost
model.Obj = Objective(rule=total_cost_rule, sense=minimize)

