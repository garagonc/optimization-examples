# -*- coding: utf-8 -*-
"""
Created on Tue Feb 20 14:43:42 2018

@author: guemruekcue
"""


from pyomo.environ import *
from pyomo.core import *
from pyomo.opt import SolverFactory

#opt= SolverFactory("ipopt", executable="C:/Users/guemruekcue/Anaconda3/pkgs/ipopt-3.11.1-2/Library/bin/ipopt")
opt= SolverFactory("bonmin", executable="C:/cygwin/home/bonmin/Bonmin-1.8.6/build/bin/bonmin")

model = ConcreteModel()
model.ind=RangeSet(1,2)
model.socind=RangeSet(1,3)

model.bat = Var(model.ind,bounds=(-5.0,5.0))
model.ch = Var(model.ind)#,bounds=(0.0,5.0))
model.dis = Var(model.ind)#,bounds=(0.0,5.0))
model.soc=Var(model.socind)


x={}
x[1]=[-5.0,0.0,5.0]
x[2]=[-5.0,0.0,5.0]


def y_ch(model,t,x):
    if x>=0:
        return 0.0
    else:
        return -x
   
def y_dis(model,t,x):
    if x>=0:
        return x
    else:
        return 0.0



model.fx1 = Piecewise(model.ind,model.ch, model.bat,
                     pw_pts=x,
                     pw_constr_type='EQ',
                     f_rule=y_ch)

model.fx2 = Piecewise(model.ind,model.dis, model.bat,
                     pw_pts=x,
                     pw_constr_type='EQ',
                     f_rule=y_dis)

def con_rule2(model,m):
    return model.soc[m+1]==model.soc[m]+0.8*model.ch[m]-1.25*model.dis[m]
def con_rule3(model):
    return model.soc[1]==5
model.con2=Constraint(model.ind,rule=con_rule2)
model.con3=Constraint(rule=con_rule3)

       

model.o = Objective(expr=(model.bat[1]+0.25)*(model.bat[1]+0.25)+(model.bat[2]-1.25)*(model.bat[2]-1.25))

opt.solve(model)
model.bat.pprint()
model.ch.pprint()
model.dis.pprint()
model.soc.pprint()

