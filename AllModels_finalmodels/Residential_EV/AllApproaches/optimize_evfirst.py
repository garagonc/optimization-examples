# -*- coding: utf-8 -*-
"""
Created on Thu Aug 16 11:38:58 2018

@author: guemruekcue
"""

import os
import pandas as pd
from datetime import *
from functions import import_statistics
from pyomo.environ import SolverFactory
from EVFirst.RealCapacity_maxPV_withoutGesscon import MaximizePV


def optimize_ev_first(year,month,day,
                  timeresolution,
                  horizon,
                  solver,
                  ev_capacity,
                  evSoCdomain,
                  evDecisionDomain,
                  ev_minSoC,
                  dropPenalty,
                  unitConsumption,
                  ess_capacity,
                  ess_minSoC,
                  ess_maxSoC,
                  ess_max_charge,
                  ess_max_discharge,
                  grid_max_export,
                  pv_max_generation,
                  local_em_weight,
                  global_em_weight,
                  behaviorModel,                  
                  forecasts_file,
                  dsoCommand_file,
                  ess_iniSoC,ev_iniSoC,
                  realScenario): #DataFrame
    
   
    simulation_start=datetime(year,month,day,0,0)
    delta_t=pd.Timedelta(seconds=timeresolution)
    xl_forecast=pd.ExcelFile(forecasts_file)
    xl_dso=pd.ExcelFile(dsoCommand_file)
    
    ess_soc={simulation_start:ess_iniSoC}
    ev_pos={simulation_start:realScenario["Position"][0]}
    ev_soc_real={simulation_start:ev_iniSoC}
    ev_soc_estm={simulation_start:ev_iniSoC}
    
    p_pv_pot={}
    p_load={}
    p_grid={}
    p_pv={}
    p_ev={}
    p_ess={}
      
       
    for t in range(horizon):
        hourDt=simulation_start+t*delta_t
        hour=hourDt.strftime("%H:%M")
        print("Optimization for",hour)
        markovModel=import_statistics(behaviorModel,hour)    
        forecasts  = xl_forecast.parse(str(t))
        dso_commands = xl_dso.parse(str(t))  
        
        forecast_load=dict(enumerate(forecasts['Load'].values.tolist()))
        forecast_pv=dict(enumerate(forecasts['PV'].values.tolist()))
        forecast_price=dict(enumerate(forecasts['Price'].values.tolist()))
        dso_command=dict(enumerate(dso_commands['Charge'].values.tolist()))
    
        ess_SoC=ess_soc[hourDt]
        ev_Pos=ev_pos[hourDt]
        ev_SoC=ev_soc_real[hourDt] if ev_Pos==1 else ev_soc_estm[hourDt]
            
        EMOptimizer=MaximizePV(timeresolution,horizon,solver,
                               ev_capacity,evSoCdomain,evDecisionDomain,unitConsumption,
                               markovModel,ev_minSoC,dropPenalty,
                               local_em_weight,global_em_weight,
                               forecast_load,forecast_pv,forecast_price,dso_command,
                               ess_max_charge,ess_max_discharge,grid_max_export,pv_max_generation,
                               ess_capacity,ess_minSoC,ess_maxSoC,
                               ess_SoC,ev_SoC,ev_Pos)
        
        decisions=EMOptimizer.optimize_full_EM()
        
        
        p_pv_pot[hourDt]=forecast_pv[0]
        p_load[hourDt]  =forecast_load[0]
        p_grid[hourDt]=decisions["P_Grid"]
        p_pv[hourDt]=decisions["P_PV"]
        p_ev[hourDt]=decisions["P_EV"]
        p_ess[hourDt]=decisions["P_ESS"]
        
        
        if t<horizon-1:
        
            ess_soc[hourDt+delta_t]=ess_soc[hourDt]-p_ess[hourDt]*timeresolution/(ess_capacity*3600)
            ev_pos[hourDt+delta_t]=realScenario["Position"][t]
            ev_soc_real[hourDt+delta_t]=ev_soc_real[hourDt]-p_ev[hourDt]*timeresolution/(ev_capacity*3600)+realScenario["deltaSoC[%]"][t]/100
            
            if ev_pos[hourDt+delta_t]==1:
                ev_soc_estm[hourDt+delta_t]=ev_soc_real[hourDt+delta_t]
            else:
                if ev_soc_estm[hourDt]-unitConsumption/100>=0:
                    ev_soc_estm[hourDt+delta_t]=ev_soc_estm[hourDt]-unitConsumption/100
                else:
                    ev_soc_estm[hourDt+delta_t]=0.0
    
    
    #Keep the results
    results=pd.DataFrame(columns=["Demand Forecast","PV Forecast","EV Position",
                                  "P_PV","P_ESS","P_GRID","P_EV",
                                  "ESS SoC","EV Real SoC","EV Estm SoC"],
            index=pd.date_range(simulation_start, periods=horizon,freq=delta_t))
    results["Demand Forecast"]=p_load.values()
    results["PV Forecast"]=p_pv_pot.values()
    results["EV Position"]=ev_pos.values()
    results["P_PV"]=p_pv.values()
    results["P_ESS"]=p_ess.values()
    results["P_GRID"]=p_grid.values()
    results["P_EV"]=p_ev.values()
    results["ESS SoC"]=ess_soc.values()
    results["EV Real SoC"]=ev_soc_real.values()
    results["EV Estm SoC"]=ev_soc_estm.values()
                
    return results
    

if __name__ == "__main__":
    print("First EV optimized")      
    #Input directory    
    AllAproaches_dir=os.path.dirname(__file__)
    Inputs_dir=os.path.join(AllAproaches_dir,'Inputs')
    
    #Scenario parameters
    year=2018
    month=7
    day=15
    timeresolution=3600
    horizon=24
    theSolver=SolverFactory('glpk',executable="C:/Users/guemruekcue/Anaconda3/pkgs/glpk-4.63-vc14_0/Library/bin/glpsol")
    #theSolver= SolverFactory("bonmin", executable="C:/cygwin/home/bonmin/Bonmin-1.8.6/build/bin/bonmin")
    ev_bat_capacity=40
    evSoCdomain=range(0,105,5)
    evDecisionDomain=range(0,25,5)
    ev_minSoC=0.2
    dropPenalty=1   #1/kWh
    unitconsumption=10  #10% SoC per hour
    ess_capacity=0.675
    ess_minSoC=0.2
    ess_maxSoC=1.0
    ess_max_charge=0.62
    ess_max_discharge=0.62
    grid_max_export=10
    pv_max_generation=1.5
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
    
    results=optimize_ev_first(year,month,day,timeresolution,horizon,theSolver,
                              ev_bat_capacity,evSoCdomain,evDecisionDomain,ev_minSoC,
                              dropPenalty,unitconsumption,
                              ess_capacity,ess_minSoC,ess_maxSoC,
                              ess_max_charge,ess_max_discharge,
                              grid_max_export,pv_max_generation,
                              local_em_weight,global_em_weight,
                              Markov_inp,Forecast_inp,DSO_inp,
                              ess_iniSoC,ev_iniSoC,scenario1) 
    
