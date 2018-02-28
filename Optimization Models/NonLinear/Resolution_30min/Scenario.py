# -*- coding: utf-8 -*-
"""
Created on Wed Feb 28 17:05:10 2018

@author: guemruekcue
"""

from pyomo.environ import *
from pyomo.opt import SolverFactory
import matplotlib.pylab as plt

# Create a solver
opt= SolverFactory("bonmin", executable="C:/cygwin/home/bonmin/Bonmin-1.8.6/build/bin/bonmin")

print("#################################################")
print("Initializing Paramters")
print("#################################################")

daylong=60*60*24
dT_min=30       #time step length in minutes
dT=dT_min*60    #time step length in seconds
N=int(daylong/dT)   #Number of time steps


file = open("C:/Users/guemruekcue/internship/optimization-agent/profiles/load_profile_10.txt", 'r')
lines = file.read().splitlines()
keys=range(len(lines))

pdem = []
for i in keys:
    pdem.append(float(lines[i]))
Pdem=[]
for ts in range(N):
    Pdem.append(sum(pdem[ts*dT_min:(ts+1)*dT_min])/dT_min)      #Takes the average of the range
    
filePV = open("C:/Users/guemruekcue/internship/optimization-agent/profiles/PV_profile3.txt", 'r')
linesPV = filePV.read().splitlines()
keysPV=range(len(linesPV))
pv = []
for i in keysPV:
    pv.append(float(linesPV[i]))
PV=[]
for ts in range(N):
    PV.append(sum(pv[ts*dT_min:(ts+1)*dT_min])/dT_min)


file_price = open("C:/Users/guemruekcue/internship/optimization-agent/profiles/price_proflie_1.txt", 'r')  
linesPrice = file_price.read().splitlines()
priceImp=[]
for row in linesPrice:
    priceImp=priceImp+[float(row)]*int(60/dT_min)

priceExp=[20]*N           #A uniformal feed-in tariff


Eff_Charging=0.9
Eff_Discharging= 0.7
Capacity=9.6*3600   #kWs
