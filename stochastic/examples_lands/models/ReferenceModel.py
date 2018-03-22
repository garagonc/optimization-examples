# -*- coding: utf-8 -*-
"""
Created on Thu Mar 15 14:58:49 2018

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

model.PlantType = Set()
model.OpMode=Set()

model.C_inst=Param(model.PlantType,within=PositiveReals)                #installation cost of plant types
model.Q_op=Param(model.PlantType,model.OpMode,within=PositiveReals)     #Cost per unit operating level of power plant i in mode j .     

model.MinTotCap=Param(within=PositiveReals)                             #The minimum total capacity to be installed                             
model.Budget=Param(within=PositiveReals)                                #Budget available for capacity installment.

model.Demand=Param(model.OpMode,within=NonNegativeReals)                #Random demand for power in mode j                     


#
# Variables
#
model.X=Var(model.PlantType,within=NonNegativeReals)                    #First stage variables: installation
model.Y=Var(model.PlantType,model.OpMode,within=NonNegativeReals)       #Second stage variables: operation


model.FirstStageCost=Var(within=NonNegativeReals)
model.SecondStageCost=Var(within=NonNegativeReals)

#
# Constraints
#
def minimum_total_capacity(model):
    return (sum([model.X[i] for i in model.PlantType])-model.MinTotCap)>=0
model.MinimumTotalCapacity=Constraint(rule=minimum_total_capacity)

def installment_budget(model):
    return (sum([model.C_inst[i]*model.X[i] for i in model.PlantType])-model.Budget)<=0
model.InstalmentBudgedConstraint=Constraint(rule=installment_budget)

def installed_capacity(model,i):
    return (sum([model.Y[i,j] for j in model.OpMode])-model.X[i])<=0
model.OperationCapacityConstraint=Constraint(model.PlantType,rule=installed_capacity)

def demand_meeting(model,j):
    return (sum([model.Y[i,j] for i in model.PlantType])-model.Demand[j]) >=0
model.DemandConstraint=Constraint(model.OpMode,rule=demand_meeting)


def first_stage_cost(model):
    return model.FirstStageCost==sum([model.C_inst[i]*model.X[i] for i in model.PlantType])
model.FirstStageCostConstraint=Constraint(rule=first_stage_cost)

def second_stage_cost(model):
    return model.SecondStageCost==summation(model.Q_op,model.Y)
model.SecondStageCostConstraint=Constraint(rule=second_stage_cost)

#
# Objective
#
def objective_rule(model):
    return model.FirstStageCost+model.SecondStageCost
model.Obj=Objective(rule=objective_rule)











