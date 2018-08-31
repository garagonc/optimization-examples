# -*- coding: utf-8 -*-
"""
Created on Mon Jul  2 10:27:19 2018

@author: guemruekcue
"""

from Obj1_minimizeImport import *
from optimization_withoutReactive.Simulations.Obj2_minimizePowerExchange import *
from optimization_withoutReactive.Simulations.Obj3_maximizePVUtil import *
from optimization_withoutReactive.Simulations.Obj4_minimizePowerBill import *

Price_Forecast={0 :  34.61,
                1 :  33.28,
                2 :  33.03,
                3 :  32.93,
                4 :  31.96,
                5 :  33.67,
                6 :  40.45,
                7 :  47.16,
                8 :  47.68,
                9 :  46.23,
                10:  43.01,
                11:  39.86,
                12:  37.64,
                13:  37.14,
                14:  39.11,
                15:  41.91,
                16:  44.11,
                17:  48.02,
                18:  51.65,
                19:  48.73,
                20:  43.56,
                21:  38.31,
                22:  37.66,
                23:  36.31}

pricesignal=[]
for ts in range(24):
    for sec in range(60):
        pricesignal.append(Price_Forecast[ts])

#%%
from optimization_withoutReactive.Simulations.Rainflow import *
#Empirical parameters to determine rated cycle-life at different DoD ranges
#Example chosen such that 4000 clycle lifetime at 80% DoD 
A=2873.1
B=-1.483

#Rainflow counting: a list of tuples that contain load ranges and the corresponding number of cycles
rf_lp_obj1=count_cycles(results_lp_woGessConn_obj1['SoC'])
rf_dp_obj1=count_cycles(results_dp_woGessConn_obj1['SoC'])
rf_lp_obj2=count_cycles(results_lp_woGessConn_obj2['SoC'])
rf_dp_obj2=count_cycles(results_dp_woGessConn_obj2['SoC'])
rf_lp_obj3=count_cycles(results_lp_woGessConn_obj3['SoC'])
rf_dp_obj3=count_cycles(results_dp_woGessConn_obj3['SoC'])
rf_lp_obj4=count_cycles(results_lp_woGessConn_obj4['SoC'])
rf_dp_obj4=count_cycles(results_dp_woGessConn_obj4['SoC'])

#Degradation of life-cycle
D_CL_lp_obj1=sum(pair[1]/(A*pow(pair[0],B)) for pair in rf_lp_obj1)
D_CL_dp_obj1=sum(pair[1]/(A*pow(pair[0],B)) for pair in rf_dp_obj1)
D_CL_lp_obj2=sum(pair[1]/(A*pow(pair[0],B)) for pair in rf_lp_obj2)
D_CL_dp_obj2=sum(pair[1]/(A*pow(pair[0],B)) for pair in rf_dp_obj2)
D_CL_lp_obj3=sum(pair[1]/(A*pow(pair[0],B)) for pair in rf_lp_obj3)
D_CL_dp_obj3=sum(pair[1]/(A*pow(pair[0],B)) for pair in rf_dp_obj3)
D_CL_lp_obj4=sum(pair[1]/(A*pow(pair[0],B)) for pair in rf_lp_obj4)
D_CL_dp_obj4=sum(pair[1]/(A*pow(pair[0],B)) for pair in rf_dp_obj4)

        
        
        
print("-----------------------------")
print("Objective: Minimize Import")
print()

print('--LP without GesConn')
print('Import:',sum(results_lp_woGessConn_obj1['gridP'][ts] for ts in range(1439) if results_lp_woGessConn_obj1['gridP'][ts]>0)/3600)
print('Grid:',sum(abs(results_lp_woGessConn_obj1['gridP'][ts]) for ts in range(1439))/3600)
print('PV Utilization:',sum(results_lp_woGessConn_obj1['pvP'])/3347.23)
print('Bill:',sum(results_lp_woGessConn_obj1['gridP'][ts]*pricesignal[ts] for ts in range(1439))/3600/1000)
print('--DP without GesConn')
print('Import:',sum(results_dp_woGessConn_obj1['gridP'][ts] for ts in range(1439) if results_dp_woGessConn_obj1['gridP'][ts]>0)/3600)
print('Grid:',sum(abs(results_dp_woGessConn_obj1['gridP'][ts]) for ts in range(1439))/3600)
print('PV Utilization:',sum(results_dp_woGessConn_obj1['pvP'])/3347.23)
print('Bill:',sum(results_dp_woGessConn_obj1['gridP'][ts]*pricesignal[ts] for ts in range(1439))/3600/1000)
print()

print("-----------------------------")
print("Objective: Minimize Power Exchange")
print()

print('--LP without GesConn')
print('Import:',sum(results_lp_woGessConn_obj2['gridP'][ts] for ts in range(1439) if results_lp_woGessConn_obj2['gridP'][ts]>0)/3600)
print('Grid:',sum(abs(results_lp_woGessConn_obj2['gridP'][ts]) for ts in range(1439))/3600)
print('PV Utilization:',sum(results_lp_woGessConn_obj2['pvP'])/3347.23)
print('Bill:',sum(results_lp_woGessConn_obj2['gridP'][ts]*pricesignal[ts] for ts in range(1439))/3600/1000)

print('--DP without GesConn')
print('Import:',sum(results_dp_woGessConn_obj2['gridP'][ts] for ts in range(1439) if results_dp_woGessConn_obj2['gridP'][ts]>0)/3600)
print('Grid:',sum(abs(results_dp_woGessConn_obj2['gridP'][ts]) for ts in range(1439))/3600)
print('PV Utilization:',sum(results_dp_woGessConn_obj2['pvP'])/3347.23)
print('Bill:',sum(results_dp_woGessConn_obj2['gridP'][ts]*pricesignal[ts] for ts in range(1439))/3600/1000)
print()

print("-----------------------------")
print("Objective: Maximize PV")
print()

print('--LP without GesConn')
print('Import:',sum(results_lp_woGessConn_obj3['gridP'][ts] for ts in range(1439) if results_lp_woGessConn_obj3['gridP'][ts]>0)/3600)
print('Grid:',sum(abs(results_lp_woGessConn_obj3['gridP'][ts]) for ts in range(1439))/3600)
print('PV Utilization:',sum(results_lp_woGessConn_obj3['pvP'])/3347.23)
print('Bill:',sum(results_lp_woGessConn_obj3['gridP'][ts]*pricesignal[ts] for ts in range(1439))/3600/1000)

print('--DP without GesConn')
print('Import:',sum(results_dp_woGessConn_obj3['gridP'][ts] for ts in range(1439) if results_dp_woGessConn_obj3['gridP'][ts]>0)/3600)
print('Grid:',sum(abs(results_dp_woGessConn_obj3['gridP'][ts]) for ts in range(1439))/3600)
print('PV Utilization:',sum(results_dp_woGessConn_obj3['pvP'])/3347.23)
print('Bill:',sum(results_dp_woGessConn_obj3['gridP'][ts]*pricesignal[ts] for ts in range(1439))/3600/1000)
print()

print("-----------------------------")
print("Objective: Minimize PBill")
print()

print('--LP without GesConn')
print('Import:',sum(results_lp_woGessConn_obj4['gridP'][ts] for ts in range(1439) if results_lp_woGessConn_obj4['gridP'][ts]>0)/3600)
print('Grid:',sum(abs(results_lp_woGessConn_obj4['gridP'][ts]) for ts in range(1439))/3600)
print('PV Utilization:',sum(results_lp_woGessConn_obj4['pvP'])/3347.23)
print('Bill:',sum(results_lp_woGessConn_obj4['gridP'][ts]*pricesignal[ts] for ts in range(1439))/3600/1000)

print('--DP without GesConn')
print('Import:',sum(results_dp_woGessConn_obj4['gridP'][ts] for ts in range(1439) if results_dp_woGessConn_obj4['gridP'][ts]>0)/3600)
print('Grid:',sum(abs(results_dp_woGessConn_obj4['gridP'][ts]) for ts in range(1439))/3600)
print('PV Utilization:',sum(results_dp_woGessConn_obj4['pvP'])/3347.23)
print('Bill:',sum(results_dp_woGessConn_obj4['gridP'][ts]*pricesignal[ts] for ts in range(1439))/3600/1000)
print()


