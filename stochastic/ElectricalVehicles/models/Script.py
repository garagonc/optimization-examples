# -*- coding: utf-8 -*-
"""
Created on Fri Mar 16 15:05:36 2018

@author: guemruekcue
"""

from pyomo.environ import SolverFactory
from ReferenceModel import model
import os
import pandas as pd

project_dir=os.path.dirname(os.path.dirname(__file__))

data_file_LDLG=project_dir+'/scenariodata/LowDemLowGenScenario.dat'
data_file_LDHG=project_dir+'/scenariodata/LowDemHighGenScenario.dat'
data_file_HDLG=project_dir+'/scenariodata/HighDemLowGenScenario.dat'
data_file_HDHG=project_dir+'/scenariodata/HighDemHighGenScenario.dat'



instance1 = model.create_instance(data_file_LDLG)
instance2= model.create_instance(data_file_LDHG)
instance3= model.create_instance(data_file_HDLG)
instance4= model.create_instance(data_file_HDHG)


opt=SolverFactory("ipopt")
results1=opt.solve(instance1)
results2=opt.solve(instance2)
results3=opt.solve(instance3)
results4=opt.solve(instance4)


def makelist(sortedlist):
    x, y = zip(*sortedlist)
    output=[]
    for value in y:
        output.append(value.value)
    return output



listsPV1=sorted(instance1.pPV.items())
listsPV2=sorted(instance2.pPV.items())   
listsPV3=sorted(instance3.pPV.items())
listsPV4=sorted(instance4.pPV.items())       

listsSOC1= sorted(instance1.SoC.items())
listsSOC2= sorted(instance2.SoC.items()) 
listsSOC3= sorted(instance3.SoC.items())
listsSOC4= sorted(instance4.SoC.items())

listsPBat1 = sorted(instance1.PBAT.items())
listsPBat2 = sorted(instance2.PBAT.items())   
listsPBat3 = sorted(instance3.PBAT.items())
listsPBat4 = sorted(instance3.PBAT.items())

listsPGrid1 = sorted(instance1.PGRID.items())
listsPGrid2 = sorted(instance2.PGRID.items())   
listsPGrid3 = sorted(instance3.PGRID.items())
listsPGrid4 = sorted(instance4.PGRID.items())

PV1=makelist(listsPV1)
PV2=makelist(listsPV2)
PV3=makelist(listsPV3)
PV4=makelist(listsPV4)

SOC1=makelist(listsSOC1)
SOC2=makelist(listsSOC2)   
SOC3=makelist(listsSOC3) 
SOC4=makelist(listsSOC4) 

PBAT1=makelist(listsPBat1)
PBAT2=makelist(listsPBat2)   
PBAT3=makelist(listsPBat3)
PBAT4=makelist(listsPBat4)

PGRID1=makelist(listsPGrid1)
PGRID2=makelist(listsPGrid2)
PGRID3=makelist(listsPGrid3)
PGRID4=makelist(listsPGrid4)

df_SOC=pd.DataFrame(list(zip(SOC1, SOC2,SOC3,SOC4)),columns=['Scenario1','Scenario2','Scenario3','Scenario4'])
df_pPV=pd.DataFrame(list(zip(PV1, PV2,PV3,PV4)),columns=['Scenario1','Scenario2','Scenario3','Scenario4'])
df_PBAT=pd.DataFrame(list(zip(PBAT1, PBAT2,PBAT3,PBAT4)),columns=['Scenario1','Scenario2','Scenario3','Scenario4'])
df_PGRID=pd.DataFrame(list(zip(PGRID1, PGRID2,PGRID3,PGRID4)),columns=['Scenario1','Scenario2','Scenario3','Scenario4'])

print("Objective function values")
print("1:",instance1.Obj())
print("2:",instance2.Obj())
print("3:",instance3.Obj())
print("4",instance4.Obj())

