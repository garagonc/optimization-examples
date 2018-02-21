# -*- coding: utf-8 -*-
"""
Created on Tue Feb 20 14:44:56 2018

@author: guemruekcue
"""

DOMAIN_PTS={}
DOMAIN_PTS[1] = [-5., 0., 0., 2., 2., 3.]
DOMAIN_PTS[2] = [-5., 0., 0., 2., 2., 3.]

def frule(model,t,x):
    if x<0:
        return -3.1
    else:
        return 4.1

model = ConcreteModel()
model.ind=RangeSet(1,2)

model.X = Var(model.ind,bounds=(0,3))
model.Z = Var(model.ind)

# See documentation on Piecewise component by typing
# help(Piecewise) in a python terminal after importing pyomo.core
model.con = Piecewise(model.ind,
                      model.Z,model.X, # range and domain variables
                      pw_pts=DOMAIN_PTS ,
                      pw_constr_type='EQ',
                      f_rule=frule)

model.obj = Objective(expr=sum((model.Z[m]-2.5)*(model.X[m]+1.8) for m in model.ind), sense=minimize)
#%%
opt.solve(model)
model.X.pprint()
model.Z.pprint()
