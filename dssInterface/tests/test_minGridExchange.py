# -*- coding: utf-8 -*-
"""
Created on Thu Feb 22 10:24:50 2018

@author: guemruekcue
"""

import random
import win32com.client
import pandas
import matplotlib.pyplot as plt
import glob, os
from functions import *
from datetime import date, datetime, time, timedelta

##########################################################################
###########
###########################################################################
print("Program started")
engine = win32com.client.Dispatch("OpenDSSEngine.DSS")
engine.Start("0")
dssText = engine.Text
print("DSS Engine started")
dssCircuit = engine.ActiveCircuit
dssSolution = dssCircuit.Solution
dssCktElement = dssCircuit.ActiveCktElement
dssBus = dssCircuit.ActiveBus
dssMeters = dssCircuit.Meters
dssPDElement = dssCircuit.PDElements
dssLoads = dssCircuit.Loads
dssLines = dssCircuit.Lines
dssTransformers = dssCircuit.Transformers
dssGenerators=dssCircuit.Generators
dssPVsystems=dssCircuit.PVSystems
#TODO: Add energy meters


#%%
print ("Preparing compilation of main.dss")
os.chdir(r'C:/Users/guemruekcue/internship/optimization-agent')
OpenDSS_folder_path = r'C:/Users/guemruekcue/internship/optimization-agent'
filename = 'main.dss'
engine.ClearAll()
dssText.Command = "compile " + filename
print ("main.dss compiled")


#%%
#######################################################################
##########Simulation with optimal operation sense: Minimum grid exchange
#######################################################################
os.chdir(r'C:/Users/guemruekcue/internship/optimization-agent/dssInterface/tests')
script_dir = os.path.dirname(__file__)
results_dir = os.path.join(os.path.dirname(__file__), 'results/')
voltages=[]
v11=[]
v12=[]
v13=[]
load_profile=[]
timestamp=[]
the_time =  datetime.combine(date.today(), time(0, 0))
resStorage=[]
LoadkW=[]
x=0
simTime=[]

dssText.Command = 'enable Storage.AtPVNode'
dssText.Command = 'enable PVSystem.PV_Menapace'
dssText.Command = 'solve mode=snap'
dssText.Command = 'Set mode = daily stepsize=1m number=1'

dssCircuit.Solution.dblHour=0.0


dssPVsystems.Name='PV_Menapace'
print("PV System name: "+dssPVsystems.Name)
print("PV System nominal kW: "+str(dssPVsystems.kw))


#%%
print ("Electricity bill minimization")
ldsrc="C:/Users/guemruekcue/internship/optimization-agent/profiles/load_profile_10.txt"
pvsrc="C:/Users/guemruekcue/internship/optimization-agent/profiles/PV_profile3.txt"
prcsrc="C:/Users/guemruekcue/internship/optimization-agent/profiles/price_proflie_1.txt"
optimizer=SolverFactory("ipopt", executable="C:/Users/guemruekcue/Anaconda3/pkgs/ipopt-3.11.1-2/Library/bin/ipopt")
timediscritization=60

target=1
batt,pv,result=optimizeSelfConsumptionL(dssText,ldsrc,pvsrc,prcsrc,optimizer,timediscritization,target)
flow_profile=[]
#%%
print("Simulation")
num_steps=1440
flow=[]
for i in range(num_steps):
    
    if i > 0:
        LoadkW=getLoadskw(dssCircuit,dssLoads,dssCktElement)
        current_value=getLoadkwNo(dssLoads,dssCktElement,54)
        flow=getPowerIntoNo(dssLoads,dssCktElement,54) #
        controlPPV(dssText,pv[i])
        SoC_Battery=getStoredStorage(dssText)
        PV_power=getPVPower(dssPVsystems,'PV_Menapace')
        resStorage.append(controlOptimalStorage(dssText,SoC_Battery,PV_power, current_value,batt[i],pv[i]*PV_power))
    
    """
    if i==964:
        dssText.Command= 'show Powers EXP_POWERS1'
        dssText.Command= 'show Powers PVSystem.PV_MENAPACE'
        dssText.Command= 'show Variables'        
    """

    dssSolution.solve()
    load_profile.append(LoadkW)
    flow_profile.append([flow]) #
    dssCircuit.SetActiveBus('121117')
    puList = dssBus.puVmagAngle[0::2]
    voltages.append(puList)
    v11.append(puList[0])
    v12.append(puList[1])
    v13.append(puList[2])
    timestamp.append(the_time)
    the_time = the_time + timedelta(minutes=1)
#%%
saveArrayInExcel(flow_profile,results_dir,"PFlowInto_GridExchangeOptimized")
saveArrayInExcel(load_profile,results_dir,"LoadProfile_GridExchangeOptimized")
saveArrayInExcel(resStorage,results_dir,"StorageControl_GridExchangeOptimized")
dssText.Command = 'CloseDI'

print("Results are printed to GridExchangeOptimized files")

SOCProfile1=[]
PVUtil1=[]
for ts in resStorage:
    SOCProfile1.append(float(ts[1]))
    PVUtil1.append(pv[resStorage.index(ts)]*100)
    




