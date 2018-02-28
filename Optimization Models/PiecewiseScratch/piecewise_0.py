# -*- coding: utf-8 -*-
"""
Created on Fri Feb  9 15:25:31 2018

@author: guemruekcue
"""
#%%
from pyomo.environ import *
from pyomo.core import *
from pyomo.opt import SolverFactory
import matplotlib.pylab as plt
import os

########################################
########################################

#Minimum interaction with grid

########################################
########################################


# Create a solver

"""
#GUSTAVO
opt= SolverFactory("ipopt", executable="C:/Users/garagon/Anaconda3/pkgs/ipopt-3.11.1-2/Library/bin/ipopt")
"""
#ERDEM
opt= SolverFactory("ipopt", executable="C:/Users/guemruekcue/Anaconda3/pkgs/ipopt-3.11.1-2/Library/bin/ipopt")

projectpath=os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

#%%%
print("#################################################")
print("Starting the optimizer")
print("#################################################")
price=0.3
timeInterval=1

file = open(projectpath+'/profiles/load_profile_1.txt', 'r')
lines = file.read().splitlines()
keys=range(len(lines))
Pdem = {}
for i in keys:
    Pdem[keys[i]]=float(lines[i])

file = open(projectpath+'/profiles/PV_profile3.txt', 'r')
linesPV = file.read().splitlines()
keysPV=range(len(linesPV))
PV = {}
for i in keysPV:
    PV[keysPV[i]]=float(linesPV[i])


N=len(Pdem)
Eff_Charging=0.9
Eff_Discharging= 0.7
Capacity=9.6*3600   #kWs

model = ConcreteModel()
model.lengthSoC=RangeSet(0,N)
model.answers=RangeSet(0,N-1)
model.PBAT= Var(model.answers,bounds=(-5.6,5.6))        
model.PGRID=Var(model.answers,bounds=(-10,10),initialize=0)                 
model.SoC=Var(model.lengthSoC,bounds=(0.20,0.95))
model.PVmod=Var(model.answers,bounds=(0,1),initialize=1)

#%%
model.gridAbs=Var(model.answers)  #Absolute value of the the power imported/exported to grid

PW_PTS = {}
for idx in model.PGRID.index_set():
    PW_PTS[idx] = [-10,0,10]

def f_obj(model,t,x):
    return abs(x)

model.con_obj = Piecewise(model.answers,       
                  model.gridAbs,model.PGRID,
                  pw_pts=PW_PTS,
                  pw_constr_type='EQ',
                  f_rule=f_obj,
                  force_pw=True)

#%%
print("#################################################")
print("Objective function")
print("#################################################")  
model.obj = Objective(expr= summation(model.gridAbs,index=model.answers) , sense=minimize)

#%%
print("#################################################")
print("Constraints")
print("#################################################")     
def con_rule2(model,m):
    return Pdem[m]== model.PVmod[m]*PV[m] + model.PBAT[m] + model.PGRID[m]
model.con2=Constraint(model.answers,rule=con_rule2)

def con_rule3(model,m):
    return model.SoC[m+1]==model.SoC[m] - model.PBAT[m]*60/Capacity
    #return model.SoC[m+1]==model.SoC[m] +model.X[m]
model.con3=Constraint(model.answers,rule=con_rule3)

def con_rule6(model):
    return model.SoC[0]==0.35
model.con6=Constraint(rule=con_rule6)


print("#################################################")
print("Solving")
print("#################################################")

# Create a model instance and optimize
instance=model.create()
results=opt.solve(instance)


print("#################################################")
print("Plots")
print("#################################################")

lists = sorted(Pdem.items())
x1, y1 = zip(*lists) 

listsPV = sorted(PV.items()) 
x2, y2 = zip(*listsPV) 

listsPVutil = sorted(instance.PVmod.items())
listsPStorageP = sorted(instance.PBAT.items()) 
listsSOC= sorted(instance.SoC.items())
listsGrid = sorted(instance.PGRID.items())
listsabsGrid = sorted(instance.gridAbs.items()) 

x3, y = zip(*listsPVutil) 
y3=[]
for value in y:
    y3.append(value.value*PV[y.index(value)])
     
x4, y = zip(*listsPStorageP)
y4=[]
for value in y:
    y4.append(value.value)

x5, y = zip(*listsSOC)
y5=[]
for value in y:
    y5.append(value.value)
    
x6, y = zip(*listsGrid)
y6=[]
for value in y:
    y6.append(value.value)

x7, y = zip(*listsabsGrid)
y7=[]
for value in y:
    y7.append(value.value)


fig1=plt.subplot(4,1,1)
fig1.set_title('Power Summary')
plt.plot(x1, y1,label='Demand')
plt.plot(x2, y2,label='PV Potential')
plt.plot(x3, y3,label='PV Utilized')
plt.legend()

fig2=plt.subplot(4,1,2)
fig2.set_title('Import/Export')
plt.plot(x6, y6,'g')

fig3=plt.subplot(4,1,3)
fig3.set_title('Battery Ch/Dis') 
plt.plot(x4, y4)

fig4=plt.subplot(4,1,4)
fig4.set_title('Battery SOC') 
plt.plot(x5, y5)

plt.tight_layout()
plt.savefig('Results_0.png')

print(results)


plt.show()
  
print(results)
print()
print("PV generation potential:",sum(PV.values()))
print("PV utilized potential:",sum(y3[m] for m in model.answers))
print("Total import/export:",sum(y7))
