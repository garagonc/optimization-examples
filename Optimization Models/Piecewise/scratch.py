# -*- coding: utf-8 -*-
"""
Created on Tue Feb 13 10:28:29 2018

@author: guemruekcue
"""

from pyomo.environ import *
from pyomo.core import *
from pyomo.opt import SolverFactory

#opt= SolverFactory("ipopt", executable="C:/Users/guemruekcue/Anaconda3/pkgs/ipopt-3.11.1-2/Library/bin/ipopt")
opt= SolverFactory("bonmin", executable="C:/cygwin/home/bonmin/Bonmin-1.8.6/build/bin/bonmin")


model = ConcreteModel()
model.ind=RangeSet(1,2)

model.bat = Var(model.ind,bounds=(-5.0,5.0))

model.socind=RangeSet(1,3)
model.soc=Var(model.socind,bounds=(0.2,0.5))
model.soc[1]=0.35
model.eff=Var(model.ind)

#%%

x={}
x[1]=[-5.0,0.0,5.0]
x[2]=[-5.0,0.0,5.0]

def y_ef(model,y,x):
    if x<0:
        return 0.9
    else:
        return 1.4

model.fx = Piecewise(model.ind,model.eff, model.bat,
                     pw_pts=x,
                     pw_constr_type='EQ',
                     f_rule=y_ef)

#%%
def con_rule3(model,m):
    return model.soc[m+1]==model.soc[m]+ model.eff[m]*model.bat[m]/1000
model.con3=Constraint(model.ind,rule=con_rule3)

model.o = Objective(expr=(model.bat[1]-2.5)*(model.bat[1]-2.5)+(model.bat[2]+1.25)*(model.bat[2]+1.25))

opt.solve(model)
model.bat.pprint()
model.eff.pprint()
model.o.pprint()


