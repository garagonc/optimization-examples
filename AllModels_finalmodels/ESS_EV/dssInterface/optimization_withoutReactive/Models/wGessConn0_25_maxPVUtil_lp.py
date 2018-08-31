# -*- coding: utf-8 -*-
"""
Created on Tue Jun 26 17:28:03 2018

@author: guemruekcue
"""

from WithGESSCon.LinearPrograming.WithoutReactive.Objectives.MaximizePV import MaximizePVUtilization as optmodel
from pyomo.environ import SolverFactory
import pandas as pd
if __name__=="__main__":
    import os 
    os.chdir(r'C:/Users/guemruekcue/internship/optimization-agent/AllModels/ESS_EV/dssInterface')

#opt1=SolverFactory('glpk',executable="C:/Users/guemruekcue/Anaconda3/pkgs/glpk-4.63-vc14_0/Library/bin/glpsol")
#opt2= SolverFactory("ipopt", executable="C:/Users/guemruekcue/Anaconda3/pkgs/ipopt-3.11.1-2/Library/bin/ipopt")
#opt3= SolverFactory("bonmin", executable="C:/cygwin/home/bonmin/Bonmin-1.8.6/build/bin/bonmin")

optimizationmodel=optmodel()
opt3= SolverFactory("bonmin", executable="C:/cygwin/home/bonmin/Bonmin-1.8.6/build/bin/bonmin")
optimizationmodel.calculateOptimalTrajectory('optimization_withoutReactive/Scenarios/scenario_lp_wGessConn_0_25.dat',opt3)

p_pv=[]
p_ess=[]
p_grid=[]

for ts in range(24):
    p_pv.append(optimizationmodel.P_PV[ts])
    p_ess.append(optimizationmodel.P_ESS[0][ts])
    p_grid.append(optimizationmodel.P_GRID[ts])
    
#%%    
schedules=pd.DataFrame(list(zip(p_pv,p_ess,p_grid)),columns=['p_pv','p_ess','p_grid'])