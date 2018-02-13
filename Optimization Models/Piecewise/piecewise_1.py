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
#Approach2

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
    
    
Ppv_dem={}
for i,value in Pdem.items():
    if Pdem[i]<=PV[i]:
        Ppv_dem[i]=Pdem[i]
    else:
        Ppv_dem[i]=PV[i]


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
#model.PVmod=Var(model.answers,bounds=(0,1),initialize=1)

model.PBAT_CH= Var(model.answers,bounds=(0.0,5.6))    #charging
model.PBAT_DIS=Var(model.answers,bounds=(0.0,5.6))    #discharging
model.PGRID_EXP=Var(model.answers,bounds=(0.0,10.0))
model.PGRID_IMP=Var(model.answers,bounds=(0.0,10.0))

model.gridAbs=Var(model.answers)  #Absolute value of the the power imported/exported to grid
#%%
PW_GRID = {}
PW_BAT={}

for idx in model.PGRID.index_set():
    PW_GRID[idx] = [-10,0,10]
    PW_BAT[idx]=[-5.6,0,5.6]
"""
def f_obj(model,t,x):
    return abs(x)
def f_load(model,t,x):
    return (x-abs(x))/2
def f_generate(model,t,x):
    return (x+abs(x))/2
"""
def f_obj(model,t,x):
    if x>=0:
        return x
    else:
        return -x

def f_load(model,t,x):
    if x>=0:
        return 0.0
    else:
        return -x
    
def f_generate(model,t,x):
    if x>=0:
        return x
    else:
        return 0.0


#%%
model.con_obj = Piecewise(model.answers,       
                  model.gridAbs,model.PGRID,
                  pw_pts=PW_GRID,
                  pw_constr_type='EQ',
                  f_rule=f_obj)#,force_pw=True)
#%%
model.con_ch = Piecewise(model.answers,       
                  model.PBAT_CH,model.PBAT,
                  pw_pts=PW_BAT,
                  pw_constr_type='EQ',
                  f_rule=f_load)#,force_pw=True)

model.con_dis = Piecewise(model.answers,       
                  model.PBAT_DIS,model.PBAT,
                  pw_pts=PW_BAT,
                  pw_constr_type='EQ',
                  f_rule=f_generate)#,force_pw=True)
#%%
model.con_exp = Piecewise(model.answers,       
                  model.PGRID_EXP,model.PGRID,
                  pw_pts=PW_GRID,
                  pw_constr_type='EQ',
                  f_rule=f_load)#,force_pw=True)

model.con_imp = Piecewise(model.answers,       
                  model.PGRID_IMP,model.PGRID,
                  pw_pts=PW_GRID,
                  pw_constr_type='EQ',
                  f_rule=f_generate)#,force_pw=True)


#%%
print("#################################################")
print("Objective function")
print("#################################################")  
model.obj = Objective(expr= summation(model.gridAbs,index=model.answers) , sense=minimize)

#%%
print("#################################################")
print("Constraints")
print("#################################################")     
def con_rule1(model,m):
    return PV[m]==Ppv_dem[m]+model.PBAT_CH[m]+model.PGRID_EXP[m]  
model.con1=Constraint(model.answers,rule=con_rule1)

def con_rule2(model,m):
    return Pdem[m]==Ppv_dem[m] + model.PBAT_DIS[m] + model.PGRID_IMP[m]
model.con2=Constraint(model.answers,rule=con_rule2)

def con_rule3(model,m):
    return model.SoC[m+1]==model.SoC[m] - model.PBAT[m]*60/Capacity
model.con3=Constraint(model.answers,rule=con_rule3)

def con_rule6(model):
    return model.SoC[0]==0.35
model.con6=Constraint(rule=con_rule6)

#%%
print("#################################################")
print("Solving")
print("#################################################")

# Create a model instance and optimize
instance=model.create()
results=opt.solve(instance)
#%%
print("#################################################")
print("Plots")
print("#################################################")

lists = sorted(Pdem.items()) 
x1, y1 = zip(*lists)

listsPV = sorted(PV.items())
x2, y2 = zip(*listsPV)
     
listsPStorageP = sorted(instance.PBAT.items()) 
listsSOC= sorted(instance.SoC.items())
listsGrid = sorted(instance.PGRID.items())
listsabsGrid = sorted(instance.gridAbs.items()) 
listsCharge = sorted(instance.PBAT_CH.items())
listsDischarge = sorted(instance.PBAT_DIS.items())
listsImport = sorted(instance.PGRID_IMP.items())
listsExport = sorted(instance.PGRID_EXP.items())  


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

x8, y = zip(*listsCharge) 
y8=[]
for value in y:
    y8.append(value.value)
    
x9, y = zip(*listsDischarge) 
y9=[]
for value in y:
    y9.append(value.value)
    
x10, y = zip(*listsImport)
y10=[]
for value in y:
    y10.append(value.value)
    
x11, y = zip(*listsExport)
y11=[]
for value in y:
    y11.append(value.value)



fig1=plt.subplot(4,1,1)
fig1.set_title('Power Summary')
plt.plot(x1, y1,label='Demand')
plt.plot(x2, y2,label='PV Potential')
#plt.plot(x3, y3,label='PV Utilized')
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
plt.savefig('Results_1.png')

print(results)

plt.show()
  
print(results)
print()
print("PV generation potential:",sum(PV.values()))
#print("PV utilized potential:",sum(y3[m] for m in model.answers))
print("Total import/export:",sum(y7))

#%%
file_total= open("TOTAL.txt", "w")
#instance.pprint(ostream=file_total)

#%%
"""
file_PBAT = open("PBAT.txt", "w")
file_PBAT_CH = open("PBAT_CH.txt", "w")
file_PBAT_DIS = open("PBAT_DIS.txt", "w")
file_PGRID = open("PGRID.txt", "w")
file_PGRID_IMP = open("PGRID_IMP.txt", "w")
file_PGRID_EXP = open("PGRID_EXP.txt", "w")

instance.PBAT.pprint(ostream=file_PBAT)
instance.PBAT_CH.pprint(ostream=file_PBAT_CH)
instance.PBAT_DIS.pprint(ostream=file_PBAT_DIS)
instance.PGRID.pprint(ostream=file_PGRID)
instance.PGRID_IMP.pprint(ostream=file_PGRID_IMP)
instance.PGRID_EXP.pprint(ostream=file_PGRID_EXP)

"""
instance.PBAT.pprint(ostream=file_total)
instance.PBAT_CH.pprint(ostream=file_total)
instance.PBAT_DIS.pprint(ostream=file_total)

