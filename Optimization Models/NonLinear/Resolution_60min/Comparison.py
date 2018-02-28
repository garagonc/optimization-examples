# -*- coding: utf-8 -*-
"""
Created on Wed Feb 28 17:30:32 2018

@author: guemruekcue
"""
from Scenario import N,dT,priceExp,priceImp,PV,Pdem
from GridInteraction import model as model1
from PVUtilization import model as model2
from BillMinimization import model as model3

import pandas
from Rainflow import *

def makelist(sortedlist):
    x, y = zip(*sortedlist)
    output=[]
    for value in y:
        output.append(value.value)
    return output

#%%
listsPV1=sorted(model1.PVmod.items())
listsPV2=sorted(model2.PVmod.items())   
listsPV3=sorted(model3.PVmod.items())       

listsSOC1= sorted(model1.SoC.items())
listsSOC2= sorted(model2.SoC.items()) 
listsSOC3= sorted(model3.SoC.items())

listsPBat1 = sorted(model1.PBAT.items())
listsPBat2 = sorted(model2.PBAT.items())   
listsPBat3 = sorted(model3.PBAT.items())

listsPGridExp1 = sorted(model1.PGRID_EXP.items())
listsPGridExp2 = sorted(model2.PGRID_EXP.items())
listsPGridExp3 = sorted(model3.PGRID_EXP.items())
 
listsswitchExp1 = sorted(model1.g1exp.items())
listsswitchExp2 = sorted(model2.g1exp.items()) 
listsswitchExp3 = sorted(model3.g1exp.items()) 
 
listsPGridImp1 = sorted(model1.PGRID_IMP.items())
listsPGridImp2 = sorted(model2.PGRID_IMP.items())
listsPGridImp3 = sorted(model3.PGRID_IMP.items())

listsswitchImp1 = sorted(model1.g2imp.items())
listsswitchImp2 = sorted(model2.g2imp.items())    
listsswitchImp3 = sorted(model3.g2imp.items())

PV1=makelist(listsPV1)
PV2=makelist(listsPV2)
PV3=makelist(listsPV3)

SOC1=makelist(listsSOC1)
SOC2=makelist(listsSOC2)   
SOC3=makelist(listsSOC3) 

PBAT1=makelist(listsPBat1)
PBAT2=makelist(listsPBat2)   
PBAT3=makelist(listsPBat3)

ex1=makelist(listsPGridExp1)
ex2=makelist(listsPGridExp2)   
ex3=makelist(listsPGridExp3)
sw_ex1=makelist(listsswitchExp1)
sw_ex2=makelist(listsswitchExp2)
sw_ex3=makelist(listsswitchExp3)

im1=makelist(listsPGridImp1)
im2=makelist(listsPGridImp2)   
im3=makelist(listsPGridImp3)
sw_im1=makelist(listsswitchImp1)
sw_im2=makelist(listsswitchImp2)
sw_im3=makelist(listsswitchImp3)

PGRID1=[]
PGRID2=[]
PGRID3=[]
for ts in range(N):
    PGRID1.append(-sw_ex1[ts]*ex1[ts]+sw_im1[ts]*im1[ts])
    PGRID2.append(-sw_ex2[ts]*ex2[ts]+sw_im2[ts]*im2[ts])
    PGRID3.append(-sw_ex3[ts]*ex3[ts]+sw_im3[ts]*im3[ts])
    
#%%    
timestamp=range(0,N)
import1=sum(PGRID1[m] for m in timestamp if PGRID1[m]>0)*dT/3600
import2=sum(PGRID2[m] for m in timestamp if PGRID2[m]>0)*dT/3600
import3=sum(PGRID3[m] for m in timestamp if PGRID3[m]>0)*dT/3600   
export1=sum(PGRID1[m] for m in timestamp if PGRID1[m]<0)*dT/3600  
export2=sum(PGRID2[m] for m in timestamp if PGRID2[m]<0)*dT/3600
export3=sum(PGRID3[m] for m in timestamp if PGRID3[m]<0)*dT/3600      

pvPot=sum(PV[m] for m in timestamp)*dT/3600
pvRate1=sum(PV1[m]*PV[m] for m in timestamp)*dT/3600
pvRate2=sum(PV2[m]*PV[m] for m in timestamp)*dT/3600
pvRate3=sum(PV3[m]*PV[m] for m in timestamp)*dT/3600

bill1=sum(-sw_ex1[m]*ex1[m]*priceExp[m]+sw_im1[m]*im3[m]*priceImp[m] for m in timestamp)*dT/3600/1000
bill2=sum(-sw_ex2[m]*ex2[m]*priceExp[m]+sw_im2[m]*im2[m]*priceImp[m] for m in timestamp)*dT/3600/1000
bill3=sum(-sw_ex3[m]*ex3[m]*priceExp[m]+sw_im3[m]*im3[m]*priceImp[m] for m in timestamp)*dT/3600/1000


df_SOC=pandas.DataFrame(list(zip(timestamp, SOC1, SOC2,SOC3)),
                        columns=['time','Model1','Model2','Model3'])


#Empirical parameters to determine rated cycle-life at different DoD ranges
#Example chosen such that 4000 clycle lifetime at 80% DoD 
A=2873.1
B=-1.483

#Rainflow counting: a list of tuples that contain load ranges and the corresponding number of cycles
rf1=count_cycles(SOC1)
rf2=count_cycles(SOC2)
rf3=count_cycles(SOC3)

#Degradation of life-cycle
D_CL1=sum(pair[1]/(A*pow(pair[0],B)) for pair in rf1)
D_CL2=sum(pair[1]/(A*pow(pair[0],B)) for pair in rf2)
D_CL3=sum(pair[1]/(A*pow(pair[0],B)) for pair in rf3)
                      

print("Total Pv potential       :",pvPot,"kWh")

print("Objective                :    Import    :    Export     :   PV_Uti   :     Bill  :")
print("-------------------------:--------------:---------------:------------:-----------:")
print("Model1                   :   %3f   :   %3f   :   %6.2f   :   %3f   :" % (import1,-export1,pvRate1/pvPot*100,bill1))
print("Model2                   :   %3f   :   %3f   :   %6.2f   :   %3f   :" % (import2,-export2,pvRate2/pvPot*100,bill2))
print("Model3                   :   %3f   :   %3f   :   %6.2f   :   %3f   :" % (import3,-export3,pvRate3/pvPot*100,bill3))
print()
print("Degradation 1:",D_CL1*365*100)
print("Degradation 2:",D_CL2*365*100)
print("Degradation 3:",D_CL3*365*100)