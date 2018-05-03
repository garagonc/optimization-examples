# -*- coding: utf-8 -*-
"""
Created on Tue Apr 17 15:22:05 2018

@author: guemruekcue
"""


from subprocess import call
from scenarioConstructer import *


P_Grid_Output  =[]
P_PV_Output    =[]
P_ESS_Output   =[]
P_EV_ChargeAway=[]
P_EV_ChargeHome=[]


def solve_stochastic_programming(timestep,SoC_ESS,SoC_EV,Position_EV=True):
    construct_scenario(timestep,SoC_ESS,SoC_EV)
    command1='runph --model-directory=model_ev_home --instance-directory=nodedata'+str(timestep)+' --default-rho=1 --solver=ipopt --solution-writer=pyomo.pysp.plugins.csvsolutionwriter'
    command2='runph --model-directory=model_ev_away --instance-directory=nodedata'+str(timestep)+' --default-rho=1 --solver=ipopt --solution-writer=pyomo.pysp.plugins.csvsolutionwriter'
    if Position_EV==True:
        call(command1)
    else:
        call(command2)
    
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
    
    return new_SoC_ESS,new_SoC_EV
    
    
#%%
ess0,ev0=0.40,0.50
ess1,ev1=solve_stochastic_programming(0,ess0,ev0)
ess2,ev2=solve_stochastic_programming(1,ess1,ev1)







    