# -*- coding: utf-8 -*-
"""
Created on Fri Feb  9 14:20:01 2018

@author: guemruekcue
"""
"""
#%%


#  ___________________________________________________________________________
#
#  Pyomo: Python Optimization Modeling Objects
#  Copyright 2017 National Technology and Engineering Solutions of Sandia, LLC
#  Under the terms of Contract DE-NA0003525 with National Technology and 
#  Engineering Solutions of Sandia, LLC, the U.S. Government retains certain 
#  rights in this software.
#  This software is distributed under the 3-clause BSD License.
#  ___________________________________________________________________________

# A simple example illustrating a piecewise
# representation of the function Z(X)
# 
#          / -X+2 , -5 <= X <= 1
#  Z(X) >= |
#          \  X ,  1 <= X <= 5
#


from pyomo.core import *
from pyomo.environ import *
from pyomo.opt import SolverFactory

# Define the function
opt= SolverFactory("ipopt", executable="C:/Users/guemruekcue/Anaconda3/pkgs/ipopt-3.11.1-2/Library/bin/ipopt")
# Just like in Pyomo constraint rules, a Pyomo model object
# must be the first argument for the function rule

model = ConcreteModel()
model.hor=RangeSet(0,1)

def f(model,hor,x):
    return abs(x)

model.X = Var(bounds=(-5,5))
model.Z = Var()

model.con = Piecewise(model.Z,model.X, # range and domain variables
                      pw_pts=[-5,0,5] ,
                      pw_constr_type='EQ',
                      f_rule=f)

model.obj = Objective(expr=model.Z, sense=minimize)

# The default piecewise representation implemented by Piecewise is SOS2.
# Note, however, that no SOS2 variables will be generated since the 
# check for convexity within Piecewise automatically simplifies the constraints
# when a lower bounding convex function is supplied. Adding 'force_pw=True'
# to the Piecewise argument list will cause the original piecewise constraints
# to be used even when simplifications can be applied.
model.obj = Objective(expr=model.Z, sense=minimize)

#%%

opt.solve(model)
model.Z.pprint()
"""

#%%
from pyomo.core import *

# Define the function
# Just like in Pyomo constraint rules, a Pyomo model object
# must be the first argument for the function rule
def f(model,t1,x):
    return abs(x)


model = ConcreteModel()

# Note we can use an arbitrary number of index sets of 
# arbitrary dimension as the first arguments to the
# Piecewise component.
model.INDEX1 = RangeSet(0,4)
model.X = Var(model.INDEX1, bounds=(-2,2))
model.Z = Var(model.INDEX1)
#%%
PW_PTS = {}

for idx in model.X.index_set():
    PW_PTS[idx] = [-2,0,2]   # [-2.0, ..., 2.0]


#%%
model.linearized_constraint = Piecewise(model.INDEX1,        # indexing sets
                                        model.Z,model.X,     # range and domain variables
                                        pw_pts=PW_PTS,
                                        pw_constr_type='EQ',
                                        f_rule=f,
                                        force_pw=True)

# maximize the sum of Z over its index
# This is just a simple example of how to implement indexed variables. All indices
# of Z will have the same solution.
model.obj = Objective(expr= summation(model.Z,index=model.INDEX1) , sense=maximize)

