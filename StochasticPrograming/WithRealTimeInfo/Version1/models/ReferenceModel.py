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
model.Stages=Set(initialize=['InitialStage','FutureStage1','FutureStage2','FutureStage3','FutureStage4'])
model.T = Set()
model.T_SoC=Set()

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
model.EV_Charge_Max_Power= Param(within=PositiveReals)
#model.EV_Charging_Eff=Param(model.N,within=PositiveReals)      


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
model.EV_Occurance_Forecast = Param(model.T,within=Binary)


#
# Variables
#
##################################       VARIABLES             #################################
#############               Initial Stage Variables                       #############
model.P_PV_Output_ini   =Var(within=NonNegativeReals,bounds=(0,model.PV_Inv_Max_Power))
model.P_Grid_Output_ini =Var(within=NonNegativeReals,bounds=(-model.P_Grid_Max_Export_Power,100000))
model.P_ESS_Output_ini  =Var(within=Reals,bounds=(-model.ESS_Max_Charge_Power,model.ESS_Max_Discharge_Power))
model.P_EV_Output_ini   =Var(within=NonNegativeReals,bounds=(0,model.ESS_Max_Charge_Power))    #V2G neglected


################################################################################################
#############               Future Stage Variables                       #############
model.P_PV_Output   =Var(model.T,within=NonNegativeReals,bounds=(0,model.PV_Inv_Max_Power))                                    #Active power output of PV
model.P_Grid_Output =Var(model.T,within=Reals,bounds=(-model.P_Grid_Max_Export_Power,100000)) 
model.P_ESS_Output  =Var(model.T,within=Reals,bounds=(-model.ESS_Max_Charge_Power,model.ESS_Max_Discharge_Power))
model.P_EV_Output   =Var(model.T,within=NonNegativeReals,bounds=(0,model.ESS_Max_Charge_Power))    #V2G neglected

model.SoC_ESS=Var(model.T_SoC,within=NonNegativeReals,bounds=(model.ESS_Min_SoC,model.ESS_Max_SoC))
model.SoC_EV =Var(model.T_SoC,within=NonNegativeReals,bounds=(model.EV_Min_SoC,model.EV_Max_SoC)) 
     
################################################################################################
def _ini_demand_meeting(model):
    return model.P_Load_Value+model.P_EV_Output_ini== model.P_PV_Output_ini + model.P_ESS_Output_ini + model.P_Grid_Output_ini
model.iniDemandConstraint=Constraint(rule=_ini_demand_meeting)

def _ini_pv_constraint(model):
    return model.P_PV_Output_ini<=model.P_PV_Value
model.iniPVConstraint=Constraint(rule=_ini_pv_constraint)

#
# Future Stage Constraints
#
def _future_demand_meeting(model,t):
    return model.P_Load_Forecast[t]+model.P_EV_Output[t]== model.P_PV_Output[t] + model.P_ESS_Output[t] + model.P_Grid_Output[t]
model.DemandConstraint=Constraint(model.T,rule=_future_demand_meeting)

def _future_pv_constraint(model,t):
    return model.P_PV_Output[t]<=model.P_PV_Forecast[t]
model.PVConstraint=Constraint(model.T,rule=_future_pv_constraint)

def state_of_charge_ess(model,t):
    if t==1:
        return model.SoC_ESS[t]==model.ESS_SoC_Value - model.P_ESS_Output_ini*model.dT/model.ESS_Capacity    
    return model.SoC_ESS[t+1]==model.SoC_ESS[t] - model.P_ESS_Output[t]*model.dT/model.ESS_Capacity
model.ESS_SOCConstraint=Constraint(model.T,rule=state_of_charge_ess)

def state_of_charge_ev(model,t):
    if t==1:
        return model.SoC_EV[t]==model.EV_SoC_Value  + model.P_EV_Output_ini*model.dT/model.ESS_Capacity
    return model.SoC_EV[t+1]==model.SoC_EV[t] + model.P_EV_Output[t]*model.dT/model.EV_Capacity
model.EV_SOCConstraint=Constraint(model.T,rule=state_of_charge_ev)

def ev_charging(model,t):
    return model.P_EV_Output[t]<=model.EV_Occurance_Forecast[t]*model.ESS_Max_Charge_Power
model.EV_OccuranceConstraint=Constraint(model.T,rule=ev_charging)

#
# Stage-specific cost computations
#


def ComputeInitialStageCost_rule(model):
    return model.P_Grid_Output_ini*model.P_Grid_Output_ini
model.InitialStageCost = Expression(rule=ComputeInitialStageCost_rule)

def ComputeFutureStageCost_rule(model):
    return sum(model.P_Grid_Output[t]*model.P_Grid_Output[t] for t in model.T)
model.FutureStageCost = Expression(rule=ComputeFutureStageCost_rule)

#
# Objective
#
def total_cost_rule(model):
    return model.InitialStageCost + model.FutureStageCost
model.Obj = Objective(rule=total_cost_rule, sense=minimize)

