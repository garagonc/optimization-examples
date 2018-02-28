# -*- coding: utf-8 -*-
"""
Created on Wed Feb 28 11:39:25 2018

@author: guemruekcue
"""

from pyomo.environ import *
from pyomo.opt import SolverFactory
import matplotlib.pylab as plt
import csv

# Create a solver
opt= SolverFactory("bonmin", executable="C:/cygwin/home/bonmin/Bonmin-1.8.6/build/bin/bonmin")

print("#################################################")
print("Starting the optimizer")
print("#################################################")

daylong=60*60*24
dT_min=60       #time step length in minutes
dT=dT_min*60    #time step length in seconds
N=int(daylong/dT)   #Number of time steps

#%%
file = open("C:/Users/guemruekcue/internship/optimization-agent/profiles/load_profile_1.txt", 'r')
lines = file.read().splitlines()
keys=range(len(lines))

pdem = []
for i in keys:
    pdem.append(float(lines[i]))
Pdem=[]
for ts in range(N):
    Pdem.append(sum(pdem[ts*dT_min:(ts+1)*dT_min])/dT_min)      #Takes the average of the range
    
file = open("C:/Users/guemruekcue/internship/optimization-agent/profiles/PV_profile3.txt", 'r')
linesPV = file.read().splitlines()
keysPV=range(len(linesPV))
pv = []
for i in keysPV:
    pv.append(float(linesPV[i]))
PV=[]
for ts in range(N):
    PV.append(sum(pdem[ts*dT_min:(ts+1)*dT_min])/dT_min)


priceImp=[];
with open("Prices.csv") as csvDataFile:
    csvReader = csv.reader(csvDataFile)
    for row in csvReader:
        priceImp=priceImp+[float(row[8])]*int(60/dT_min)

priceExp=[20]*N           #A uniformal feed-in tariff

#%%
Eff_Charging=0.9
Eff_Discharging= 0.7
Capacity=9.6*3600   #kWs


model = ConcreteModel()
model.horizon=RangeSet(0,N-1)
model.lengthSoC=RangeSet(0,N)

model.PBAT_CH= Var(model.horizon,bounds=(0,5.6),initialize=0)    
model.PBAT_DIS=Var(model.horizon, bounds=(0,5.6),initialize=0)    
model.PGRID_EXP= Var(model.horizon,bounds=(0,5.6),initialize=0)    
model.PGRID_IMP=Var(model.horizon, bounds=(0,5.6),initialize=0)    

model.s1ch=Var(model.horizon,within=Binary)
model.s2dis=Var(model.horizon,within=Binary)
model.g1exp=Var(model.horizon,within=Binary)
model.g2imp=Var(model.horizon,within=Binary)

model.SoC=Var(model.lengthSoC,bounds=(0.20,0.95))
model.PVmod=Var(model.horizon,bounds=(0,1),initialize=1)


#%%
print("#################################################")
print("Objective functions")
print("#################################################")      
def obj_rule1(model):   #Minimum grid exchange
    return sum(model.g1exp[m]*model.PGRID_EXP[m]+ model.g2imp[m]*model.PGRID_IMP[m] for m in model.horizon)
def obj_rule2(model):   #Maximum PV utilization
    return sum(model.PVmod[m]*PV[m] for m in model.horizon)
def obj_rule3(model):   #Minimum power bill
    return sum(-model.g1exp[m]*model.PGRID_EXP[m]*priceExp[m]+ model.g2imp[m]*model.PGRID_IMP[m]*priceImp[m] for m in model.horizon)
model.obj=Objective(rule=obj_rule3)

#%%
print("#################################################")
print("Constraints")
print("#################################################")
    
def con_rule2(model,m):
    return Pdem[m]==model.PVmod[m]*PV[m] -model.s1ch[m]*model.PBAT_CH[m]+ model.s2dis[m]*model.PBAT_DIS[m] -model.g1exp[m]*model.PGRID_EXP[m]+ model.g2imp[m]*model.PGRID_IMP[m]
model.con2=Constraint(model.horizon,rule=con_rule2)

def con_rule3(model,m):
    return model.SoC[m+1]==model.SoC[m]+ (model.s1ch[m]*model.PBAT_CH[m]*Eff_Charging-model.s2dis[m]*model.PBAT_DIS[m]/Eff_Discharging)*dT/Capacity 
model.con3=Constraint(model.horizon,rule=con_rule3)

def con_rule4(model,m):
    return model.s1ch[m]+model.s2dis[m]==1
model.con4=Constraint(model.horizon,rule=con_rule4)

def con_rule5(model,m):
    return model.g1exp[m]+model.g2imp[m]==1
model.con5=Constraint(model.horizon,rule=con_rule5)

def con_rule6(model):
    return model.SoC[0]==0.35
model.con6=Constraint(rule=con_rule6)

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

lists = sorted(Pdem.items()) 
x, y1 = zip(*lists)

listsPV = sorted(PV.items())
x, y2 = zip(*listsPV)

##################BATTERY##################    
listsSOC= sorted(model.SoC.items()) 
x, y = zip(*listsSOC) 
ySOC=[]
for value in y:
    ySOC.append(value.value)

listsPBatCh = sorted(model.PBAT_CH.items()) 
listsswitchCh = sorted(model.s1ch.items()) 
listsPBatDis = sorted(model.PBAT_DIS.items())
listsswitchDis = sorted(model.s2dis.items())  
yCh=[]
yCh_s1=[]
yDis=[]
yDis_s2=[]

x, y = zip(*listsPBatCh)
for value in y:
    yCh.append(value.value)
x, y = zip(*listsswitchCh)
for value in y:
    yCh_s1.append(value.value)
x, y = zip(*listsPBatDis)
for value in y:
    yDis.append(value.value)
x, y = zip(*listsswitchDis)
for value in y:
    yDis_s2.append(value.value)
lenlist=len(yDis_s2)

pBat=[]
for ts in range(lenlist):
    pBat.append(-yCh_s1[ts]*yCh[ts]+yDis_s2[ts]*yDis[ts])
##########################################


##################GRIDEXCHANGE############   
listsPGridExp = sorted(model.PGRID_EXP.items()) 
listsswitchExp = sorted(model.g1exp.items()) 
listsPGridImp = sorted(model.PGRID_IMP.items())
listsswitchImp = sorted(model.g2imp.items())  
yEx=[]
yEx_g1=[]
yImp=[]
yImp_g2=[]

x, y = zip(*listsPGridExp)
for value in y:
    yEx.append(value.value)
x, y = zip(*listsswitchExp)
for value in y:
    yEx_g1.append(value.value)
x, y = zip(*listsPGridImp)
for value in y:
    yImp.append(value.value)
x, y = zip(*listsswitchImp)
for value in y:
    yImp_g2.append(value.value)
lenlist=len(yDis_s2)

pGrid=[]
for ts in range(lenlist):
    pGrid.append(-yEx_g1[ts]*yEx[ts]+yImp_g2[ts]*yImp[ts])
##########################################
    
    
fig1=plt.subplot(4,1,1)
fig1.set_title('Power Summary')
plt.plot(x, y1[0:lenlist],label='Demand')
plt.plot(x, y2[0:lenlist],label='PV')
plt.legend()

fig2=plt.subplot(4,1,2)
fig2.set_ylim([-3,3])
fig2.set_title('Import/Export')
plt.plot(x, pGrid,'g')

fig3=plt.subplot(4,1,3)
fig3.set_ylim([-3,3])
fig3.set_title('Battery Ch/Dis') 
plt.plot(x, pBat)


fig4=plt.subplot(4,1,4)
fig4.set_title('Battery SOC')
fig4.set_ylim([0.15,0.95])
plt.plot(x, ySOC[0:lenlist])
plt.tight_layout()
plt.savefig('MinimumGridInteraction.png')

print(results)
""""""



