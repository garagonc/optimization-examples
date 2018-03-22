# Imports
#

from pyomo.core import *

#
# Model
#

model = AbstractModel()

#
# Parameters
#


model.Investments = Set()

model.InitialWealth = Param(within=PositiveReals)

model.TargetCapital = Param(within=PositiveReals)

model.ExcessPerUnitBenefit = Param(within=PositiveReals)
model.ShortagePerUnitCost = Param(within=PositiveReals)

model.NumTimes = Param(within=PositiveIntegers)

def stages_rule(model):
    return set(range(1, model.NumTimes()+1))
model.Times = Set(initialize=stages_rule)

model.Return=Param(model.Investments,model.Times)

#
# Variables
#
model.StageCost = Var(model.Times)

model.AmountInvested=Var(model.Investments,model.Times, within=NonNegativeReals)
#model.Wealth=Var(model.Times)

model.TargetDeficit=Var(within=NonNegativeReals)
model.TargetSurplus=Var(within=NonNegativeReals)
model.FinalWealth=Var()


#
# Constraints
#
def force_wealth_distribution(model, t):
    if t == 1:
        return (sum([model.AmountInvested[i,1] for i in model.Investments]) - model.InitialWealth) == 0.0
    else:
        return (sum([model.Return[i,t-1] * model.AmountInvested[i,t-1] for i in model.Investments]) - sum([model.AmountInvested[i,t] for i in model.Investments])) == 0.0
model.ForceWealthDistributionConstraint = Constraint(model.Times, rule=force_wealth_distribution)

def compute_surplus_deficit(model):
    return (sum([model.AmountInvested[i,model.NumTimes()]*model.Return[i,model.NumTimes()] for i in model.Investments])-model.TargetCapital-model.TargetSurplus+model.TargetDeficit)== 0.0
model.ComputeSurplusDeficitConstraint= Constraint(rule=compute_surplus_deficit)

def compute_final_wealth(model):
    return (model.FinalWealth-model.ExcessPerUnitBenefit*model.TargetSurplus+model.ShortagePerUnitCost*model.TargetDeficit)==0
model.ComputeFinalWealth=Constraint(rule=compute_final_wealth)

#
# Objective
#
def obj_rule(model):
    return model.FinalWealth
model.TotalWealthObjective=Objective(rule=obj_rule,sense=maximize)



