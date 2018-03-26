# -*- coding: utf-8 -*-
"""
Created on Thu Mar 22 13:27:32 2018

@author: guemruekcue
"""

import numpy as np
import scipy.stats
import pandas as pd

np.random.seed(0)

mu_soc, sigma_soc = 3.78, 0.58209**2    # mean and standard deviation for SOC at arrivaö
mu_arr, sigma_arr = 969.8916, 234.9789  # mean and standard deviation for arrival time

S=20            #Number of samples
E_bat=30*60     #30 kWh capacity
P_bat=3.0       #3 kW charging power 

series_arr=np.random.normal(mu_arr, sigma_arr,S)

series_soc=60*np.ones(S)
for s in range(S):
    drawn_soc=np.random.lognormal(mu_soc, sigma_soc)
    if 20.0<=drawn_soc<=90.0:
        series_soc[s]=drawn_soc
    else:
        series_soc[s]=np.random.uniform(20.0,90.0)
        print('Wrong generation')

#Case list
"""
Early_arrival   : Final trip finishes earlier than 5 p.m.  -->       t_arrival< 1020
Normal_arrival  : Final trip finishes between 5-11 p.m     --> 1020<=t_arrival<=1380
Late_arrival    : Final trip finishes later than 11 p.m.   --> 1380< t_arrival

Low_SOC         : SOC after final trip is smaller than 30% -->
Medium_SOC      : SOC after final trip is between   30-70% -->
High_SOC        : SOC after final trip is greater than 70% -->   
"""

#Charge/Discharge patterns
"""
if Early_arrival==True:
    if Low_SOC==True:
        action='Start charging now, stop at 50% SOC, Start charging at 11 p.m., stop at 100%'
    if Medium_SOC==True:
        action='Start charging at 11 p.m., stop at 100%'
    if High_SOC==True:
        action='Start discharging now, stop at 50%, Start charging at 11 p.m., stop at 100%'
if Normal_arrival==True:
    if Low_SOC==True or Medium_SOC==True:
        action='Start charging at 11 p.m., charge until 100%'
    if High_SOC==True:
        action='Start discharging now, stop at 50%, Start charging at 11 p.m., stop at 100%'
if Late_arrival==True:
    action='Charge until 100%, or 7 a.m.
"""
    


N=1860 #Simulation horizon is 31 hours (till 7 a.m. next day)

sample={}
#For each sample in the set
for s in range(S):
    #Initialize the dictionary         
    sample[s]={'t_arrival':series_arr[s],'soc':series_soc[s],'schedule':np.zeros(N)}

    
    #if Early_arrival==True
    if sample[s]['t_arrival']<1020:
        
        # if Low_SOC==True
        if sample[s]['soc']<30.0:
            chargeEnergy1=(50.0-sample[s]['soc'])/100*E_bat
            chargePeriod1=int(chargeEnergy1/P_bat)
            op1_start=int(sample[s]['t_arrival'])+1 #op1 starts immediately
            op1_end=op1_start+chargePeriod1         #op1 finishes when 50% reached
            op1_pow=3.0                             #op1 is charging operation
            chargeEnergy2=50/100*E_bat              
            chargePeriod2=int(chargeEnergy2/P_bat)       
            op2_start=1380                          #op2 starts at 11 p.m.
            op2_end=op2_start+chargePeriod2         #op2 finishes when 100% reached
            op2_pow=3.0                             #op2 is charging operation
            
        # if Medium_SOC==True
        if 30.0<=sample[s]['soc']<=70.0:
            chargeEnergy1=0.0
            chargePeriod1=int(chargeEnergy1/P_bat)
            op1_start=int(sample[s]['t_arrival'])+1 #op1 starts immediately
            op1_end=1380                            #op1 finishes at 11 p.m.
            op1_pow=0.0                             #op1 is idling
            chargeEnergy2=(100.0-sample[s]['soc'])/100*E_bat              
            chargePeriod2=int(chargeEnergy2/P_bat)       
            op2_start=1380                          #op2 starts at 11 p.m.
            op2_end=op2_start+chargePeriod2         #op2 finishes when 100% reached
            op2_pow=3.0                             #op2 is charging operation
        
        #if High_SOC==True
        if 70.0<sample[s]['soc']:
            chargeEnergy1=(sample[s]['soc']-50.0)/100*E_bat
            chargePeriod1=int(chargeEnergy1/P_bat)
            op1_start=int(sample[s]['t_arrival'])+1 #op1 starts immediately
            op1_end=op1_start+chargePeriod1         #op1 finishes when 50% reached
            op1_pow=-3.0                            #op1 is discharging operation
            chargeEnergy2=50/100*E_bat              
            chargePeriod2=int(chargeEnergy2/P_bat)       
            op2_start=1380                          #op2 starts at 11 p.m.
            op2_end=op2_start+chargePeriod2         #op2 finishes when 100% reached
            op2_pow=3.0                             #op2 is charging operation
      
     #if Normal_arrival==True
    if 1020<=sample[s]['t_arrival']<=1380:
     
        #if Low_SOC==True or Medium_SOC==True
        if sample[s]['soc']<=70.0:  
            chargeEnergy1=0.0
            chargePeriod1=int(chargeEnergy1/P_bat)
            op1_start=int(sample[s]['t_arrival'])+1 #op1 starts immediately
            op1_end=1380                            #op1 finishes at 11 p.m.
            op1_pow=0.0                             #op1 is idling
            chargeEnergy2=(100.0-sample[s]['soc'])/100*E_bat              
            chargePeriod2=int(chargeEnergy2/P_bat)       
            op2_start=1380                          #op2 starts at 11 p.m.
            op2_end=op2_start+chargePeriod2         #op2 finishes when 100% reached
            op2_pow=3.0                             #op2 is charging operation
         
         #if High_SOC==True
        if 70.0<sample[s]['soc']:
            chargeEnergy1=(sample[s]['soc']-50.0)/100*E_bat
            chargePeriod1=int(chargeEnergy1/P_bat)
            op1_start=int(sample[s]['t_arrival'])+1 #op1 starts immediately
            op1_end=op1_start+chargePeriod1         #op1 finishes when 50% reached
            op1_pow=-3.0                            #op1 is discharging operation
            chargeEnergy2=50/100*E_bat              
            chargePeriod2=int(chargeEnergy2/P_bat)       
            op2_start=1380                          #op2 starts at 11 p.m.
            op2_end=op2_start+chargePeriod2         #op2 finishes when 100% reached
            op2_pow=3.0                             #op2 is charging operation
     
     #if Late_arrival==True
    if 1380<sample[s]['t_arrival']:
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
                               
         
df=pd.DataFrame(list(zip(sample[0]['schedule'],sample[1]['schedule'],sample[2]['schedule'],sample[3]['schedule'],sample[4]['schedule'])),
                        columns=['s0','s1','s2','s3','s4'])


for n in range(5):
    print('Sample',n)
    print('Arrival:',sample[n]['t_arrival'])
    print('Arrival:',sample[n]['soc'])         
         
         
         