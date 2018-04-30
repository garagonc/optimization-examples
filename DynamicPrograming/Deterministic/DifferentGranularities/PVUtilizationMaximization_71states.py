# -*- coding: utf-8 -*-
"""
Created on Mon Apr 23 10:06:57 2018

@author: guemruekcue
"""

#Minimum grid exchange with 0.01 SOC discretization
from Deterministic.ScenarioClass import scenario_24Ts
from Deterministic.DynamicProgram import DeterministicDynamicProgram
from pyomo.environ import SolverFactory
import time

opt1=SolverFactory('glpk',executable="C:/Users/guemruekcue/Anaconda3/pkgs/glpk-4.63-vc14_0/Library/bin/glpsol")
opt3= SolverFactory("bonmin", executable="C:/cygwin/home/bonmin/Bonmin-1.8.6/build/bin/bonmin")

dynprog_opt3=DeterministicDynamicProgram(scenario_24Ts,1,opt1,1)

#Solving with bonmin
start_time=time.time()
dynprog_opt3.calculateOptimalTrajectory(35)
end_time=time.time()
print("Execution completed in",end_time-start_time,"seconds")