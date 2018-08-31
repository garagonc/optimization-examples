# -*- coding: utf-8 -*-
"""
Created on Thu Jun 28 13:47:47 2018

@author: guemruekcue
"""

import win32com.client
import pandas
import matplotlib.pyplot as plt
import os
import numpy as np
from dssInterface.functions import *
from datetime import date, datetime, time, timedelta

##########################################################################
###########
###########################################################################
print("Optimization objective: Minimize power exchange with grid")
engine = win32com.client.Dispatch("OpenDSSEngine.DSS")
engine.Start("0")
dssText = engine.Text
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
#import optimization models
os.chdir(r'C:/Users/guemruekcue/internship/optimization-agent/AllModels/ESS_EV/dssInterface')
from optimization_withoutReactive.Models.woGessConn_minPowExchange_lp import schedules as schedule_woLp
from optimization_withoutReactive.Models.wGessConn1_minPowExchange_lp import schedules as schedule_wLp
from optimization_withoutReactive.Models.woGessConn_minPowExchange_dp import schedules as schedule_woDp
from optimization_withoutReactive.Models.wGessConn1_minPowExchange_dp import schedules as schedule_wDp

def simulate_a_schedule(Sch,inputMessage):
    
    os.chdir(r'C:/Users/guemruekcue/internship/optimization-agent/AllModels/ESS_EV/dssInterface')
    filename = 'main.dss'
    engine.ClearAll()
    dssText.Command = "compile " + filename
    
    print ("main.dss compiled for simulation: "+inputMessage)#LP optimized without GessConn Command
    
    dssText.Command = 'enable Storage.AtPVNode'
    dssText.Command = 'enable PVSystem.PV_Menapace'
    dssText.Command = 'solve mode=snap'
    dssText.Command = 'Set mode = daily stepsize=1m number=1'
    
    dssCircuit.Solution.dblHour=0.0
    dssPVsystems.Name='PV_Menapace'
    
    the_time =  datetime.combine(date.today(), time(0, 0))
    
    pv_p=[]
    pv_pf=[]
    ess_p=[]
    ess_q=[]
    grid_p=[]
    grid_q=[]
    load_p=[]
       
    for i in range(24):
        for sec in range(60):
            pv_p.append(Sch['p_pv'][i])
            pv_pf.append(1)
            ess_p.append(Sch['p_ess'][i])
            grid_p.append(Sch['p_grid'][i])
            grid_q.append(0.0)

    result_VoltageR=[]
    result_SOCProfile=[]
    result_PVUtil=[]
    result_load_p=[]
    result_pv_p=[]
    result_pv_q=[]
    result_ess_p=[]
    result_ess_q=[]
    result_grid_p=[]
    result_grid_q=[]

    print("Simulation")
    num_steps=1440
    for t in range(1,num_steps):
        
        #LoadkW=getLoadskw(dssCircuit,dssLoads,dssCktElement)
        current_p_load=getLoadkwNo(dssLoads,dssCktElement,54)
        controlPPV(dssText,pv_p[t]/10,0.00)
        SoC_Battery=getStoredStorage(dssText)
        P_power,Q_power=getPVPower(dssPVsystems,'PV_Menapace')
        controlOptimalStorage(dssText,ess_p[t])
    
        dssSolution.solve()
        
        dssCircuit.SetActiveBus('121117')
        #dssCircuit.SetActiveBus('123775')
        puList = dssBus.puVmagAngle[0::2]
        
        result_VoltageR.append(puList[0])    
        result_SOCProfile.append(float(SoC_Battery))
        result_load_p.append(current_p_load) 
        result_pv_p.append(P_power)
        result_pv_q.append(Q_power)
        result_ess_p.append(ess_p[t])
        result_ess_q.append(0.0)
        result_grid_p.append(grid_p[t])
        result_grid_q.append(0.0)
        
        #timestamp.append(the_time)
        the_time = the_time + timedelta(minutes=1)
        results_dataFrame=pandas.DataFrame(list(zip(result_load_p,
                                                    result_pv_p,result_pv_q,
                                                    result_ess_p,result_ess_q,
                                                    result_grid_p,result_grid_q,
                                                    result_SOCProfile,result_VoltageR)),columns=['LoadP','pvP','pvQ','essP','essQ','gridP','gridQ','SoC','Voltage'])
        
    return results_dataFrame
        
results_lp_woGessConn_obj2=simulate_a_schedule(schedule_woLp,"LP optimized without GessConn Command")
results_lp_wGessConn_obj2=simulate_a_schedule(schedule_wLp,"LP optimized with GessConn Command")
results_dp_woGessConn_obj2=simulate_a_schedule(schedule_woDp,"DP optimized without GessConn Command")
results_dp_wGessConn_obj2=simulate_a_schedule(schedule_wDp,"DP optimized with GessConn Command")

"""
PVs=pandas.DataFrame(list(zip(results_lp_woGessConn['pvP'],results_lp_wGessConn['pvP'],results_dp_woGessConn['pvP'],results_dp_wGessConn['pvP'])),columns=['lp0','lp1','dp0','dp1'])
ESSs=pandas.DataFrame(list(zip(results_lp_woGessConn['essP'],results_lp_wGessConn['essP'],results_dp_woGessConn['essP'],results_dp_wGessConn['essP'])),columns=['lp0','lp1','dp0','dp1'])
GRIDs=pandas.DataFrame(list(zip(results_lp_woGessConn['gridP'],results_lp_wGessConn['gridP'],results_dp_woGessConn['gridP'],results_dp_wGessConn['gridP'])),columns=['lp0','lp1','dp0','dp1'])
SoCs=pandas.DataFrame(list(zip(results_lp_woGessConn['SoC'],results_lp_wGessConn['SoC'],results_dp_woGessConn['SoC'],results_dp_wGessConn['SoC'])),columns=['lp0','lp1','dp0','dp1'])
Volts=pandas.DataFrame(list(zip(results_lp_woGessConn['Voltage'],results_lp_wGessConn['Voltage'],results_dp_woGessConn['Voltage'],results_dp_wGessConn['Voltage'])),columns=['lp0','lp1','dp0','dp1'])
Loads=pandas.DataFrame(list(zip(results_lp_woGessConn['LoadP'],results_lp_wGessConn['LoadP'],results_dp_woGessConn['LoadP'],results_dp_wGessConn['LoadP'])),columns=['lp0','lp1','dp0','dp1'])
"""


