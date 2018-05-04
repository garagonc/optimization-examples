# -*- coding: utf-8 -*-
"""
Created on Tue Apr 17 15:22:05 2018

@author: guemruekcue
"""


from subprocess import call
from scenarioConstructer import *
import time
import os

P_Grid_Output  =[]
P_PV_Output    =[]
P_ESS_Output   =[]
P_EV_ChargeAway=[]
P_EV_ChargeHome=[]


def solve_stochastic_programming(timestep,SoC_ESS,SoC_EV,Position_EV=True):
    print(timestep)
    start_time=time.time()
    
    if Position_EV==True:
        construct_scenario1(timestep,SoC_ESS,SoC_EV)
        call('runph --model-directory=model_ev_home --instance-directory=nodedata_'+str(timestep)+' --default-rho=1 --solver=ipopt --solution-writer=pyomo.pysp.plugins.csvsolutionwriter')
    else:
        construct_scenario2(timestep,SoC_ESS,SoC_EV)
        call('runph --model-directory=model_ev_away --instance-directory=nodedata_'+str(timestep)+' --default-rho=1 --solver=ipopt --solution-writer=pyomo.pysp.plugins.csvsolutionwriter')
    
    csv_file = "ph.csv"
    with open(csv_file) as f:
        for line in f:
            row=line.split(",")
            if row[1]==' RootNode':
                if row[2]==' P_ESS_Output_ini':
                    P_ESS_Output.append(float(row[4]))
                    new_SoC_ESS=SoC_ESS-float(row[4])/9.6
                elif row[2]==' P_EV_ChargeAway_ini':
                    P_EV_ChargeAway.append(float(row[4]))
                elif row[2]==' P_EV_ChargeHome_ini':
                    P_EV_ChargeHome.append(float(row[4]))
                    new_SoC_EV=SoC_EV+float(row[4])/30.0
                elif row[2]==' P_Grid_Output_ini':
                    P_Grid_Output.append(float(row[4]))            
                elif row[2]==' P_PV_Output_ini':
                    P_PV_Output.append(float(row[4]))
    
    os.remove(csv_file)
    
    end_time=time.time()
    print("Execution time:",end_time-start_time,"seconds")

    return new_SoC_ESS,new_SoC_EV

#%%
ev_min=0.45    

ess0,ev0=0.40,0.30
ess1 ,ev1 =solve_stochastic_programming(0 ,ess0 ,ev0)
ess2 ,ev2 =solve_stochastic_programming(1 ,ess1 ,ev1)
ess3 ,ev3 =solve_stochastic_programming(2 ,ess2 ,ev2)
ess4 ,ev4 =solve_stochastic_programming(3 ,ess3 ,ev3)
ess5 ,ev5 =solve_stochastic_programming(4 ,ess4 ,ev4)
ess6 ,ev6 =solve_stochastic_programming(5 ,ess5 ,ev5)
ess7 ,ev7 =solve_stochastic_programming(6 ,ess6 ,ev6)
ess8 ,ev8 =solve_stochastic_programming(7 ,ess7 ,ev7)
ess9 ,ev9 =solve_stochastic_programming(8 ,ess8 ,ev8)
ess10,ev10=solve_stochastic_programming(9 ,ess9 ,ev9)
ess11,ev11=solve_stochastic_programming(10,ess10,ev10)
ess12,ev12=solve_stochastic_programming(11,ess11,ev11)
ess13,ev13=solve_stochastic_programming(12,ess12,ev12)
ess14,ev14=solve_stochastic_programming(13,ess13,ev13)
ess15,ev15=solve_stochastic_programming(14,ess14,ev14)
ess16,ev16=solve_stochastic_programming(15,ess15,ev15)
ev16=ev_min
ess17,ev17=solve_stochastic_programming(16,ess16,ev16,False)
ev17=ev_min
ess18,ev18=solve_stochastic_programming(17,ess17,ev17,False)
ev18=ev_min
ess19,ev19=solve_stochastic_programming(18,ess18,ev18,False)
ev19=ev_min
ess20,ev20=solve_stochastic_programming(19,ess19,ev19,False)
ev20=ev_min
ess21,ev21=solve_stochastic_programming(20,ess20,ev20,False)

#%%
ev21=0.35     #Net consumption of the car when away is 25% of the battery capacity
ess22,ev22=solve_stochastic_programming(21,ess21,ev21)
ess23,ev23=solve_stochastic_programming(22,ess22,ev22)




    