# -*- coding: utf-8 -*-
"""
Created on Mon Apr 30 16:51:48 2018

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
import math

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
csv_file='dynamic2_MinimizeGrid.csv'
p_pv_sch=[]
q_pv_sch=[]
ess_sch=[]
p_imp_sch=[]
q_imp_sch=[]
pf_sch=[]


with open(csv_file) as f:
    for line in f:
        row=line.split(",")
        for i in range(60):
            p_pv_sch.append(float(row[0]))
            ess_sch.append(float(row[1]))
            p_imp_sch.append(float(row[2]))
            q_pv_sch.append(float(row[3]))
            q_imp_sch.append(float(row[4]))
            
            pf_sch.append(math.cos(math.atan2(float(row[3]),float(row[0]))))

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
pv_p_power_profile=[]
pv_q_power_profile=[]

dssText.Command = 'enable Storage.AtPVNode'
dssText.Command = 'enable PVSystem.PV_Menapace'
dssText.Command = 'solve mode=snap'
dssText.Command = 'Set mode = daily stepsize=1m number=1'

dssCircuit.Solution.dblHour=0.0

for i in range(1440):
    
    LoadkW=getLoadskw(dssCircuit,dssLoads,dssCktElement)
    current_value=getLoadkwNo(dssLoads,dssCktElement,54)
    controlPPV(dssText,p_pv_sch[i]/10,pf_sch[i])
    SoC_Battery=getStoredStorage(dssText)
    P_power,Q_power=getPVPower(dssPVsystems,'PV_Menapace')
    resStorage.append(controlOptimalStorage(dssText,SoC_Battery,P_power, current_value,ess_sch[i],p_pv_sch[i]))
    pv_p_power_profile.append(P_power)
    pv_q_power_profile.append(Q_power)

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
         
minGridDyn = pandas.DataFrame(list(zip(timestamp, v1, SOCProfile,load_profile,pv_p_power_profile,pv_q_power_profile,p_imp_sch,q_imp_sch)), columns=['time','Voltage','SoC','Load','P_PV','Q_PV','P_Import','Q_Import'])
        
        