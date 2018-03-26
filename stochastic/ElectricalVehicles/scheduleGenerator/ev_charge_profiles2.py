# -*- coding: utf-8 -*-
"""
Created on Mon Mar 26 11:42:28 2018

@author: guemruekcue
"""

import numpy as np
import scipy.stats
import pandas as pd

np.random.seed(0)
"""
mu_leave, sigmleave = 571.47, 203.3597
mu_arrival, sigmarrival = 1036.89172, 195.6852
mu_eleCon, sigmeleCon = 6.756456347, 4.177621543

mu_leave, sigmleave = 554.9276316, 196.4975869
mu_arrival, sigmarrival = 1056.996711, 189.5963316
mu_eleCon, sigmeleCon = 8.384973792, 5.258704604
"""
mu_leave, sigmleave = 554.511254, 196.1607447
mu_arrival, sigmarrival = 1058.491961, 189.5043257
mu_eleCon, sigmeleCon = 8.81587686, 5.935570589

S=500           #Number of samples
E_bat=30*60     #30 kWh capacity
P_bat=3.0       #3 kW charging power 

series_leave=np.random.normal(mu_leave, sigmleave,S)
series_arr=np.random.normal(mu_arrival, sigmarrival,S)
series_eleCon=np.random.normal(mu_eleCon, sigmeleCon,S)

series_soc=100-series_eleCon/30*100


N=1800 #Simulation horizon is 31 hours (till 6 a.m. next day)

lowSOC=25
highSOC=75

timebound0=14*60
timebound1=18*60
timebound2=22*60


#Case list
"""
Early_arrival   : Final trip finishes between 2-6 p.m .  -->       t_arrival< timebound0
Normal_arrival  : Final trip finishes between 6-10 p.m     --> timebound0<=t_arrival<=timebound1
Late_arrival    : Final trip finishes later than 10 p.m.   --> timebound2< t_arrival

Low_SOC         : SOC after final trip is smaller than 25% -->
Medium_SOC      : SOC after final trip is between   25-75% -->
High_SOC        : SOC after final trip is greater than 75% -->   
"""

#Charge/Discharge patterns
"""
if Early_arrival==True:
    if Low_SOC==True:
        action='Start charging now, stop at 50% SOC, Start charging at 10 p.m., stop at 100%'
    if Medium_SOC==True:
        action='Start charging at 10 p.m., stop at 100%'
    if High_SOC==True:
        action='Start discharging now, stop at 50%, Start charging at 10 p.m., stop at 100%'
if Normal_arrival==True:
    if Low_SOC==True or Medium_SOC==True:
        action='Start charging at 10 p.m., charge until 100%'
    if High_SOC==True:
        action='Start discharging now, stop at 50% or at 10 p.m., Start charging at 10 p.m., stop at 100%'
if Late_arrival==True:
    action='Charge until 100%, or 6 a.m.
"""
    

sample={}
#Calculate the schedules for each sample in the set
for s in range(S):
    #Initialize the dictionary         
    sample[s]={'t_arrival':series_arr[s],'soc':series_soc[s],'schedule':np.zeros(N)}
    
    #if Early_arrival==True
    if timebound0<sample[s]['t_arrival']<timebound1:
        
        # if Low_SOC==True
        if sample[s]['soc']<lowSOC:
            chargeEnergy1=(50.0-sample[s]['soc'])/100*E_bat
            chargePeriod1=int(chargeEnergy1/P_bat)
            op1_start=int(sample[s]['t_arrival'])+1 #op1 starts immediately
            op1_end=op1_start+chargePeriod1         #op1 finishes when 50% reached
            op1_pow=3.0                             #op1 is charging operation
            chargeEnergy2=50/100*E_bat              
            chargePeriod2=int(chargeEnergy2/P_bat)       
            op2_start=timebound2                    #op2 starts at 10 p.m.
            op2_end=op2_start+chargePeriod2         #op2 finishes when 100% reached
            op2_pow=3.0                             #op2 is charging operation
            
        # if Medium_SOC==True
        if lowSOC<=sample[s]['soc']<=highSOC:
            chargeEnergy1=0.0
            chargePeriod1=int(chargeEnergy1/P_bat)
            op1_start=int(sample[s]['t_arrival'])+1 #op1 starts immediately
            op1_end=timebound2                      #op1 finishes at 10 p.m.
            op1_pow=0.0                             #op1 is idling
            chargeEnergy2=(100.0-sample[s]['soc'])/100*E_bat              
            chargePeriod2=int(chargeEnergy2/P_bat)       
            op2_start=timebound2                    #op2 starts at 10 p.m.
            op2_end=op2_start+chargePeriod2         #op2 finishes when 100% reached
            op2_pow=3.0                             #op2 is charging operation
        
        #if High_SOC==True
        if highSOC<sample[s]['soc']:
            chargeEnergy1=(sample[s]['soc']-50.0)/100*E_bat
            chargePeriod1=int(chargeEnergy1/P_bat)
            op1_start=int(sample[s]['t_arrival'])+1 #op1 starts immediately
            op1_end=op1_start+chargePeriod1         #op1 finishes when 50% reached
            op1_pow=-3.0                            #op1 is discharging operation
            chargeEnergy2=50/100*E_bat              
            chargePeriod2=int(chargeEnergy2/P_bat)       
            op2_start=timebound2                    #op2 starts at 11 p.m.
            op2_end=op2_start+chargePeriod2         #op2 finishes when 100% reached
            op2_pow=3.0                             #op2 is charging operation
        
      
     #if normal_arrival==True
    if timebound1<=sample[s]['t_arrival']<=timebound2:
     
        #if Low_SOC==True or Medium_SOC==True
        if sample[s]['soc']<=highSOC:  
            chargeEnergy1=0.0
            chargePeriod1=int(chargeEnergy1/P_bat)
            op1_start=int(sample[s]['t_arrival'])+1 #op1 starts immediately
            op1_end=chargePeriod1                   #op1 finishes at 10 p.m.
            op1_pow=0.0                             #op1 is idling
            chargeEnergy2=(100.0-sample[s]['soc'])/100*E_bat              
            chargePeriod2=int(chargeEnergy2/P_bat)       
            op2_start=timebound2                    #op2 starts at 11 p.m.
            op2_end=op2_start+chargePeriod2         #op2 finishes when 100% reached
            op2_pow=3.0                             #op2 is charging operation
         
         #if High_SOC==True
        if highSOC<sample[s]['soc']:
            chargeEnergy1=(sample[s]['soc']-50.0)/100*E_bat
            chargePeriod1=int(chargeEnergy1/P_bat)
            op1_start=int(sample[s]['t_arrival'])+1 #op1 starts immediately
            op1_end=op1_start+chargePeriod1 if op1_start+chargePeriod1<timebound2 else timebound2 #op1 finishes when 50% reached
            op1_pow=-3.0                            #op1 is discharging operation
            chargeEnergy2=50/100*E_bat              
            chargePeriod2=int(chargeEnergy2/P_bat)       
            op2_start=timebound2                    #op2 starts at 11 p.m.
            op2_end=op2_start+chargePeriod2         #op2 finishes when 100% reached
            op2_pow=3.0                             #op2 is charging operation

    #if Late_arrival==True
    if timebound2<sample[s]['t_arrival']:
        op1_start=0
        op1_end=int(sample[s]['t_arrival'])+1
        op1_pow=0.0               
        chargeEnergy2=(100.0-sample[s]['soc'])/100*E_bat
        chargePeriod2=int(chargeEnergy2/P_bat)        
        op2_start=op1_end                          #op2 starts immediately at arrival        
        op2_end= op2_start+chargePeriod2 if op2_start+chargePeriod2<1860 else 1860 #op2 finishes either when 100% reached or at 7 a.m.
        op2_pow=3.0
            
    sample[s]['schedule'][op1_start:op1_end]=op1_pow
    sample[s]['schedule'][op2_start:op2_end]=op2_pow
                               
         
#Detects the categories into which each sample falls
early_low=[]
early_med=[]
early_high=[]
normal_low=[]
normal_med=[]
normal_high=[]
late_low=[]
late_med=[]
late_high=[]

for key in sample.keys():
    s=sample[key]  
    if s['soc']<lowSOC and timebound0<s['t_arrival']<timebound1:
        early_low.append(key)
    if lowSOC<=s['soc']<=highSOC and timebound0<s['t_arrival']<timebound1:
        early_med.append(key)    
    if s['soc']>highSOC and timebound0<s['t_arrival']<timebound1:
        early_high.append(key)      
    if s['soc']<lowSOC and timebound1<=s['t_arrival']<=timebound2:
        normal_low.append(key)
    if lowSOC<=s['soc']<=highSOC and timebound1<=s['t_arrival']<=timebound2:
        normal_med.append(key)    
    if s['soc']>highSOC and timebound1<=s['t_arrival']<=timebound2:
        normal_high.append(key)   
    if s['soc']<lowSOC and s['t_arrival']>timebound2:
        late_low.append(key)
    if lowSOC<=s['soc']<=highSOC and s['t_arrival']>timebound2:
        late_med.append(key)    
    if s['soc']>highSOC and s['t_arrival']>timebound2:
        late_high.append(key)

#One schedule from each category
df=pd.DataFrame(list(zip(sample[early_low[0]]['schedule'],
                         sample[early_med[0]]['schedule'],
                         sample[early_high[0]]['schedule'],
                         sample[normal_low[0]]['schedule'],
                         sample[normal_med[0]]['schedule'],
                         sample[normal_high[0]]['schedule'],
                         sample[late_low[0]]['schedule'],
                         sample[late_med[0]]['schedule'],
                         sample[late_high[0]]['schedule'])),
                        columns=['EarlyLow','EarlyMed','EarlyHigh',
                                 'NormalLow','NormalMed','NormalHigh',
                                 'LateLow','LateMed','LateHigh'])
     
         
         