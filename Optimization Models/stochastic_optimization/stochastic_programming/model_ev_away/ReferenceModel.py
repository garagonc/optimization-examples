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

model.iniT=Set()
model.recT=Set()
model.T = Set()
model.T_SoC=Set()

model.weightGridExchange=Param(initialize=1.0)
model.weightEVAwayCharging=Param(initialize=1.0)
#TODO: Non-constant over time

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
#################               First stage decision variables                 #################
model.P_PV_Output_ini    =Var(model.iniT,within=NonNegativeReals,bounds=(0,model.PV_Inv_Max_Power))
model.P_Grid_Output_ini  =Var(model.iniT,within=NonNegativeReals,bounds=(-model.P_Grid_Max_Export_Power,100000))
model.P_ESS_Output_ini   =Var(model.iniT,within=Reals,bounds=(-model.ESS_Max_Charge_Power,model.ESS_Max_Discharge_Power))
model.P_EV_ChargeHome_ini=Var(model.iniT,within=NonNegativeReals,bounds=(0,model.ESS_Max_Charge_Power))    #V2G neglected: Discharge takes place only when car drives
model.P_EV_ChargeAway_ini=Var(model.iniT,within=NonNegativeReals,bounds=(0,model.ESS_Max_Charge_Power))   #Optimization starts at home  

#################              Recourse Stage Variables                        #################
model.P_PV_Output_rec    =Var(model.recT,within=NonNegativeReals,bounds=(0,model.PV_Inv_Max_Power))                                    #Active power output of PV
model.P_Grid_Output_rec  =Var(model.recT,within=Reals,bounds=(-model.P_Grid_Max_Export_Power,100000)) 
model.P_ESS_Output_rec   =Var(model.recT,within=Reals,bounds=(-model.ESS_Max_Charge_Power,model.ESS_Max_Discharge_Power))
model.P_EV_ChargeHome_rec=Var(model.recT,within=NonNegativeReals,bounds=(0,model.ESS_Max_Charge_Power))    
model.P_EV_ChargeAway_rec=Var(model.recT,within=NonNegativeReals,bounds=(0,model.ESS_Max_Charge_Power))     

#################                     State Variables                          #################
model.SoC_ESS                    =Var(model.T_SoC,within=NonNegativeReals,bounds=(model.ESS_Min_SoC,model.ESS_Max_SoC))
model.SoC_EV                     =Var(model.T_SoC,within=NonNegativeReals,bounds=(model.EV_Min_SoC,model.EV_Max_SoC)) 
model.Absolute_P_Grid_Exchange   =Var(model.T,within=NonNegativeReals)

#################                 Stage Costs Variables                        #################
model.InitialStageCost=Var(within=NonNegativeReals)
model.FutureStageCost =Var(within=NonNegativeReals)
##################################################################################################

##################################################################################################
##################################       CONSTRAINTS             #################################
#############               Generation side constraints                        ##############
def _ini_pv_constraint(model,t):
    return 0.0<=model.P_PV_Output_ini[t]<=model.P_PV_Forecast[t]
model.iniPVConstraint=Constraint(model.iniT,rule=_ini_pv_constraint)

def _rec_pv_constraint(model,t):
    return 0.0<=model.P_PV_Output_rec[t]<=model.P_PV_Forecast[t]
model.recPVConstraint=Constraint(model.recT,rule=_rec_pv_constraint)

#############               House demand side constraints         ##############
def _ini_demand_meeting(model,t):
    return model.P_Load_Forecast[t]== model.P_PV_Output_ini[t] + model.P_ESS_Output_ini[t] + model.P_Grid_Output_ini[t]
model.iniDemandConstraint=Constraint(model.iniT,rule=_ini_demand_meeting)

def _rec_demand_meeting(model,t):
    return model.P_Load_Forecast[t]+model.P_EV_ChargeHome_rec[t]== model.P_PV_Output_rec[t] + model.P_ESS_Output_rec[t] + model.P_Grid_Output_rec[t]
model.recDemandConstraint=Constraint(model.recT,rule=_rec_demand_meeting)

#############               EV charge constraints                ##############
def _ini_ev_charging_athome(model,t):
    return model.P_EV_ChargeHome_ini[t]==0
model.EV_ChargeHome_ini=Constraint(model.iniT,rule=_ini_ev_charging_athome)

def _ini_ev_charging_away(model,t):
    return 0.0<=model.P_EV_ChargeAway_ini[t]<=model.EV_ParkAway_Forecast[t]*model.EV_Max_Charge_Power
model.EV_ChargeAway_ini=Constraint(model.iniT,rule=_ini_ev_charging_away)

def _rec_ev_charging_athome(model,t):
    return 0.0<=model.P_EV_ChargeHome_rec[t]<=model.EV_ParkAtHome_Forecast[t]*model.EV_Max_Charge_Power
model.EV_ChargeAtHome_rec=Constraint(model.recT,rule=_rec_ev_charging_athome)

def _rec_ev_charging_away(model,t):
    return 0.0<=model.P_EV_ChargeAway_rec[t]<=model.EV_ParkAway_Forecast[t]*model.EV_Max_Charge_Power
model.EV_ChargeAway_rec=Constraint(model.recT,rule=_rec_ev_charging_away)


#################           Real-time information constraints                  #################
def state_of_charge_ess_firstTs(model):
        return model.SoC_ESS[min(model.iniT)]==model.ESS_SoC_Value
model.ESS_SOC_firstTS_Constraint=Constraint(rule=state_of_charge_ess_firstTs)

def state_of_charge_ev_firstTs(model):
        return model.SoC_EV[min(model.iniT)]==model.EV_SoC_Value
model.EV_SOC_firstTS_Constraint=Constraint(rule=state_of_charge_ev_firstTs)


#################           State variable calculations                        #################
def _ini_state_of_charge_ess(model,t):   
    return model.SoC_ESS[t+1]==model.SoC_ESS[t] - model.P_ESS_Output_ini[t]*model.dT/(model.ESS_Capacity*3600)
def _rec_state_of_charge_ess(model,t):
    return model.SoC_ESS[t+1]==model.SoC_ESS[t] - model.P_ESS_Output_rec[t]*model.dT/(model.ESS_Capacity*3600)
model.ESS_SOCConstraint_ini=Constraint(model.iniT,rule=_ini_state_of_charge_ess)
model.ESS_SOCConstraint_rec=Constraint(model.recT,rule=_rec_state_of_charge_ess)

def _ini_state_of_charge_ev(model,t):
    return model.SoC_EV[t+1]==model.SoC_EV[t] + (+model.P_EV_ChargeAway_ini[t]-model.P_EV_DriveDemand[t])*model.dT/(model.EV_Capacity*3600)
def _rec_state_of_charge_ev(model,t):
    return model.SoC_EV[t+1]==model.SoC_EV[t] + (model.P_EV_ChargeHome_rec[t]+model.P_EV_ChargeAway_rec[t]-model.P_EV_DriveDemand[t])*model.dT/(model.EV_Capacity*3600)
model.EV_SOCConstraint_ini=Constraint(model.iniT,rule=_ini_state_of_charge_ev)
model.EV_SOCConstraint_rec=Constraint(model.recT,rule=_rec_state_of_charge_ev)

def _ini_ComputeAbsoluteImport(model,t):
    return model.Absolute_P_Grid_Exchange[t]*model.Absolute_P_Grid_Exchange[t]==model.P_Grid_Output_ini[t]*model.P_Grid_Output_ini[t]
def _rec_ComputeAbsoluteImport(model,t):
    return model.Absolute_P_Grid_Exchange[t]*model.Absolute_P_Grid_Exchange[t]==model.P_Grid_Output_rec[t]*model.P_Grid_Output_rec[t]
model.AbsoluteImportConstraint_ini = Constraint(model.iniT,rule=_ini_ComputeAbsoluteImport)
model.AbsoluteImportConstraint_rec = Constraint(model.recT,rule=_rec_ComputeAbsoluteImport)
  
#############               State cost calculations              ##############
def ComputeInitialStageCost_rule(model):
    return model.InitialStageCost==sum(model.weightGridExchange*model.Absolute_P_Grid_Exchange[t] for t in model.iniT)
model.InitialStageCost_Contraint = Constraint(rule=ComputeInitialStageCost_rule)

def ComputeFutureStageCost_rule(model):
    return model.FutureStageCost==sum(model.weightGridExchange*model.Absolute_P_Grid_Exchange[t]+model.weightEVAwayCharging*model.P_EV_ChargeAway_rec[t] for t in model.recT)
model.FutureStageCost_Contraint = Constraint(rule=ComputeFutureStageCost_rule)
##################################################################################################

##################################################################################################
##################################       OBJECTIVE             #################################
def total_cost_rule(model):
    return model.InitialStageCost + model.FutureStageCost
model.Obj = Objective(rule=total_cost_rule, sense=minimize)

