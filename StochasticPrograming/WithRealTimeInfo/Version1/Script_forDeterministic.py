# -*- coding: utf-8 -*-
"""
Created on Fri Mar 16 15:05:36 2018

@author: guemruekcue
"""

from pyomo.environ import SolverFactory
from models.ReferenceModel import model
import numpy as np
import os
import pandas
#%%
#project_dir=os.path.dirname(os.path.dirname(__file__))
project_dir=os.path.dirname(__file__)

data_file1=project_dir+'/scenariodata/EarlyLeaveShortCommute.dat'
data_file2=project_dir+'/scenariodata/EarlyLeaveMedCommute.dat'
data_file3=project_dir+'/scenariodata/EarlyLeaveLongCommute.dat'


scenario1 = model.create_instance(data_file1)
scenario2 = model.create_instance(data_file2)
scenario3 = model.create_instance(data_file3)


#%%
opt=SolverFactory("ipopt")
results1=opt.solve(scenario1)
results2=opt.solve(scenario2)
results3=opt.solve(scenario3)

PV_potential_1=[scenario1.P_PV_Value]
P_Load_1=[scenario1.P_Load_Value]
EV_ParkAtHome_1=[1]
EV_ParkAway_1=[0]
P_PV_1=[scenario1.P_PV_Output_ini()]
P_Grid_1=[scenario1.P_Grid_Output_ini()]
P_EV_HomeCharge_1=[scenario1.P_EV_Charge_ini()]
P_EV_AwayCharge_1=[0.0]
P_EV_Discharge_1=[0.0]
P_ESS_1=[scenario1.P_ESS_Output_ini()]
SoC_ESS_1=[scenario1.ESS_SoC_Value()]
SoC_EV_1=[scenario1.EV_SoC_Value()]

PV_potential_2=[scenario2.P_PV_Value]
P_Load_2=[scenario2.P_Load_Value]
EV_ParkAtHome_2=[1]
EV_ParkAway_2=[0]
P_PV_2=[scenario2.P_PV_Output_ini()]
P_Grid_2=[scenario2.P_Grid_Output_ini()]
P_EV_HomeCharge_2=[scenario2.P_EV_Charge_ini()]
P_EV_AwayCharge_2=[0.0]
P_EV_Discharge_2=[0.0]
P_ESS_2=[scenario2.P_ESS_Output_ini()]
SoC_ESS_2=[scenario2.ESS_SoC_Value()]
SoC_EV_2=[scenario2.EV_SoC_Value()]

PV_potential_3=[scenario3.P_PV_Value]
P_Load_3=[scenario3.P_Load_Value]
EV_ParkAtHome_3=[1]
EV_ParkAway_3=[0]
P_PV_3=[scenario1.P_PV_Output_ini()]
P_Grid_3=[scenario1.P_Grid_Output_ini()]
P_EV_HomeCharge_3=[scenario3.P_EV_Charge_ini()]
P_EV_AwayCharge_3=[0.0]
P_EV_Discharge_3=[0.0]
P_ESS_3=[scenario3.P_ESS_Output_ini()]
SoC_ESS_3=[scenario3.ESS_SoC_Value()]
SoC_EV_3=[scenario3.EV_SoC_Value()]


# %%
for t in range(23):      
    P_Load_1.append(scenario1.P_Load_Forecast[t+1])
    P_Load_2.append(scenario2.P_Load_Forecast[t+1])
    P_Load_3.append(scenario3.P_Load_Forecast[t+1])
    
    PV_potential_1.append(scenario1.P_PV_Forecast[t+1])
    PV_potential_2.append(scenario2.P_PV_Forecast[t+1])
    PV_potential_3.append(scenario3.P_PV_Forecast[t+1])
    
    EV_ParkAtHome_1.append(scenario1.EV_ParkAtHome_Forecast[t+1])
    EV_ParkAtHome_2.append(scenario2.EV_ParkAtHome_Forecast[t+1])
    EV_ParkAtHome_3.append(scenario3.EV_ParkAtHome_Forecast[t+1])
    
    EV_ParkAway_1.append(scenario1.EV_ParkAway_Forecast[t+1])
    EV_ParkAway_2.append(scenario2.EV_ParkAway_Forecast[t+1])
    EV_ParkAway_3.append(scenario3.EV_ParkAway_Forecast[t+1])
    
    P_EV_Discharge_1.append(scenario1.P_EV_DriveDemand[t+1])
    P_EV_Discharge_2.append(scenario2.P_EV_DriveDemand[t+1])
    P_EV_Discharge_3.append(scenario3.P_EV_DriveDemand[t+1])      
    
    P_PV_1.append(scenario1.P_PV_Output[t+1]())
    P_PV_2.append(scenario2.P_PV_Output[t+1]())
    P_PV_3.append(scenario3.P_PV_Output[t+1]())
    
    P_Grid_1.append(scenario1.P_Grid_Output[t+1]())
    P_Grid_2.append(scenario2.P_Grid_Output[t+1]())
    P_Grid_3.append(scenario3.P_Grid_Output[t+1]())
    
    P_ESS_1.append(scenario1.P_ESS_Output[t+1]())
    P_ESS_2.append(scenario2.P_ESS_Output[t+1]())
    P_ESS_3.append(scenario3.P_ESS_Output[t+1]())
    
    P_EV_HomeCharge_1.append(scenario1.P_EV_Charge_AtHome[t+1]())
    P_EV_HomeCharge_2.append(scenario2.P_EV_Charge_AtHome[t+1]())
    P_EV_HomeCharge_3.append(scenario3.P_EV_Charge_AtHome[t+1]())
    
    P_EV_AwayCharge_1.append(scenario1.P_EV_Charge_Away[t+1]())
    P_EV_AwayCharge_2.append(scenario2.P_EV_Charge_Away[t+1]())
    P_EV_AwayCharge_3.append(scenario3.P_EV_Charge_Away[t+1]())
    
    SoC_ESS_1.append(scenario1.SoC_ESS[t+1]())
    SoC_ESS_2.append(scenario2.SoC_ESS[t+1]())
    SoC_ESS_3.append(scenario3.SoC_ESS[t+1]())
    
    SoC_EV_1.append(scenario1.SoC_EV[t+1]())
    SoC_EV_2.append(scenario2.SoC_EV[t+1]())
    SoC_EV_3.append(scenario3.SoC_EV[t+1]())

    

scenario1_Df=pandas.DataFrame(list(zip(EV_ParkAtHome_1,EV_ParkAway_1,P_EV_HomeCharge_1,P_EV_AwayCharge_1,P_EV_Discharge_1,SoC_EV_1)),
                        columns=['Homepark','Awaypark','EV Charge at Home','EV Charge Away','EV Discharge','EV SOC'])

scenario2_Df=pandas.DataFrame(list(zip(EV_ParkAtHome_2,EV_ParkAway_2,P_EV_HomeCharge_2,P_EV_AwayCharge_2,P_EV_Discharge_2,SoC_EV_2)),
                        columns=['Homepark','Awaypark','EV Charge at Home','EV Charge Away','EV Discharge','EV SOC'])

scenario3_Df=pandas.DataFrame(list(zip(EV_ParkAtHome_3,EV_ParkAway_3,P_EV_HomeCharge_3,P_EV_AwayCharge_3,P_EV_Discharge_3,SoC_EV_3)),
                        columns=['Homepark','Awaypark','EV Charge at Home','EV Charge Away','EV Discharge','EV SOC'])
""""""