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

model.Horizon = Param()
model.dT=Param()

model.BatteryCapacity = Param(within=PositiveReals)
model.BatterykW= Param(within=PositiveReals)

model.minSOC=Param(within=PositiveReals)
model.maxSOC=Param(within=PositiveReals)
model.iniSOC=Param(within=PositiveReals)

model.maxImp=Param(within=NonNegativeReals)
model.maxExp=Param(within=NonNegativeReals)

model.T=RangeSet(0,model.Horizon-1)
model.Tsoc=RangeSet(0,model.Horizon)

#Deterministic parameters
model.PV = Param(model.T,within=NonNegativeReals)
model.Demand = Param(model.T,within=NonNegativeReals)
model.Price = Param(model.T, within=NonNegativeReals)

#Stochastic parameters
model.EV = Param(model.T)
#TODO: different prices for export and import

#
# Variables
#
model.PBAT= Var(model.T,bounds=(-model.BatterykW,model.BatterykW))
model.PGRID=Var(model.T,bounds=(-model.maxExp,model.maxImp))
model.pPV=Var(model.T,bounds=(0,1))             
model.SoC=Var(model.Tsoc,bounds=(model.minSOC,model.maxSOC))

#
# Constraints
#
def demand_meeting(model,t):
    return model.Demand[t]== model.pPV[t]*model.PV[t] + model.PBAT[t] + model.PGRID[t]-model.EV[t]
model.DemandConstraint=Constraint(model.T,rule=demand_meeting)

def state_of_charge(model,t):
    if t==0:
        return model.SoC[t]==model.iniSOC     
    return model.SoC[t+1]==model.SoC[t] - model.PBAT[t]*model.dT/model.BatteryCapacity
model.SOCConstraint=Constraint(model.T,rule=state_of_charge)


#
# Stage-specific cost computations
#

def ComputeFirstStageCost_rule(model):
    #return sum((1-model.pPV[t])*model.PV[t] for t in model.T)
    return 0
model.FirstStageCost = Expression(rule=ComputeFirstStageCost_rule)

def ComputeSecondStageCost_rule(model):
    return sum(model.PGRID[t]*model.PGRID[t] for t in model.T)
model.SecondStageCost = Expression(rule=ComputeSecondStageCost_rule)

#
# Objective
#
def total_cost_rule(model):
    return model.FirstStageCost + model.SecondStageCost
model.Obj = Objective(rule=total_cost_rule, sense=minimize)

