# -*- coding: utf-8 -*-
"""
Created on Tue Apr 17 15:22:05 2018

@author: guemruekcue
"""


from subprocess import call
import shutil
from scenarioConstructer import *
import time
import os

def solve_stochastic_programming(timestep,objective,SoC_ESS,SoC_EV,position,scenarios,drives,probabilities,optimizationValues):  
    
    if objective==1:
        modeldirectory='model_minImp'
    elif objective==2:
        modeldirectory='model_minGrid'
    elif objective==3:
        modeldirectory='model_maxPV'
    elif objective==4:
        modeldirectory='model_minBill'
        
    start_time=time.time()
    
    construct_scenario1(timestep,SoC_ESS,SoC_EV,position,scenarios,drives,probabilities)
    call('runph --model-directory='+modeldirectory+' --instance-directory=nodedata_'+str(timestep)+' --default-rho=1 --solver=ipopt --solution-writer=pyomo.pysp.plugins.csvsolutionwriter')

    csv_file = "ph.csv"
    with open(csv_file) as f:
        for line in f:
            row=line.split(",")
            if row[1]==' RootNode':
                if row[2]==' P_ESS_Output_ini':
                    optimizationValues['P_ESS_Output'].append(float(row[4]))
                    new_SoC_ESS=SoC_ESS-float(row[4])/9.6
                elif row[2]==' P_EV_ChargeAway_ini':
                    optimizationValues['P_EV_ChargeAway'].append(float(row[4]))
                elif row[2]==' P_EV_ChargeHome_ini':
                    optimizationValues['P_EV_ChargeHome'].append(float(row[4]))
                    new_SoC_EV=SoC_EV+float(row[4])/30.0
                elif row[2]==' P_Grid_Output_ini':
                    optimizationValues['P_Grid_Output'].append(float(row[4]))            
                elif row[2]==' P_PV_Output_ini':
                    optimizationValues['P_PV_Output'].append(float(row[4]))
    
    nodefile='nodedata_'+str(timestep)
    os.remove(csv_file)
    os.remove('ph_StageCostDetail.csv')
    shutil.rmtree(nodefile)
    
    end_time=time.time()
    print("Execution time:",end_time-start_time,"seconds")

    return new_SoC_ESS,new_SoC_EV,optimizationValues

#%%
def continuousOptimization(iniEss,iniEv,positions,scenarios,drives,probabilities,obj):
    
    optVal={}
    optVal['P_Grid_Output']  =[]
    optVal['P_PV_Output']    =[]
    optVal['P_ESS_Output']   =[]
    optVal['P_EV_ChargeAway']=[]
    optVal['P_EV_ChargeHome']=[]
       
    
    ess={0:iniEss}
    ev={0:iniEv}
    
    for ts in range(23):
        print("Hour:",ts)
        ini_ess=ess[ts]
        ini_ev=ev[ts] if positions[ts]==1 else 0.20
    
        ess[ts+1],ev[ts+1],optVal=solve_stochastic_programming(ts,obj,ini_ess,ini_ev,positions[ts],scenarios,drives,probabilities,optVal)
    
    return ess,ev,optVal

print('Minimum import')
soc_ess1,soc_ev1,optval1=continuousOptimization(0.40,0.30,realization1,ScenariosOfRealization1,DrivesOfRealization1,ScenarioProbabilitiesforRealization1,1)
print('Minimum power exchange')
#soc_ess2,soc_ev2,optval2=continuousOptimization(0.40,0.30,realization1,ScenariosOfRealization1,DrivesOfRealization1,ScenarioProbabilitiesforRealization1,2)
print('Max PV utilization')
#soc_ess3,soc_ev3,optval3=continuousOptimization(0.40,0.30,realization1,ScenariosOfRealization1,DrivesOfRealization1,ScenarioProbabilitiesforRealization1,3)
print('Minimum power bill')
#soc_ess4,soc_ev4,optval4=continuousOptimization(0.40,0.30,realization1,ScenariosOfRealization1,DrivesOfRealization1,ScenarioProbabilitiesforRealization1,4)



    