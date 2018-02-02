# -*- coding: utf-8 -*-
"""
Created on Wed Jan 31 13:33:13 2018

@author: garagon
"""

# -*- coding: utf-8 -*-
"""
Created on Tue Jan 23 10:20:53 2018

@author: garagon
"""

# noiteration1.py

from pyomo.environ import *
from pyomo.opt import SolverFactory
import matplotlib.pylab as plt
import string



#def file_len(fname):
#    with open(fname) as f:
#        for i, l in enumerate(f):
#            pass
#    return i + 1


# Create a solver
#opt = SolverFactory('glpk',executable="C:/Users/garagon/Anaconda3/pkgs/glpk-4.63-vc14_0/Library/bin/glpsol")
#opt = SolverFactory('glpk',executable="C:/ProgramData/Anaconda3/pkgs/glpk-4.63-vc14_0/Library/bin/glpsol")
#opt= SolverFactory("ipopt", executable="C:/Users/garagon/Anaconda3/pkgs/ipopt-3.11.1-2/Library/bin/ipopt")
#opt= SolverFactory("ipopt", executable="C:/ProgramData/Anaconda3/pkgs/ipopt-3.11.1-2/Library/bin/ipopt")
opt= SolverFactory("gurobi")

# A simple model with binary variables and
# an empty constraint list.
#

print("#################################################")
print("Starting the optimizer")
print("#################################################")
price=0.3
timeInterval=1


file = open("U:/Projekte/UCC/Storage4Grid/Simulation/python/profiles/load_profile_1.txt", 'r')
lines = file.read().splitlines()
#lines=map(int, file.readlines())
keys=range(len(lines))
Pdem = {}
for i in keys:
    Pdem[keys[i]]=float(lines[i])

file = open("U:/Projekte/UCC/Storage4Grid/Simulation/python/profiles/PV_profile3.txt", 'r')
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


#print("Este es el tamano de Pdem: "+str(len(Pdem)))
#print("Este es el tamano de PV: "+str(len(PV)))







#Pdem={0:0.4, 1:0.6, 2:0.6, 3:1, 4:2, 5:1, 6:0.5, 7:3, 8:4, 9:4, 10:2}
#PV_power={0:3,1:3, 2:3, 3:3, 4:3, 5:3, 6:3, 7:1, 8:0, 9:0, 10:0}
SoC_Battery={0:35, 1:0, 2:0, 3:0, 4:0, 5:0, 6:0, 7:0, 8:0, 9:0, 10:0}
#SoC_Battery={1:35, 2: , 3: , 
N=len(Pdem)
Eff_Charging=0.9
Eff_Discharging= 0.7

SoC=PV
SoC[1440]=1
#SoC[0]=35
#print(Pdem[4],PV_power[2])
#print(sum(Pdem[i] for i in Pdem))
#print(sum(Pdem[i]*PV_power[i] for i in Pdem))

#for x in Pdem:
 #   print(x)
model = ConcreteModel()
model.lengthSoC=RangeSet(0,N)
model.answers=RangeSet(0,N-1)
model.PBAT_CH= Var(model.answers,bounds=(0,6.4))    #charging
model.PBAT_DIS=Var(model.answers, bounds=(0,6.4))    #discharging
model.PGRID_EXP=Var(model.answers, within=NonNegativeReals)
model.PGRID_IMP=Var(model.answers, within=NonNegativeReals)
model.SoC=Var(model.lengthSoC,bounds=(20,95), initialize=35)
model.s1ch=Var(model.answers,within=Binary)
model.s2dis=Var(model.answers,within=Binary)
model.g1imp=Var(model.answers,within=Binary)
model.g2exp=Var(model.answers,within=Binary)
#model.SoC_Battery=Var(model.answers, initialize=35, domain=Integers, bounds=(0,100))
#print(model.s1.bounds)
#positive power from storage means discharging
#negative power from storage means charging


#model.obj= Objective(expr= price*timeInterval*(sum(Pdem[i]+(model.s1[i]*model.x[i]-model.s2[i]*model.y[i])-PV_power[i] for i in Pdem)), sense = minimize )
#model.obj=Objective(expr=)
print("#################################################")
print("Objective function")
print("#################################################")
      
      
def obj_rule(model):
    #return (summation(Ppv_dem,index=model.answers) + summation(model.PBAT_DIS,index=model.answers)) / summation(Pdem,index=model.answers)
    #return (sum(Ppv_dem[i] for i in model.answers)+sum(model.s2dis[i]*model.PBAT_DIS[i] for i in model.answers))/sum(Pdem[i] for i in model.answers)
    return summation(model.PGRID_IMP,index=model.answers)+ summation(model.PGRID_EXP,index=model.answers)
model.obj=Objective(rule=obj_rule, sense = minimize)


print("#################################################")
print("Constraints")
print("#################################################")

def con_rule1(model,m):
    return PV[m]==Ppv_dem[m]+model.s1ch[m]*model.PBAT_CH[m]+model.g2exp[m]*model.PGRID_EXP[m]   
model.con1=Constraint(model.answers,rule=con_rule1)

def con_rule2(model,m):
    return Pdem[m]==Ppv_dem[m] + model.s2dis[m]*model.PBAT_DIS[m] + model.g1imp[m]*model.PGRID_IMP[m]
model.con2=Constraint(model.answers,rule=con_rule2)

def con_rule3(model,m):
    return model.SoC[m+1]==model.SoC[0] + Eff_Charging*model.PBAT_CH[m]*model.s1ch[m]-(1/Eff_Discharging)*model.PBAT_DIS[m]*model.s2dis[m] 
model.con3=Constraint(model.answers,rule=con_rule3)

def con_rule4(model,m):
    return model.g1imp[m]+model.g2exp[m]==1
model.con4=Constraint(model.answers,rule=con_rule4)

def con_rule5(model,m):
    return model.s1ch[m]+model.s2dis[m]==1 
model.con5=Constraint(model.answers,rule=con_rule5)
#model.con1=Constraint(expr = (SoC_Battery[i]+Eff_Charging*model.x[i]+(1/Eff_Discharging)*model.y[i] for i in Pdem) >= 20)
#model.con2=Constraint(expr = SoC_Battery[i]+Eff_Charging*model.x[i]+(1/Eff_Discharging)*model.y[i] <= 80)
#model.con3=Constraint(expr = model.s1[i]+model.s2[i]<=1)


print("#################################################")
print("Solving")
print("#################################################")

#model.limits.add(SoC_Battery <= 100)
    

#äopt = SolverFactory('glpk',executable="C:/Users/garagon/Anaconda3/pkgs/glpk-4.63-vc14_0/Library/bin/glpsol")
# Create a model instance and optimize

instance=model.create()
#model.pprint()

results = opt.solve(instance)

instance.solutions.load_from(results)
#instance.display()

#for key, value in instance.x.items():
#    print(key,value.value)

"""
listsPStorageP = sorted(instance.x.items()) # sorted by key, return a list of tuples

for key,value in listsPStorageP:
    newList[key]=value.value


for key,value in newList:
    print(key,value)

x3, y3 = zip(*listsPStorageP) # unpack a list of pairs into two tuples

for key,value in listsPStorageP:
    print(key,value)
#plt.plot(x3, y3)

  """
lists = sorted(Pdem.items()) # sorted by key, return a list of tuples
x1, y1 = zip(*lists) # unpack a list of pairs into two tuples
#plt.plot(x1, y1)

listsPV = sorted(PV.items()) # sorted by key, return a list of tuples
x2, y2 = zip(*listsPV) # unpack a list of pairs into two tuples
#plt.plot(x2, y2)

listsPV_dem = sorted(Ppv_dem.items()) # sorted by key, return a list of tuples
x3, y3 = zip(*listsPV_dem) # unpack a list of pairs into two tuples
#plt.plot(x3, y3)  
  
listsPStorageP = sorted(instance.PBAT_CH.items()) # sorted by key, return a list of tuples
x4, y = zip(*listsPStorageP) # unpack a list of pairs into two tuples
y4=[]
for value in y:
    y4.append(value.value)

#plt.plot(x4, y4)

listsPStorageN = sorted(instance.PBAT_DIS.items()) # sorted by key, return a list of tuples
x5, y = zip(*listsPStorageN) # unpack a list of pairs into two tuples
y5=[]
for value in y:
    y5.append(value.value)

#plt.plot(x5, y5)

listsS1 = sorted(instance.s1ch.items()) # sorted by key, return a list of tuples
x6, y = zip(*listsS1) # unpack a list of pairs into two tuples
y6=[]
for value in y:
    y6.append(value.value)
  
listsS2 = sorted(instance.s2dis.items()) # sorted by key, return a list of tuples
x7, y = zip(*listsS1) # unpack a list of pairs into two tuples
y7=[]
for value in y:
    y7.append(value.value)
    
listsSoC = sorted(instance.SoC.items()) # sorted by key, return a list of tuples
x8, y = zip(*listsSoC) # unpack a list of pairs into two tuples
y8=[]
for value in y:
    y8.append(value.value)
    
listsSoC = sorted(instance.g1imp.items()) # sorted by key, return a list of tuples
x9, y = zip(*listsSoC) # unpack a list of pairs into two tuples
y9=[]
for value in y:
    y9.append(value.value)
    
listsSoC = sorted(instance.g2exp.items()) # sorted by key, return a list of tuples
x10, y = zip(*listsSoC) # unpack a list of pairs into two tuples
y10=[]
for value in y:
    y10.append(value.value)

fig1=plt.subplot(3,4,1)
fig1.set_title('Demand') 
plt.plot(x1, y1)

fig2=plt.subplot(3,4,2)
fig2.set_title('PV')
plt.plot(x2, y2)

fig4=plt.subplot(3,4,3)
fig4.set_title('Storage charging') 
plt.plot(x4, y4)

fig5=plt.subplot(3,4,4)
fig5.set_title('Storage discharging')
plt.plot(x5, y5)

fig6=plt.subplot(3,4,5)
fig6.set_title('S1 Charging')
plt.plot(x6, y6)

fig7=plt.subplot(3,4,6)
fig7.set_title('S2 discharging')
plt.plot(x7, y7)

fig8=plt.subplot(3,4,7)
fig8.set_title('SoC')
plt.plot(x8, y8)

fig9=plt.subplot(3,4,8)
fig9.set_title('S1GridI')
plt.plot(x9, y9)

fig10=plt.subplot(3,4,9)
fig10.set_title('S2GridE')
plt.plot(x10, y10)

plt.show() 





  
"""
#for key, value in instance.x.iteritems():
#    print(key,value.value)
        
for key, value in instance.x.iteritems():
    print(key,value.value)
"""



