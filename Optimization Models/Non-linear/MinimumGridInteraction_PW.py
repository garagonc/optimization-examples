# -*- coding: utf-8 -*-
"""
Created on Tue Feb 20 10:11:12 2018

@author: guemruekcue
"""

from pyomo.environ import *
from pyomo.core import *
from pyomo.opt import SolverFactory
import matplotlib.pylab as plt

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

#N=len(Pdem)
N=60
Eff_Charging=0.9
Eff_Discharging= 0.7
Capacity=9.6*3600   #kWs


model = ConcreteModel()
model.lengthSoC=RangeSet(0,N)
model.horizon=RangeSet(0,N-1)
model.PBAT= Var(model.horizon,bounds=(-5.6,5.6))        
#model.PGRID=Var(model.horizon,within=NonNegativeReals,initialize=0)    #Export is not allowed
model.PGRID=Var(model.horizon,initialize=0)    #Export is allowed                       
model.SoC=Var(model.lengthSoC,bounds=(0.20,0.95))
model.PVmod=Var(model.horizon,bounds=(0,1),initialize=1)

model.bateff=Var(model.horizon)

#%%
print("#################################################")
print("Objective function")
print("#################################################")      
def obj_rule(model):
    return sum(model.PGRID[m]*model.PGRID[m] for m in model.horizon)
model.obj=Objective(rule=obj_rule)

#%%
print("#################################################")
print("Constraints")
print("#################################################")
def con_rule2(model,m):
    return Pdem[m]== model.PVmod[m]*PV[m] + model.PBAT[m] + model.PGRID[m]
model.con2=Constraint(model.horizon,rule=con_rule2)

def con_rule3(model,m):
    return model.SoC[m+1]==model.SoC[m]+ model.bateff[m]*model.PBAT[m]*60/Capacity 
model.con3=Constraint(model.horizon,rule=con_rule3)

def con_rule6(model):
    return model.SoC[0]==0.35
model.con6=Constraint(rule=con_rule6)


#%%
"""
Piecewise constraint to define battery efficiency as
# A simple example illustrating a piecewise
# representation of the function Z(X)
# ndis: discharge efficiency 
# nch: charge efficiency
#
#          /  1/ndis , -5.4 <= PBAT <= 0.0
#  bateff= |
#          \  nch    ,  0.0 <= PBAT <= 5.4
#
"""

PW_BAT={}
ef_BAT={}
for idx in model.PGRID.index_set():
    PW_BAT[idx]=[-5.6,-0.28,0.,5.6]
    ef_BAT[idx]=[0.9000,0.0,0.0,1.42857]
    
def f_bat(model,t,x):
    if x>0.0000000:
        return -1/Eff_Discharging
    elif x<0.000000:
        return Eff_Charging
    else:
        return 0.000000
    
    
model.con_ch = Piecewise(model.horizon,       
              model.bateff,model.PBAT,
              pw_pts=PW_BAT,
              pw_constr_type='EQ',
              f_rule=ef_BAT)


#%%
print("#################################################")
print("Solving")
print("#################################################")

# Create a model model and optimize
results=opt.solve(model)

print("#################################################")
print("Plots")
print("#################################################")

lists = sorted(Pdem.items()) # sorted by key, return a list of tuples
x1, y1 = zip(*lists) # unpack a list of pairs into two tuples

listsPV = sorted(PV.items()) # sorted by key, return a list of tuples
x2, y2 = zip(*listsPV) # unpack a list of pairs into two tuples

listsPVutil = sorted(model.PVmod.items()) # sorted by key, return a list of tuples
x3, y = zip(*listsPVutil) # unpack a list of pairs into two tuples
y3=[]
for value in y:
    y3.append(value.value)
     
listsPStorageP = sorted(model.PBAT.items()) # sorted by key, return a list of tuples
x4, y = zip(*listsPStorageP) # unpack a list of pairs into two tuples
y4=[]
for value in y:
    y4.append(value.value)

listsSOC= sorted(model.SoC.items()) # sorted by key, return a list of tuples
x5, y = zip(*listsSOC) # unpack a list of pairs into two tuples
y5=[]
for value in y:
    y5.append(value.value)
    
listsImport = sorted(model.PGRID.items()) # sorted by key, return a list of tuples
x6, y = zip(*listsImport) # unpack a list of pairs into two tuples
y6=[]
for value in y:
    y6.append(value.value)



fig1=plt.subplot(4,1,1)
fig1.set_title('Power Summary')
plt.plot(x1, y1,label='Demand')
plt.plot(x2, y2,label='PV Potential')
plt.plot(x3, y3,label='PV Utilized')
plt.legend()

fig2=plt.subplot(4,1,2)
fig2.set_title('Import')
plt.plot(x6, y6,'g')

fig3=plt.subplot(4,1,3)
fig3.set_title('Battery Ch/Dis') 
plt.plot(x4, y4)

fig4=plt.subplot(4,1,4)
fig4.set_title('Battery SOC') 
plt.plot(x5, y5)

plt.tight_layout()
plt.savefig('Results_3.png')

plt.show()
  
print(results)
print()
print("PV generation potential:",sum(PV.values()))
print("PV utilized potential:",sum(y3[m]*PV[m] for m in model.horizon))
print("Total export:",-sum(y6[m] for m in model.horizon if y6[m]<0))
print("Total import:",sum(y6[m] for m in model.horizon if y6[m]>0))

#%%
listsbateff = sorted(model.bateff.items()) # sorted by key, return a list of tuples
x7, y = zip(*listsbateff) # unpack a list of pairs into two tuples
y7=[]
for value in y:
    y7.append(value.value)
    
file_total= open("TOTAL.txt", "w")
model.con_ch.pprint(ostream=file_total)
