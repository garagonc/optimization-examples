# -*- coding: utf-8 -*-
"""
Created on Tue Apr 17 15:22:05 2018

@author: guemruekcue
"""

from subprocess import call
call("runph --model-directory=models --instance-directory=scenariodata --default-rho=1 --solver=ipopt --solution-writer=pyomo.pysp.plugins.csvsolutionwriter")

#%%
import csv
csv_file = "ph.csv"

P_Grid_Output_ini  ={}
P_PV_Output_ini    ={}
P_ESS_Output_ini   ={}
P_EV_ChargeAway_ini={}
P_EV_ChargeHome_ini={}

P_Grid_Output_lng  ={}
P_PV_Output_lng    ={}
P_ESS_Output_lng   ={}
P_EV_ChargeAway_lng={}
P_EV_ChargeHome_lng={}

P_Grid_Output_med  ={}
P_PV_Output_med    ={}
P_ESS_Output_med   ={}
P_EV_ChargeAway_med={}
P_EV_ChargeHome_med={}

P_Grid_Output_sho  ={}
P_PV_Output_sho    ={}
P_ESS_Output_sho   ={}
P_EV_ChargeAway_sho={}
P_EV_ChargeHome_sho={}

with open(csv_file) as f:
    for line in f:
        row=line.split(",")
        if row[1]==' RootNode':
            if row[2]==' P_ESS_Output_ini':
                P_ESS_Output_ini[int(row[3])]=float(row[4])
            elif row[2]==' P_EV_ChargeAway_ini':
                P_EV_ChargeAway_ini[int(row[3])]=float(row[4])
            elif row[2]==' P_EV_ChargeHome_ini':
                P_EV_ChargeHome_ini[int(row[3])]=float(row[4])            
            elif row[2]==' P_Grid_Output_ini':
                P_Grid_Output_ini[int(row[3])]=float(row[4])            
            elif row[2]==' P_PV_Output_ini':
                P_PV_Output_ini[int(row[3])]=float(row[4])
        elif row[1]==' EarlyLeaveLongCommuteNode':
            if row[2]==' P_ESS_Output_rec':
                P_ESS_Output_lng[int(row[3])]=float(row[4])
            elif row[2]==' P_EV_ChargeAway_rec':
                P_EV_ChargeAway_lng[int(row[3])]=float(row[4])
            elif row[2]==' P_EV_ChargeHome_rec':
                P_EV_ChargeHome_lng[int(row[3])]=float(row[4])            
            elif row[2]==' P_Grid_Output_rec':
                P_Grid_Output_lng[int(row[3])]=float(row[4])            
            elif row[2]==' P_PV_Output_rec':
                P_PV_Output_lng[int(row[3])]=float(row[4])
        elif row[1]==' EarlyLeaveMedCommuteNode':
            if row[2]==' P_ESS_Output_rec':
                P_ESS_Output_med[int(row[3])]=float(row[4])
            elif row[2]==' P_EV_ChargeAway_rec':
                P_EV_ChargeAway_med[int(row[3])]=float(row[4])
            elif row[2]==' P_EV_ChargeHome_rec':
                P_EV_ChargeHome_med[int(row[3])]=float(row[4])            
            elif row[2]==' P_Grid_Output_rec':
                P_Grid_Output_med[int(row[3])]=float(row[4])            
            elif row[2]==' P_PV_Output_rec':
                P_PV_Output_med[int(row[3])]=float(row[4])
        elif row[1]==' EarlyLeaveShortCommuteNode':
            if row[2]==' P_ESS_Output_rec':
                P_ESS_Output_sho[int(row[3])]=float(row[4])
            elif row[2]==' P_EV_ChargeAway_rec':
                P_EV_ChargeAway_sho[int(row[3])]=float(row[4])
            elif row[2]==' P_EV_ChargeHome_rec':
                P_EV_ChargeHome_sho[int(row[3])]=float(row[4])            
            elif row[2]==' P_Grid_Output_rec':
                P_Grid_Output_sho[int(row[3])]=float(row[4])            
            elif row[2]==' P_PV_Output_rec':
                P_PV_Output_sho[int(row[3])]=float(row[4])        

#%%
PGRID3_sho=[]
PPV3_sho  =[]
PBAT3_sho =[]
PEVH3_sho =[]
PEVA3_sho =[]

PGRID3_med=[]
PPV3_med  =[]
PBAT3_med =[]
PEVH3_med =[]
PEVA3_med =[]

PGRID3_lng=[]
PPV3_lng  =[]
PBAT3_lng =[]
PEVH3_lng =[]
PEVA3_lng =[]

for t in range(4):  
    #If short commute scenario occurs
    PGRID3_sho.append(P_Grid_Output_ini[t])
    PPV3_sho.append(P_PV_Output_ini[t])
    PBAT3_sho.append(P_ESS_Output_ini[t])
    PEVH3_sho.append(P_EV_ChargeHome_ini[t])
    PEVA3_sho.append(P_EV_ChargeAway_ini[t])
    
    #If med commute scenario occurs
    PGRID3_med.append(P_Grid_Output_ini[t])
    PPV3_med.append(P_PV_Output_ini[t])
    PBAT3_med.append(P_ESS_Output_ini[t])
    PEVH3_med.append(P_EV_ChargeHome_ini[t])
    PEVA3_med.append(P_EV_ChargeAway_ini[t])
       
    #If long commute scenario occurs
    PGRID3_lng.append(P_Grid_Output_ini[t])
    PPV3_lng.append(P_PV_Output_ini[t])
    PBAT3_lng.append(P_ESS_Output_ini[t])
    PEVH3_lng.append(P_EV_ChargeHome_ini[t])
    PEVA3_lng.append(P_EV_ChargeAway_ini[t])

for t in range(4,24):  
    #If short commute scenario occurs
    PGRID3_sho.append(P_Grid_Output_sho[t])
    PPV3_sho.append(P_PV_Output_sho[t])
    PBAT3_sho.append(P_ESS_Output_sho[t])
    PEVH3_sho.append(P_EV_ChargeHome_sho[t])
    PEVA3_sho.append(P_EV_ChargeAway_sho[t])
    
    #If med commute scenario occurs
    PGRID3_med.append(P_Grid_Output_med[t])
    PPV3_med.append(P_PV_Output_med[t])
    PBAT3_med.append(P_ESS_Output_med[t])
    PEVH3_med.append(P_EV_ChargeHome_med[t])
    PEVA3_med.append(P_EV_ChargeAway_med[t])
       
    #If long commute scenario occurs
    PGRID3_lng.append(P_Grid_Output_lng[t])
    PPV3_lng.append(P_PV_Output_lng[t])
    PBAT3_lng.append(P_ESS_Output_lng[t])
    PEVH3_lng.append(P_EV_ChargeHome_lng[t])
    PEVA3_lng.append(P_EV_ChargeAway_lng[t])