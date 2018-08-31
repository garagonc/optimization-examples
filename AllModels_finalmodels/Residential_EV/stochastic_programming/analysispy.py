# -*- coding: utf-8 -*-
"""
Created on Wed May 23 15:56:58 2018

@author: guemruekcue
"""

import pandas as pd
import numpy as np
from itertools import product
import os


os.chdir(os.path.dirname(__file__))

xl = pd.ExcelFile("MCS.xlsx")
df_LA  = xl.parse("L_A")

xl2= pd.ExcelFile("forSP.xlsx")
df_r1= xl2.parse("Realization1")
df_r2= xl2.parse("Realization2")
df_r3= xl2.parse("Realization3")
df_re= xl2.parse("Real")
df_redr_r1= xl2.parse("Realization1_drive")
df_de= xl2.parse("Deterministic")

# %% 
samples=dict.fromkeys(range(1,10001))
tuples=dict.fromkeys(range(1,10001))

statkeys=[(t,p) for t,p in product(range(24),range(2))]
stats={}
for each in statkeys:
    stats[each]=0

markovkeys=[(t,s1,s2) for t,s1,s2 in product(range(24),range(2),range(2))]
markov={}
for each in markovkeys:
    markov[each]=0

for s in samples.keys():
    samples[s]=np.ones(24)

for s in range(1,10001):
    tuples[s]=(df_LA['Leave'][s],df_LA['Arrival'][s])
    for t in range(24):
        if int(df_LA['Leave'][s])<t<int(df_LA['Arrival'][s])+1:
            samples[s][t]=0     #driving
            stats[t,0]+=1/10000
        else:
            stats[t,1]+=1/10000
        
        if t<int(df_LA['Leave'][s]):
            markov[t,1,1]+=1/10000
        elif t==int(df_LA['Leave'][s]):
            markov[t,1,0]+=1/10000
        elif df_LA['Leave'][s]<t<df_LA['Arrival'][s]:
            markov[t,0,0]+=1/10000
        elif t==int(df_LA['Arrival'][s])+1:
            markov[t,1,0]+=1/10000
        elif t>int(df_LA['Arrival'][s])+1:
            markov[t,1,1]+=1/10000

#for hour in range(24):
# %%
ScenariosOfRealization1=dict.fromkeys(range(24))
#ScenariosOfRealization2=dict.fromkeys(range(24))
#ScenariosOfRealization3=dict.fromkeys(range(24))
ScenarioProbabilitiesforRealization1=dict.fromkeys(range(24))
#ScenarioProbabilitiesforRealization2=dict.fromkeys(range(24))
#ScenarioProbabilitiesforRealization3=dict.fromkeys(range(24))
DrivesOfRealization1=dict.fromkeys(range(24))

realization1=df_re['Realization1']
#realization2=df_re['Realization2']
#realization3=df_re['Realization3']

   
def calculate_prob(hour,scenario,firstPosition,statistics):
    #print(scenario) 
    
    probability=1   
    for t in range(hour,24):
        position=int(scenario[t+1])
        probability*=statistics[t,position]    
    
    return probability


# %%
for hour in range(23):
    #print("Hour")
    R1_scenario1=df_r1.iloc[4*hour+0]
    R1_scenario2=df_r1.iloc[4*hour+1]
    R1_scenario3=df_r1.iloc[4*hour+2]    
    
    R1_drive1=df_redr_r1.iloc[4*hour+0]
    R1_drive2=df_redr_r1.iloc[4*hour+1]
    R1_drive3=df_redr_r1.iloc[4*hour+2]
    
    prob_r1_s1=calculate_prob(hour,R1_scenario1,realization1[hour],stats)
    prob_r1_s2=calculate_prob(hour,R1_scenario2,realization1[hour],stats)
    prob_r1_s3=calculate_prob(hour,R1_scenario3,realization1[hour],stats)   
    summation=prob_r1_s1+prob_r1_s2+prob_r1_s3
    prob_r1_s1=round(prob_r1_s1/summation, 5)
    prob_r1_s2=round(prob_r1_s2/summation, 5)
    prob_r1_s3=round(1-prob_r1_s1-prob_r1_s2,5)
    
    
    
           
    ScenariosOfRealization1[hour]={'s1':list(R1_scenario1)[3+hour:26],'s2':list(R1_scenario2)[3+hour:26],'s3':list(R1_scenario3)[3+hour:26]}
    DrivesOfRealization1[hour]={'s1':list(R1_drive1)[3+hour:26],'s2':list(R1_drive2)[3+hour:26],'s3':list(R1_drive3)[3+hour:26]}
    ScenarioProbabilitiesforRealization1[hour]={'s1':prob_r1_s1,'s2':prob_r1_s2,'s3':prob_r1_s3}
    


