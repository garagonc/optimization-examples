# -*- coding: utf-8 -*-
"""
Created on Tue Jun 26 15:37:08 2018

@author: guemruekcue
"""
import win32com.client
import pandas
import matplotlib.pyplot as plt
import os
import numpy as np
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

#%%
print ("Preparing compilation of main.dss")
os.chdir(r'C:/Users/guemruekcue/internship/optimization-agent/AllModels/ESS_EV/dssInterface')
OpenDSS_folder_path = r'C:/Users/guemruekcue/internship/optimization-agent/AllModels/ESS_EV/dssInterface'
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
v21=[]
v22=[]
v23=[]
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


#%%
ldsrc="C:/Users/guemruekcue/internship/optimization-agent/profiles/load_profile_10.txt"
pvsrc="C:/Users/guemruekcue/internship/optimization-agent/profiles/PV_profile3.txt"
prcsrc="C:/Users/guemruekcue/internship/optimization-agent/profiles/price_proflie_1.txt"

#%%
#import optimization model
os.chdir(r'C:/Users/guemruekcue/internship/optimization-agent/AllModels/ESS_EV/dssInterface')
from optimization.woGessConn_minPowImport_lp import schedules
VoltageR=[]
pv_p=[]
pv_pf=[]
ess_p=[]
grid_p=[]
grid_q=[]
load_p=[]

SOCProfile=[]
PVUtil=[]

for t in range(24):
    for sec in range(60):
        pv_p.append(schedules['p_pv'][t])
        pv_pf.append(1)
        ess_p.append(schedules['p_ess'][t])
        grid_p.append(schedules['p_grid'][t])
        grid_q.append(0.0)


#%%
print("Simulation")
num_steps=1440
for i in range(num_steps):
    
    #LoadkW=getLoadskw(dssCircuit,dssLoads,dssCktElement)
    current_p_load=getLoadkwNo(dssLoads,dssCktElement,54)
    controlPPV(dssText,pv_p[i]/10,pv_pf[i])
    SoC_Battery=getStoredStorage(dssText)
    P_power,Q_power=getPVPower(dssPVsystems,'PV_Menapace')
    resStorage.append(controlOptimalStorage(dssText,SoC_Battery,P_power, current_p_load,ess_p[i],pv_p[i]))

    dssSolution.solve()
    
    dssCircuit.SetActiveBus('121117')
    #dssCircuit.SetActiveBus('123775')
    puList = dssBus.puVmagAngle[0::2]
    VoltageR.append(puList[0])
    
    SOCProfile.append(float(SoC_Battery))
    load_p.append(current_p_load)
    #PVUtil.append(1.00 if pvpot[i]==0 else sqrt(P_power*P_power+Q_power*Q_power)/pvpot[i])
    
    timestamp.append(the_time)
    the_time = the_time + timedelta(minutes=1)








