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

df_leave  = xl.parse("Leave")
df_arrive = xl.parse("Arrival")

# %% 
samples=dict.fromkeys(range(1,10001))
carlist=[column for column in df_arrive]

stats=dict.fromkeys((x,y) for x,y in product(range(24),range(len(carlist)+1)))
for t,n in product(range(24),range(len(carlist)+1)):
    stats[t,n]=0

# %% 
for s in range(1,10001):
    samples[s]=np.zeros(24)
    for t in range(24):
        nbdrivingcar=0
        for car in carlist:
            if t>df_leave[car][s] and t<df_arrive[car][s]:
                nbdrivingcar+=1
        samples[s][t]=nbdrivingcar
        stats[t,nbdrivingcar]+=1/10000
        
# %%
markov=dict.fromkeys(product(range(24),range(-len(carlist),len(carlist)+1)),0)

checkdict={}

for key in sorted(samples.keys()):
    sample=samples[key]
    a = np.delete(sample, 0)
    b = np.delete(sample, 23)
    c=b-a
    c=np.append(c,sample[0]-sample[23])
    checkdict[key]=c
    
    for t in range(24):
        markov[t,c[t]]+=1/10000