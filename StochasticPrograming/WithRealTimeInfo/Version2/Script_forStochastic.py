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
PGRID2_sho=[]
PPV2_sho  =[]
PBAT2_sho =[]
PEVH2_sho =[]
PEVA2_sho =[]

PGRID2_med=[]
PPV2_med  =[]
PBAT2_med =[]
PEVH2_med =[]
PEVA2_med =[]

PGRID2_lng=[]
PPV2_lng  =[]
PBAT2_lng =[]
PEVH2_lng =[]
PEVA2_lng =[]

for t in range(3):  
    #If short commute scenario occurs
    PGRID2_sho.append(P_Grid_Output_ini[t])
    PPV2_sho.append(P_PV_Output_ini[t])
    PBAT2_sho.append(P_ESS_Output_ini[t])
    PEVH2_sho.append(P_EV_ChargeHome_ini[t])
    PEVA2_sho.append(P_EV_ChargeAway_ini[t])
    
    #If med commute scenario occurs
    PGRID2_med.append(P_Grid_Output_ini[t])
    PPV2_med.append(P_PV_Output_ini[t])
    PBAT2_med.append(P_ESS_Output_ini[t])
    PEVH2_med.append(P_EV_ChargeHome_ini[t])
    PEVA2_med.append(P_EV_ChargeAway_ini[t])
       
    #If long commute scenario occurs
    PGRID2_lng.append(P_Grid_Output_ini[t])
    PPV2_lng.append(P_PV_Output_ini[t])
    PBAT2_lng.append(P_ESS_Output_ini[t])
    PEVH2_lng.append(P_EV_ChargeHome_ini[t])
    PEVA2_lng.append(P_EV_ChargeAway_ini[t])

for t in range(3,24):  
    #If short commute scenario occurs
    PGRID2_sho.append(P_Grid_Output_sho[t])
    PPV2_sho.append(P_PV_Output_sho[t])
    PBAT2_sho.append(P_ESS_Output_sho[t])
    PEVH2_sho.append(P_EV_ChargeHome_sho[t])
    PEVA2_sho.append(P_EV_ChargeAway_sho[t])
    
    #If med commute scenario occurs
    PGRID2_med.append(P_Grid_Output_med[t])
    PPV2_med.append(P_PV_Output_med[t])
    PBAT2_med.append(P_ESS_Output_med[t])
    PEVH2_med.append(P_EV_ChargeHome_med[t])
    PEVA2_med.append(P_EV_ChargeAway_med[t])
       
    #If long commute scenario occurs
    PGRID2_lng.append(P_Grid_Output_lng[t])
    PPV2_lng.append(P_PV_Output_lng[t])
    PBAT2_lng.append(P_ESS_Output_lng[t])
    PEVH2_lng.append(P_EV_ChargeHome_lng[t])
    PEVA2_lng.append(P_EV_ChargeAway_lng[t])