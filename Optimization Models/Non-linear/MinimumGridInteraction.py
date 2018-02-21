# -*- coding: utf-8 -*-
"""
Created on Mon Feb 19 10:53:57 2018

@author: guemruekcue
"""


from pyomo.environ import *
from pyomo.opt import SolverFactory
import matplotlib.pylab as plt
import multiprocessing

# Create a solver
opt= SolverFactory("bonmin", executable="C:/cygwin/home/bonmin/Bonmin-1.8.6/build/bin/bonmin")

print("#################################################")
print("Starting the optimizer")
print("#################################################")
price=0.3
timeInterval=1


file = open("C:/Users/guemruekcue/internship/optimization-agent/profiles/load_profile_1.txt", 'r')
lines = file.read().splitlines()
keys=range(len(lines))
Pdem = {}
for i in keys:
    Pdem[keys[i]]=float(lines[i])*2

file = open("C:/Users/guemruekcue/internship/optimization-agent/profiles/PV_profile3.txt", 'r')
linesPV = file.read().splitlines()
keysPV=range(len(linesPV))
PV = {}
for i in keysPV:
    PV[keysPV[i]]=float(linesPV[i])


Ppv_dem={}
for i,value in Pdem.items():
    if Pdem[i]<=PV[i]:
        Ppv_dem[i]=Pdem[i]
    else:
        Ppv_dem[i]=PV[i]


#N=len(Pdem)
N=15
Eff_Charging=0.9
Eff_Discharging= 0.7
Capacity=9.6*3600   #kWs


model = ConcreteModel()
model.horizon=RangeSet(0,N-1)
model.lengthSoC=RangeSet(0,N)

model.PBAT_CH= Var(model.horizon,bounds=(0,5.6),initialize=0)    #charging
model.PBAT_DIS=Var(model.horizon, bounds=(0,5.6),initialize=0)    #discharging
model.PGRID_EXP=Var(model.horizon,within=NonNegativeReals,initialize=0)
model.PGRID_IMP=Var(model.horizon,within=NonNegativeReals,initialize=0)
model.s1ch=Var(model.horizon,within=Binary)
model.s2dis=Var(model.horizon,within=Binary)
model.g1imp=Var(model.horizon,within=Binary)
model.g2exp=Var(model.horizon,within=Binary)
model.SoC=Var(model.lengthSoC,bounds=(0.20,0.95))


#%%
print("#################################################")
print("Objective function")
print("#################################################")      
def obj_rule(model):
    return sum(model.g1imp[m]*model.PGRID_IMP[m]+model.g2exp[m]*model.PGRID_EXP[m] for m in model.horizon)
model.obj=Objective(rule=obj_rule)

#%%
print("#################################################")
print("Constraints")
print("#################################################")
    
def con_rule1(model,m):
    return PV[m]==Ppv_dem[m]+model.s1ch[m]*model.PBAT_CH[m]+model.g2exp[m]*model.PGRID_EXP[m]
model.con1=Constraint(model.horizon,rule=con_rule1)

def con_rule2(model,m):
    return Pdem[m]==Ppv_dem[m] + model.s2dis[m]*model.PBAT_DIS[m] + model.g1imp[m]*model.PGRID_IMP[m]
model.con2=Constraint(model.horizon,rule=con_rule2)

def con_rule3(model,m):
    return model.SoC[m+1]==model.SoC[m]+ (model.s1ch[m]*model.PBAT_CH[m]*Eff_Charging-model.s2dis[m]*model.PBAT_DIS[m]/Eff_Discharging)*60/Capacity 
model.con3=Constraint(model.horizon,rule=con_rule3)

def con_rule4(model,m):
    return model.s1ch[m]+model.s2dis[m]<=1
model.con4=Constraint(model.horizon,rule=con_rule4)

def con_rule5(model,m):
    return model.g1imp[m]+model.g2exp[m]<=1
model.con5=Constraint(model.horizon,rule=con_rule5)

#%%
print("#################################################")
print("Solving")
print("#################################################")
results = opt.solve(model)

print(results)

#%%
print("#################################################")
print("Plots")
print("#################################################")

lists = sorted(Pdem.items()) # sorted by key, return a list of tuples
x1, y1 = zip(*lists) # unpack a list of pairs into two tuples

listsPV = sorted(PV.items()) # sorted by key, return a list of tuples
x2, y2 = zip(*listsPV) # unpack a list of pairs into two tuples

listsPV_dem = sorted(Ppv_dem.items()) # sorted by key, return a list of tuples
x3, y3 = zip(*listsPV_dem) # unpack a list of pairs into two tuples
     
listsPBatCh = sorted(instance.PBAT_CH.items()) # sorted by key, return a list of tuples
listsPBatDis = sorted(instance.PBAT_DIS.items()) # sorted by key, return a list of tuples
x4, y = zip(*listsPBatCh) # unpack a list of pairs into two tuples
y4=[]
for value in y:
    y4.append(value.value)

listsSOC= sorted(instance.SoC.items()) # sorted by key, return a list of tuples
x5, y = zip(*listsSOC) # unpack a list of pairs into two tuples
y5=[]
for value in y:
    y5.append(value.value)
    
listsImport = sorted(instance.PGRID_IMP.items()) # sorted by key, return a list of tuples
x6, y = zip(*listsImport) # unpack a list of pairs into two tuples
y6=[]
for value in y:
    y6.append(value.value)

fig1=plt.subplot(4,1,1)
fig1.set_title('Power Summary')
plt.plot(x1, y1,label='Demand')
plt.plot(x2, y2,label='PV')
plt.legend()

fig2=plt.subplot(4,1,2)
fig2.set_ylim([-3,3])
fig2.set_title('Import/Export')
plt.plot(x6, y6,'g')

fig3=plt.subplot(4,1,3)
fig3.set_ylim([-3,3])
fig3.set_title('Battery Ch/Dis') 
plt.plot(x4, y4)


fig4=plt.subplot(4,1,4)
fig4.set_title('Battery SOC')
fig4.set_ylim([0.15,0.95])
plt.plot(x5, y5)
plt.tight_layout()
plt.savefig('MinimumGridInteraction.png')

print(results)



