# -*- coding: utf-8 -*-
"""
Created on Wed Feb 28 16:34:40 2018

@author: guemruekcue
"""
from Scenario import *

print("#################################################")
print("PV Utilization")
print("#################################################")

#%%
model = ConcreteModel()
model.horizon=RangeSet(0,N-1)
model.lengthSoC=RangeSet(0,N)

model.PBAT= Var(model.horizon,bounds=(-6.4,6.4),initialize=0)      
model.PGRID_EXP= Var(model.horizon,bounds=(0,7.8),initialize=0)    
model.PGRID_IMP=Var(model.horizon, bounds=(0,7.8),initialize=0)    

model.g1exp=Var(model.horizon,within=Binary)
model.g2imp=Var(model.horizon,within=Binary)

model.SoC=Var(model.lengthSoC,bounds=(0.20,0.95))
model.PVmod=Var(model.horizon,bounds=(0,1),initialize=1)



#%%
#Objective
########################################################   
def obj_rule1(model):   #Minimum grid exchange
    return sum(model.g1exp[m]*model.PGRID_EXP[m]+ model.g2imp[m]*model.PGRID_IMP[m] for m in model.horizon)
def obj_rule2(model):   #Maximum PV utilization
    return sum((1-model.PVmod[m])*PV[m] for m in model.horizon)
def obj_rule3(model):   #Minimum power bill
    return sum(-model.g1exp[m]*model.PGRID_EXP[m]*priceExp[m]+ model.g2imp[m]*model.PGRID_IMP[m]*priceImp[m] for m in model.horizon)
model.obj=Objective(rule=obj_rule2)

#%%
#Constraints
########################################################   
    
def con_rule2(model,m):
    return Pdem[m]==model.PVmod[m]*PV[m]+model.PBAT[m] -model.g1exp[m]*model.PGRID_EXP[m]+ model.g2imp[m]*model.PGRID_IMP[m]
model.con2=Constraint(model.horizon,rule=con_rule2)

def con_rule3(model,m):
    return model.SoC[m+1]==model.SoC[m]+ model.PBAT[m]*dT/Capacity 
model.con3=Constraint(model.horizon,rule=con_rule3)

def con_rule5(model,m):
    return model.g1exp[m]+model.g2imp[m]==1
model.con5=Constraint(model.horizon,rule=con_rule5)

def con_rule6(model):
    return model.SoC[0]==0.35
model.con6=Constraint(rule=con_rule6)

#%%
#Solution
########################################################   
results = opt.solve(model)
print(results)

#%%
if __name__ == "__main__":
    print(results)
    print("#################################################")
    print("Plots")
    print("#################################################")
    
    ##################BATTERY##################    
    listsSOC= sorted(model.SoC.items()) 
    x, y = zip(*listsSOC) 
    ySOC=[]
    for value in y:
        ySOC.append(value.value)
    
    listsPBat = sorted(model.PBAT.items()) 
    x, y = zip(*listsPBat)
    pBat=[]
    for value in y:
        pBat.append(value.value)
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
    lenlist=len(yImp_g2)
    
    pGrid=[]
    for ts in range(lenlist):
        pGrid.append(-yEx_g1[ts]*yEx[ts]+yImp_g2[ts]*yImp[ts])
    ##########################################
        
        
    fig1=plt.subplot(4,1,1)
    fig1.set_title('Power Summary')
    plt.plot(x, Pdem,label='Demand')
    plt.plot(x, PV,label='PV')
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
    plt.savefig('PVUtilization.png')



