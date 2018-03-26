# -*- coding: utf-8 -*-
"""
Created on Mon Mar 26 15:05:26 2018

@author: guemruekcue
"""

from ev_charge_profiles2 import df
import numpy as np


for scenario in df.columns:   
    filename='Scenario_'+scenario+'.txt'
    with open(filename,'w') as file:
        len60=np.array(np.split(df[scenario].values[0:1440],24))
        for i in range(24):
            file.write(str(i)+'     '+str(np.mean(len60[i])))
            file.write('\n')
        file.write(';')
    file.close()
    