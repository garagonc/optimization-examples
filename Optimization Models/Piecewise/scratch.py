# -*- coding: utf-8 -*-
"""
Created on Tue Feb 13 10:28:29 2018

@author: guemruekcue
"""

from pyomo.environ import *
from pyomo.core import *
from pyomo.opt import SolverFactory

opt= SolverFactory("ipopt", executable="C:/Users/guemruekcue/Anaconda3/pkgs/ipopt-3.11.1-2/Library/bin/ipopt")


model = ConcreteModel()
model.ind=RangeSet(0,3)
model.bat = Var(bounds=(-5.0,5.0))
model.ch = Var(bounds=(0.0,5.0))
model.dis = Var(bounds=(0.0,5.0))

x=[-5.0,0.0,5.0]

def y_ch(model,x):
    if x>=0:
        return 0.0
    else:
        return -x
    
def y_dis(model,x):
    if x>=0:
        return x
    else:
        return 0.0


model.fx1 = Piecewise(model.ch, model.bat,
                     pw_pts=x,
                     pw_constr_type='EQ',
                     f_rule=y_ch)

model.fx2 = Piecewise(model.dis, model.bat,
                     pw_pts=x,
                     pw_constr_type='EQ',
                     f_rule=y_dis)

model.o = Objective(expr=model.bat)

opt.solve(model)
model.pprint()