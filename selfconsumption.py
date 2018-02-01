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
opt= SolverFactory("ipopt", executable="C:/ProgramData/Anaconda3/pkgs/ipopt-3.11.1-2/Library/bin/ipopt")

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

lists = sorted(Pdem.items()) # sorted by key, return a list of tuples
x1, y1 = zip(*lists) # unpack a list of pairs into two tuples
plt.plot(x1, y1)

listsPV = sorted(PV.items()) # sorted by key, return a list of tuples
x2, y2 = zip(*listsPV) # unpack a list of pairs into two tuples
plt.plot(x2, y2)

listsPV_dem = sorted(Ppv_dem.items()) # sorted by key, return a list of tuples
x3, y3 = zip(*listsPV_dem) # unpack a list of pairs into two tuples
plt.plot(x3, y3)





#Pdem={0:0.4, 1:0.6, 2:0.6, 3:1, 4:2, 5:1, 6:0.5, 7:3, 8:4, 9:4, 10:2}
#PV_power={0:3,1:3, 2:3, 3:3, 4:3, 5:3, 6:3, 7:1, 8:0, 9:0, 10:0}
SoC_Battery={0:35, 1:0, 2:0, 3:0, 4:0, 5:0, 6:0, 7:0, 8:0, 9:0, 10:0}
#SoC_Battery={1:35, 2: , 3: , 
N=len(Pdem)
Eff_Charging=0.9
Eff_Discharging= 0.7
SoC=20
#print(Pdem[4],PV_power[2])
#print(sum(Pdem[i] for i in Pdem))
#print(sum(Pdem[i]*PV_power[i] for i in Pdem))

#for x in Pdem:
 #   print(x)
model = ConcreteModel()
model.answers=range(N)
model.PBAT_CH= Var(model.answers,bounds=(0,5.6))    #charging
model.PBAT_DIS=Var(model.answers, bounds=(0,5.6))    #discharging
model.PGRID_EXP=Var(model.answers)
model.PGRID_IMP=Var(model.answers)
model.s1ch=Var(model.answers,within=Binary)
model.s2dis=Var(model.answers,within=Binary)
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
    return (sum(Ppv_dem[i] for i in model.answers)+sum(model.s2dis[i]*model.PBAT_DIS[i] for i in model.answers))/sum(Pdem[i] for i in model.answers)
    #return price*timeInterval*(sum(Pdem[i]+model.x[i]-model.y[i]-PV_power[i] for i in Pdem))
model.obj=Objective(rule=obj_rule, sense = maximize)

#model.obj= Objective(expr= price*timeInterval*(sum(Pdem[i]+(model.s1[i]*model.x[i]-model.s2[i]*model.y[i])-PV_power[i] for i in Pdem)), sense = minimize )

print("#################################################")
print("Constraints")
print("#################################################")
#model.limits=ConstraintList()
#model.con1=Constraint()
#def con_rule(model, m):

#    return sum(a[i,m]*model.x[i] for i in N) >= b[m]
#model.con5 = Constraint(model.SoC_Battery, rule=con_rule)

     
#def con_rule1(model,m):
#    return SoC + Eff_Charging*sum(model.x[m]*model.s1[m])-(1/Eff_Discharging)*model.y[m]*model.s2[m] >= 20
#model.con1=Constraint(model.answers,rule=con_rule1)

def con_rule1(model,m):
    return PV[m]-Ppv_dem[m]-model.s1ch[m]*model.PBAT_CH[m]-model.PGRID_EXP[m] == 0   
model.con1=Constraint(model.answers,rule=con_rule1)

def con_rule2(model,m):
    return Pdem[m]==Ppv_dem[m] + model.s2dis[m]*model.PBAT_DIS[m] + model.PGRID_EXP[m]
model.con2=Constraint(model.answers,rule=con_rule2)

def con_rule3(model,m):
    return model.s1ch[m]*model.PBAT_CH[m] == 0.6 + model.s2dis[m]*model.PBAT_DIS[m] 
model.con3=Constraint(model.answers,rule=con_rule3)
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
listsPStorageP = sorted(instance.PBAT_CH.items()) # sorted by key, return a list of tuples
x4, y = zip(*listsPStorageP) # unpack a list of pairs into two tuples
y4=[]
for value in y:
    y4.append(value.value)

#plt.plot(x4, y4)

listsPStorageN = sorted(instance.PBAT_CH.items()) # sorted by key, return a list of tuples
x5, y = zip(*listsPStorageN) # unpack a list of pairs into two tuples
y5=[]
for value in y:
    y5.append(value.value)

plt.plot(x5, y5)

plt.show() 
  
"""
#for key, value in instance.x.iteritems():
#    print(key,value.value)
        
for key, value in instance.x.iteritems():
    print(key,value.value)
"""



