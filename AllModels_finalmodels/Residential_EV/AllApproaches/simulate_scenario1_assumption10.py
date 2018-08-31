# -*- coding: utf-8 -*-
"""
Created on Fri Aug 17 10:59:17 2018

@author: guemruekcue
"""

import os
import pandas as pd
from pyomo.environ import SolverFactory

from optimize_evfirst import optimize_ev_first
from optimize_simultaneous import optimize_simultaneously

#%%
#Input directory    
AllAproaches_dir=os.path.dirname(__file__)
Inputs_dir=os.path.join(AllAproaches_dir,'Inputs')

#Simulation parameters
year=2018
month=7
day=15
timeresolution=3600
horizon=24
theSolver=SolverFactory('glpk',executable="C:/Users/guemruekcue/Anaconda3/pkgs/glpk-4.63-vc14_0/Library/bin/glpsol")

#Physical constraints
ev_bat_capacity=40
ev_minSoC=0.2
ess_capacity=0.675
ess_minSoC=0.2
ess_maxSoC=1.0
ess_max_charge=0.62
ess_max_discharge=0.62
grid_max_export=10
pv_max_generation=1.5

#Optimization parameters
evSoCdomain=range(0,110,10)
evDecisionDomain=range(0,20,10)
essSoCdomain=range(0,110,10)
essDecisionDomain=range(-10,20,10)
dropPenalty=1   #1/kWh
unitconsumptionAssumption=10  #10% SoC per hour
local_em_weight=1
global_em_weight=1
     
#Input files
Forecast_inp=Inputs_dir+'\Forecasts_60M.xlsx'
Markov_inp=Inputs_dir+'\Markov_60M.csv'
DSO_inp=Inputs_dir+'\GessCon_60M.xlsx'
Scenario_inp=Inputs_dir+'\DriveScenarios_60M.xlsx'
scenario_xl= pd.ExcelFile(Scenario_inp)
scenario1  = scenario_xl.parse('Scenario1')
    
#Simulation start parameters
ess_iniSoC=0.4
ev_iniSoC=0.2


#%%
print("First EV optimized")
results_evfirst=optimize_ev_first(year,month,day,timeresolution,horizon,theSolver,
                                   ev_bat_capacity,evSoCdomain,evDecisionDomain,ev_minSoC,
                                  dropPenalty,unitconsumptionAssumption,
                                  ess_capacity,ess_minSoC,ess_maxSoC,
                                  ess_max_charge,ess_max_discharge,
                                  grid_max_export,pv_max_generation,
                                  local_em_weight,global_em_weight,
                                  Markov_inp,Forecast_inp,DSO_inp,
                                  ess_iniSoC,ev_iniSoC,scenario1) 

#%%
print("Simultaneous optimization")
results_simultaneous=optimize_simultaneously(year,month,day,timeresolution,horizon,theSolver,
                                          ev_bat_capacity,evSoCdomain,evDecisionDomain,
                                          essSoCdomain,essDecisionDomain,
                                          ev_minSoC,dropPenalty,unitconsumptionAssumption,
                                          ess_capacity,ess_minSoC,ess_maxSoC,
                                          ess_max_charge,ess_max_discharge,
                                          grid_max_export,pv_max_generation,
                                          Markov_inp,Forecast_inp,
                                          ess_iniSoC,ev_iniSoC,scenario1)

#%%
"""
print("Printing results")
writer = pd.ExcelWriter('Results_Scenario1_Assumption10.xlsx')
results_evfirst.to_excel(writer,"EVFirst")
results_simultaneous.to_excel(writer,"Simultaneous")
writer.save()
"""

