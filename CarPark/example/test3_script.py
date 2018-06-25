# -*- coding: utf-8 -*-
"""
Created on Wed Jun 20 10:36:37 2018

@author: guemruekcue
"""

import numpy as np
import pandas as pd
import os
from CarParkOptimization.DynamicProgram import *
from CarParkOptimization.CarPark import CarPark
from StatisticalAnalysis.analysispy import stats,markov

os.chdir(os.path.dirname(__file__))


def proceed(Carpark,start_ess,start_vir,solver):
    
    print("Coef2:",Carpark.coef2)
    print("--------------------")
    ess_soc=start_ess
    vir_soc=start_vir
    realtime={}
    
    for t in range(Carpark.systemParameters.T):
        
        print("Hour:",t)
        print("Start",ess_soc,vir_soc)
        
        realtime[t]=RTDataClass(ess_soc,vir_soc,df_drive['Driving'][t])
        load_forecast=df_load[t]
        pv_forecast=df_pv[t]
        
        Carpark.calculate_control_action(t,realtime[t],load_forecast,pv_forecast,solver)
        
        ess_soc=int(ess_soc+Carpark.p_ess[t]/Carpark.systemParameters.ess_capacity*100)
        vir_soc=int(vir_soc+Carpark.p_vir[t]/Carpark.systemParameters.vir_capacity*100+df_drive['deltaSoC'][t])
        
        print("End",ess_soc,vir_soc)
    print()

#%%
opt1=SolverFactory('glpk',executable="C:/Users/guemruekcue/Anaconda3/pkgs/glpk-4.63-vc14_0/Library/bin/glpsol")
 
opt_horizon=24
ess_capacity=50
vir_capacity=200
systParam=SystemParameters(opt_horizon,ess_capacity,vir_capacity)

ess_soc_domain=range(0,110,10)
virtual_soc_domain=range(0,105,5)
ess_decision=range(-30,30,10)
vir_decision=range(0,25,5)
maxnbofcars=8
unitconsumption=5
dpParam=DPParameters(ess_soc_domain,virtual_soc_domain,opt1,ess_decision,vir_decision,maxnbofcars,unitconsumption)

xl = pd.ExcelFile("Forecasts_constant_test3.xlsx")
df_load = xl.parse("Load")
df_pv  = xl.parse("PV")
df_drive=xl.parse("Drive")

carpark1=CarPark(systParam,dpParam,markov,1,1)
carpark2=CarPark(systParam,dpParam,markov,1,2)
carpark3=CarPark(systParam,dpParam,markov,1,3)
carpark4=CarPark(systParam,dpParam,markov,1,4)
carpark5=CarPark(systParam,dpParam,markov,1,5)

#%%

start_ess_soc=30
start_vir_soc=40
#realtime0=RTDataClass(start_ess_soc,start_vir_soc,0)
#load_forecast=df_load[0]
#pv_forecast=df_pv[0]
#carpark.calculate_control_action(0,realtime0,load_forecast,pv_forecast,opt1)

proceed(carpark1,start_ess_soc,start_vir_soc,opt1)
proceed(carpark2,start_ess_soc,start_vir_soc,opt1)
proceed(carpark3,start_ess_soc,start_vir_soc,opt1)
proceed(carpark4,start_ess_soc,start_vir_soc,opt1)
proceed(carpark5,start_ess_soc,start_vir_soc,opt1)
#%%
coef1_p_vir=carpark1.p_vir
coef2_p_vir=carpark2.p_vir
coef3_p_vir=carpark3.p_vir
coef4_p_vir=carpark4.p_vir
coef5_p_vir=carpark5.p_vir

coef1_pv=carpark1.p_pv
coef2_pv=carpark2.p_pv
coef3_pv=carpark3.p_pv
coef4_pv=carpark4.p_pv
coef5_pv=carpark5.p_pv

coef1_grid=carpark1.p_grid
coef2_grid=carpark2.p_grid
coef3_grid=carpark3.p_grid
coef4_grid=carpark4.p_grid
coef5_grid=carpark5.p_grid

coef1_p_ess=carpark1.p_ess
coef2_p_ess=carpark2.p_ess
coef3_p_ess=carpark3.p_ess
coef4_p_ess=carpark4.p_ess
coef5_p_ess=carpark5.p_ess

coef1_essSoc=carpark1.soc_ess
coef2_essSoc=carpark2.soc_ess
coef3_essSoc=carpark3.soc_ess
coef4_essSoc=carpark4.soc_ess
coef5_essSoc=carpark5.soc_ess

coef1_virSoc=carpark1.soc_vir
coef2_virSoc=carpark2.soc_vir
coef3_virSoc=carpark3.soc_vir
coef4_virSoc=carpark4.soc_vir
coef5_virSoc=carpark5.soc_vir

pEss=pd.DataFrame(list(zip(coef1_p_ess,coef2_p_ess,coef3_p_ess,coef4_p_ess,coef5_p_ess)),columns=['coef1','coef2','coef3','coef4','coef5'])
pVir=pd.DataFrame(list(zip(coef1_p_vir,coef2_p_vir,coef3_p_vir,coef4_p_vir,coef5_p_vir)),columns=['coef1','coef2','coef3','coef4','coef5'])
pPV=pd.DataFrame(list(zip(coef1_pv,coef2_pv,coef3_pv,coef4_pv,coef5_pv)),columns=['coef1','coef2','coef3','coef4','coef5'])
pGrid=pd.DataFrame(list(zip(coef1_grid,coef2_grid,coef3_grid,coef4_grid,coef5_grid)),columns=['coef1','coef2','coef3','coef4','coef5'])
SocEss=pd.DataFrame(list(zip(coef1_essSoc,coef2_essSoc,coef3_essSoc,coef4_essSoc,coef5_essSoc)),columns=['coef1','coef2','coef3','coef4','coef5'])
SoCVir=pd.DataFrame(list(zip(coef1_virSoc,coef2_virSoc,coef3_virSoc,coef4_virSoc,coef5_virSoc)),columns=['coef1','coef2','coef3','coef4','coef5'])