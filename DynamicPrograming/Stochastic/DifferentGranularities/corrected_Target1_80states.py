# -*- coding: utf-8 -*-
"""
Created on Wed Apr 25 16:43:44 2018

@author: guemruekcue
"""

#Minimum grid exchange with 0.1 SOC discretization
from Stochastic.ScenarioClass import scenario_24Ts
from Stochastic.DynamicProgram2 import StochasticDynamicProgram
from pyomo.environ import SolverFactory
import time
import os

# %%
stochasticfolder=os.path.dirname(os.path.dirname(__file__))
pbmatrix='MarkovModel.csv'
pbmatrix2='EVSoCModel.csv'
filename1=os.path.join(stochasticfolder,pbmatrix)
filename2=os.path.join(stochasticfolder,pbmatrix2)

prob_plug={}
with open(filename1) as f:
    for line in f:
        row=line.split(",")
        prob_plug[int(row[0]),int(row[1]),int(row[2])]=float(row[3])        

prob_end_soc={}
with open(filename2) as f2:
    for line in f2:
        row=line.split(",")
        prob_end_soc[int(row[0])]=float(row[1])   


# %%
opt1=SolverFactory('glpk',executable="C:/Users/guemruekcue/Anaconda3/pkgs/glpk-4.63-vc14_0/Library/bin/glpsol")
opt2= SolverFactory("ipopt", executable="C:/Users/guemruekcue/Anaconda3/pkgs/ipopt-3.11.1-2/Library/bin/ipopt")
opt3= SolverFactory("bonmin", executable="C:/cygwin/home/bonmin/Bonmin-1.8.6/build/bin/bonmin")

ess_domain=[20,30,40,50,60,70,80,90]
ev_domain=[30,40,50,60,70]


dynprog=StochasticDynamicProgram(scenario_24Ts,ess_domain,ev_domain,opt1,1,prob_plug,prob_end_soc)
"""
dynprog_opt3.optimaldecisioncalculator(23,50,40,0)
result=dynprog_opt3.Decision[23,50,40,0]
"""
start_time=time.time()
dynprog.wholeMapCalculation()
end_time=time.time()
print("Execution completed in",end_time-start_time,"seconds")

# %%
results=dynprog.findoptimalValues(0,50,50,1)
print(results)
