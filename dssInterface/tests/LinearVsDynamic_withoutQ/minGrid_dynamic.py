# -*- coding: utf-8 -*-
"""
Created on Fri Apr 27 09:12:18 2018

@author: guemruekcue
"""

import random
import win32com.client
import pandas
import matplotlib.pyplot as plt
import glob, os
from functions import *
from datetime import date, datetime, time, timedelta
import numpy as np

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

#%%
print("Loading the schedules")
csv_file='dynamic_MinimizeGrid.csv'
pv_sch=[]
ess_sch=[]
imp_sch=[]

with open(csv_file) as f:
    for line in f:
        row=line.split(",")
        for i in range(60):
            pv_sch.append(float(row[0]))
            ess_sch.append(float(row[1]))
            imp_sch.append(float(row[2]))

#%%
print ("Preparing compilation of main.dss")
filename = 'main.dss'
engine.ClearAll()
dssText.Command = "compile " + filename
print ("main.dss compiled")

#######################################################################
##########Simulation with optimal operation sense: Min grid exchange with Lienar model
#######################################################################
voltages=[]
v1=[]
v2=[]
v3=[]
load_profile=[]
timestamp=[]
the_time =  datetime.combine(date.today(), time(0, 0))
resStorage=[]
LoadkW=[]
x=0
simTime=[]
SOCProfile=[]
pv_power_profile=[]

dssText.Command = 'enable Storage.AtPVNode'
dssText.Command = 'enable PVSystem.PV_Menapace'
dssText.Command = 'solve mode=snap'
dssText.Command = 'Set mode = daily stepsize=1m number=1'

dssCircuit.Solution.dblHour=0.0

for i in range(1440):
    
    LoadkW=getLoadskw(dssCircuit,dssLoads,dssCktElement)
    current_value=getLoadkwNo(dssLoads,dssCktElement,54)
    controlPPV(dssText,pv_sch[i]/10,1.00)
    SoC_Battery=getStoredStorage(dssText)
    P_power,Q_power=getPVPower(dssPVsystems,'PV_Menapace')
    resStorage.append(controlOptimalStorage(dssText,SoC_Battery,P_power, current_value,ess_sch[i],pv_sch[i]))
    pv_power_profile.append(P_power)

    dssSolution.solve()    
    load_profile.append(LoadkW)
    dssCircuit.SetActiveBus('121117')
    #dssCircuit.SetActiveBus('123775')
    puList = dssBus.puVmagAngle[0::2]
    voltages.append(puList)
    v1.append(puList[0])
    v2.append(puList[1])
    v3.append(puList[2])
    
    SOCProfile.append(float(SoC_Battery))
    
    timestamp.append(the_time)
    the_time = the_time + timedelta(minutes=1)
         
minGridDyn = pandas.DataFrame(list(zip(timestamp, v1, SOCProfile,load_profile,pv_power_profile,imp_sch)), columns=['time','Voltage','SoC','Load','PV','Import'])
        