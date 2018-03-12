# -*- coding: utf-8 -*-
"""
Created on Tue Mar  6 17:08:26 2018

@author: guemruekcue
"""

from pyomo.environ import *
from pyomo.opt import SolverFactory
import matplotlib.pylab as plt
from Rainflow import *
import csv
import numpy as np
import pandas as pd

def makelist(sortedlist):
    x, y = zip(*sortedlist)
    output=[]
    for value in y:
        output.append(value.value)
    return output


########################################
########################################
#Minimum voltage drop
########################################
########################################


# Create a solver
#opt1=SolverFactory('glpk',executable="C:/Users/guemruekcue/Anaconda3/pkgs/glpk-4.63-vc14_0/Library/bin/glpsol")
opt2= SolverFactory("ipopt", executable="C:/Users/guemruekcue/Anaconda3/pkgs/ipopt-3.11.1-2/Library/bin/ipopt")
#opt3= SolverFactory("bonmin", executable="C:/cygwin/home/bonmin/Bonmin-1.8.6/build/bin/bonmin")


# A simple model with binary variables and
# an empty constraint list.
#
print("#################################################")
print("Loading the forecasts")
print("#################################################")

file_load = open("C:/Users/guemruekcue/internship/optimization-agent/profiles/load_profile_1.txt", 'r')
file_PV = open("C:/Users/guemruekcue/internship/optimization-agent/profiles/PV_profile3.txt", 'r')
linesLoad = file_load.read().splitlines()
linesPV = file_PV.read().splitlines()

if len(linesLoad)==len(linesPV):
    keys=range(len(linesPV))
    Pdem = []
    Qdem = []
    PV = []
    N=len(linesLoad)
    for i in keys:
        Pdem.append(float(linesLoad[i]))
        Qdem.append(float(linesLoad[i])*0.312)
        PV.append(float(linesPV[i]))

price=[];
with open("Prices.csv") as csvDataFile:
    csvReader = csv.reader(csvDataFile)
    for row in csvReader:
        price=price+[float(row[8])]*60    #Feb 18, 2018 data
       

#%%
N=len(Pdem)
Eff_Charging=0.9
Eff_Discharging= 0.7
Capacity=9.6*3600   #kWs

R=0.67
X=0.282
VGEN=0.4


#%%
model = ConcreteModel()
model.lengthSoC=RangeSet(0,N)
model.answers=RangeSet(0,N-1)
model.PBAT= Var(model.answers,bounds=(-5.6,5.6))        

model.PGRID=Var(model.answers,bounds=(-10.0,10.0),initialize=0)
model.QGRID=Var(model.answers,bounds=(-10.0,10.0),initialize=0)

model.Ppv=Var(model.answers,initialize=0)
model.Qpv=Var(model.answers,initialize=0)

                     
model.SoC=Var(model.lengthSoC,bounds=(0.20,0.95))
model.dV=Var(model.answers)#,bounds=(-0.2,0.2))



print("#################################################")
print("Objective function")
print("#################################################")  
def obj_rule(model):
    #return sum(model.PGRID[m]*model.PGRID[m] for m in model.answers)
    #return sum((1-model.PVmod[m])*PV[m] for m in model.answers)
    #return sum(price[m]*model.PGRID[m] for m in model.answers)
    return sum(model.dV[m]*model.dV[m] for m in model.answers)
model.obj=Objective(rule=obj_rule, sense = minimize)
print("Objective is the minimization of voltage drop")

print("#################################################")
print("Constraints")
print("#################################################")     
def con_rule_P(model,m):
    return Pdem[m]== model.Ppv[m] + model.PBAT[m] + model.PGRID[m]
model.con1=Constraint(model.answers,rule=con_rule_P)

def con_rule_Q(model,m):
    return Qdem[m]== model.Qpv[m] + model.QGRID[m]
model.con2=Constraint(model.answers,rule=con_rule_Q)

def con_rule3(model,m):
    return model.SoC[m+1]==model.SoC[m] - model.PBAT[m]*60/Capacity 
model.con3=Constraint(model.answers,rule=con_rule3)

def con_rule_PV(model,m):
    return model.Ppv[m]*model.Ppv[m]+model.Qpv[m]*model.Qpv[m] <= PV[m]*PV[m]
model.con4=Constraint(model.answers,rule=con_rule_PV)

def con_rule6(model):
    return model.SoC[0]==0.35
model.con6=Constraint(rule=con_rule6)

def con_rule7(model,m):
    return model.dV[m]==(R*model.PGRID[m]+X*model.QGRID[m])/VGEN
model.con7=Constraint(model.answers,rule=con_rule7)


print("#################################################")
print("Solving")
print("#################################################")

# Create a model model and optimize
#results1=opt1.solve(model)
results2=opt2.solve(model)
#results3=opt3.solve(model)
#%%
print("#################################################")
print("Plots")
print("#################################################")

      
listPpv=sorted(model.Ppv.items()) 
listQpv=sorted(model.Qpv.items()) 
listsPStorageP = sorted(model.PBAT.items()) 
listsSOC= sorted(model.SoC.items()) 
listsPImport = sorted(model.PGRID.items())
listsQImport = sorted(model.QGRID.items())  
listsdV= sorted(model.dV.items())


ppv=makelist(listPpv)
qpv=makelist(listQpv)
Pbat=makelist(listsPStorageP)
soc=makelist(listsSOC)
Pimp=makelist(listsPImport)
Qimp=makelist(listsQImport)
vdrop=makelist(listsdV)

x=range(len(linesPV))
ybus=[1+vdrop[m] for m in x]
    


fig1=plt.subplot(4,1,1)
fig1.set_title('Power Summary')
plt.plot(x, Pdem,label='Demand')
plt.plot(x, PV,label='PV Potential')
plt.plot(x, ppv,label='PV Utilized')
plt.legend()

fig2=plt.subplot(4,1,2)
fig2.set_title('Import')
plt.plot(x, Pimp,label='P')
plt.plot(x, Qimp,label='Q')

fig3=plt.subplot(4,1,3)
fig3.set_title('Battery Ch/Dis') 
plt.plot(x, Pbat)

fig4=plt.subplot(4,1,4)
fig4.set_title('Battery SOC') 
plt.plot(x, soc[0:len(x)])

plt.tight_layout()
plt.savefig('Results_4.png')

plt.show()



print("##############")
print("Ipopt")
print(results2)
"""
print("##############")
print()
print("PV generation potential  :",sum(PV.values())*60/3600,"kWh")
print("PV utilized potential    :",sum(y3[m]*PV[m] for m in model.answers)*60/3600,"kWh")
print("Total export             :",-sum(y6[m] for m in model.answers if y6[m]<0)*60/3600,"kWh")
print("Total import             :",sum(y6[m] for m in model.answers if y6[m]>0)*60/3600,"kWh")
#TODO: Total electricity bill paid
"""

#%%
#Rainflow counting: a list of tuples that contain load ranges and the corresponding number of cycles
rf=count_cycles(soc)

#Empirical parameters to determine rated cycle-life at different DoD ranges
#Example chosen such that 4000 clycle lifetime at 80% DoD 
A=2873.1
B=-1.483

#Degradation of life-cycle
D_CL=sum(pair[1]/(A*pow(pair[0],B)) for pair in rf)

print("Degradation of life-cycle:",D_CL)

#%%
df=pd.DataFrame(data={'BusVoltage':ybus,'importP':Pimp,'importQ':Qimp,'dem':Pdem,'PVpot':PV,'PVp':ppv,'PVq':qpv})
