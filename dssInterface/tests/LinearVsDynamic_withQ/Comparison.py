# -*- coding: utf-8 -*-
"""
Created on Fri Apr 27 09:38:21 2018

@author: guemruekcue
"""

from maxPV_dynamic  import maxPVDyn
from maxPV_quadratic  import maxPVQuad
from minGrid_dynamic  import minGridDyn
from minGrid_quadratic  import minGridQuad
from minPBill_dynamic  import minPBillDyn
from minPBill_quadratic  import minPBillQuad

#%%
import matplotlib.pyplot as plt
from Rainflow import *

#%%

#Performance indicators

#Total import

totalimport_maxPv_dyn=sum(maxPVDyn['P_Import'][t]*60 for t in range(1440) if maxPVDyn['P_Import'][t]>0)/3600
totalimport_maxPv_lin=sum(maxPVQuad['P_Import'][t]*60 for t in range(1440) if maxPVQuad['P_Import'][t]>0)/3600
totalimport_grid_dyn=sum(minGridDyn['P_Import'][t]*60 for t in range(1440) if minGridDyn['P_Import'][t]>0)/3600
totalimport_grid_lin=sum(minGridQuad['P_Import'][t]*60 for t in range(1440) if minGridQuad['P_Import'][t]>0)/3600
totalimport_bill_dyn=sum(minPBillDyn['P_Import'][t]*60 for t in range(1440) if minPBillDyn['P_Import'][t]>0)/3600
totalimport_bill_lin=sum(minPBillQuad['P_Import'][t]*60 for t in range(1440) if minPBillQuad['P_Import'][t]>0)/3600

totalexport_maxPv_dyn=sum(maxPVDyn['P_Import'][t]*60 for t in range(1440) if maxPVDyn['P_Import'][t]<0)/3600
totalexport_maxPv_lin=sum(maxPVQuad['P_Import'][t]*60 for t in range(1440) if maxPVQuad['P_Import'][t]<0)/3600
totalexport_grid_dyn=sum(minGridDyn['P_Import'][t]*60 for t in range(1440) if minGridDyn['P_Import'][t]<0)/3600
totalexport_grid_lin=sum(minGridQuad['P_Import'][t]*60 for t in range(1440) if minGridQuad['P_Import'][t]<0)/3600
totalexport_bill_dyn=sum(minPBillDyn['P_Import'][t]*60 for t in range(1440) if minPBillDyn['P_Import'][t]<0)/3600
totalexport_bill_lin=sum(minPBillQuad['P_Import'][t]*60 for t in range(1440) if minPBillQuad['P_Import'][t]<0)/3600

#PV Utilization
normalization=sum(maxPVDyn['P_PV']) 
pvutil_maxPv_dyn=sum(maxPVDyn['P_PV'])/normalization   
pvutil_maxPv_lin=sum(maxPVQuad['P_PV'])/normalization
pvutil_grid_dyn=sum(minGridDyn['P_PV'])/normalization
pvutil_grid_lin=sum(minGridQuad['P_PV'])/normalization
pvutil_bill_dyn=sum(minPBillDyn['P_PV'])/normalization
pvutil_bill_lin=sum(minPBillQuad['P_PV'])/normalization


#Battery degratation
#Example chosen such that 4000 clycle lifetime at 80% DoD 
A=2873.1
B=-1.483

#Rainflow counting: a list of tuples that contain load ranges and the corresponding number of cycles
rf_maxPv_dyn=count_cycles(maxPVDyn['SoC'])  
rf_maxPv_lin=count_cycles(maxPVQuad['SoC'])
rf_grid_dyn=count_cycles(minGridDyn['SoC'])
rf_grid_lin=count_cycles(minGridQuad['SoC'])
rf_bill_dyn=count_cycles(minPBillDyn['SoC'])
rf_bill_lin=count_cycles(minPBillQuad['SoC'])



#Degradation of life-cycle
D_CL_maxPv_dyn=sum(pair[1]/(A*pow(pair[0],B)) for pair in rf_maxPv_dyn)*100
D_CL_maxPv_lin=sum(pair[1]/(A*pow(pair[0],B)) for pair in rf_maxPv_lin)*100
D_CL_grid_dyn=sum(pair[1]/(A*pow(pair[0],B)) for pair in rf_grid_dyn)*100
D_CL_grid_lin=sum(pair[1]/(A*pow(pair[0],B)) for pair in rf_grid_lin)*100
D_CL_bill_dyn=sum(pair[1]/(A*pow(pair[0],B)) for pair in rf_bill_dyn)*100
D_CL_bill_lin=sum(pair[1]/(A*pow(pair[0],B)) for pair in rf_bill_lin)*100


#Bill paid
price_Forecast={
0 :  34.61,
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

price=[]
for i in range(24):
    for t in range(60):
        price.append(price_Forecast[i])

billmaxPv_dyn=sum(price[t]*maxPVDyn['P_Import'][t]*60/3600/1000 for t in range(1440))  
billmaxPv_quad=sum(price[t]*maxPVQuad['P_Import'][t]*60/3600/1000 for t in range(1440))
billgrid_dyn=sum(price[t]*minGridDyn['P_Import'][t]*60/3600/1000 for t in range(1440))
billgrid_quad=sum(price[t]*minGridQuad['P_Import'][t]*60/3600/1000 for t in range(1440))
billbill_dyn=sum(price[t]*minPBillDyn['P_Import'][t]*60/3600/1000 for t in range(1440))
billbill_quad=sum(price[t]*minPBillQuad['P_Import'][t]*60/3600/1000 for t in range(1440))

