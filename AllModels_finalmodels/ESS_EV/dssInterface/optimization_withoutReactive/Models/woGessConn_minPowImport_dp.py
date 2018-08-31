# -*- coding: utf-8 -*-
"""
Created on Tue Jun 26 18:31:07 2018

@author: guemruekcue
"""

from WithoutGESSCon.DynamicPrograming.WithoutReactive.Objectives.MinimizePImport import DynamicMinimizePImport as optmodel
from dssInterface.optimization_withoutReactive.Scenarios.scenario_dp_woGessConn import *
from pyomo.environ import SolverFactory
import pandas as pd

#opt1=SolverFactory('glpk',executable="C:/Users/guemruekcue/Anaconda3/pkgs/glpk-4.63-vc14_0/Library/bin/glpsol")
#opt2= SolverFactory("ipopt", executable="C:/Users/guemruekcue/Anaconda3/pkgs/ipopt-3.11.1-2/Library/bin/ipopt")
#opt3= SolverFactory("bonmin", executable="C:/cygwin/home/bonmin/Bonmin-1.8.6/build/bin/bonmin")

opt3= SolverFactory("bonmin", executable="C:/cygwin/home/bonmin/Bonmin-1.8.6/build/bin/bonmin")
dynprog=optmodel(scenario_24Ts,ess_soc_domain,decision_domain,opt3)
dynprog.calculateOptimalTrajectory(ini_soc)

p_pv=[]
p_ess=[]
p_grid=[]

for ts in range(24):
    p_pv.append(dynprog.P_PV[ts])
    p_ess.append(dynprog.P_ESS[ts])
    p_grid.append(dynprog.P_Grid[ts])
    
#%%
if __name__=="__main__":
    import pandas as pd
    
schedules=pd.DataFrame(list(zip(p_pv,p_ess,p_grid)),columns=['p_pv','p_ess','p_grid'])