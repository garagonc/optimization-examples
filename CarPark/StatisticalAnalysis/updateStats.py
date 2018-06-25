# -*- coding: utf-8 -*-
"""
Created on Fri Jun  8 16:40:39 2018

@author: guemruekcue
"""

from analysispy import stats,samples,markov
import pandas as pd
from itertools import product

#%%
def rewrite(hour,numberofdrivingcar):
    nexthourstats={}
    
    #Next time step
    for drivingcar in range(9):
        nexthourstats[0,drivingcar]=markov[hour,numberofdrivingcar-drivingcar]

    #Following time steps
    for t in range(1,24):
        
        markovtime=t+hour if t+hour<24 else t+hour-24
        
        for fin_state in range(9):         
            nexthourstats[t,fin_state]=sum(nexthourstats[t-1,ini_state]*markov[markovtime,ini_state-fin_state] for ini_state in range(9))
     
    return nexthourstats

ti_00=stats
#%%
ti_01=rewrite(1,0)
ti_02=rewrite(2,0)
ti_03=rewrite(3,0)
ti_04=rewrite(4,1)
