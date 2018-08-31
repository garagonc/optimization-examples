# -*- coding: utf-8 -*-
"""
Created on Sun Aug 19 14:11:29 2018


@author: guemruekcue
"""
from datetime import *
import numpy as np
import pandas as pd
from itertools import product
import time



#%%
def mc_simulation(timeresolution,horizon,sampleNo,depMu,depStd,arrMu,arrStd,maxCarNo):
    """
    Runs a Monte-Carlo simulation with given statistical parameters
    Returns a dictionary of pmf model
    
    inputs
    -------
    timeresolution: number of seconds in one time step                   
    horizon       : total number of time steps in the prediction horizon
           timeresolution=3600 ->1 hour resolution
           horizon= 24 if timeresolution=3600 ->1 day horizon with 24 time steps
    sampleNo      : number of repetition of MC simulation
    depMu         : Mean departure time of EV 
    depStd        : Standard variation of departure hour 
    arrMu         : Mean arrival time of EV 
    arrStd        : Standard variation of arrival hour
            depMu= 7.75 stands for 07:45 mean departure hour 
                   1.0 equals 60 minutes  
    maxCarNo      : Number of cars in the fleet
    """
    
    
    
    start=datetime(2018,1,1,0,0,0)
    d_range=pd.date_range(start, periods=horizon,freq=pd.Timedelta(seconds=timeresolution))
    timestamps=[]
    position_proof={}
    for dt in d_range:
        #Iterate through the date range (for which we will calculate the markov model)
        mstr=str(dt).split(' ')[1]
        timestamps.append(mstr[:5])   #Generate a list that contains the day times in HH:MM format
        for carNo in range(maxCarNo+1):
            position_proof[mstr[:5],carNo]=0  #Number of the proofs of hosting "carNo" numbers of cars at the park
    
                                
    for n in range(sampleNo):       
        #Simulate many times
        overlap=True
               
        while overlap==True:                   
            cand_dep = np.random.normal(depMu,depStd,maxCarNo)
            cand_arr = np.random.normal(arrMu,arrStd,maxCarNo)
            
            #If departure<arrival
            if all(cand_dep<cand_arr):
                overlap=False
                min_dep = cand_dep*60
                hou_dep, min_dep = divmod(min_dep, 60)
                min_arr = cand_arr*60
                hou_arr, min_arr = divmod(min_arr, 60)

                departure={}
                arrival={}
                for carLabel in range(maxCarNo):                
                
                    #Convert float to HH:MM format
                    departure[carLabel+1]="%02d:%02d"%(hou_dep[carLabel], min_dep[carLabel])
                    arrival[carLabel+1]  ="%02d:%02d"%(hou_arr[carLabel], min_arr[carLabel])
                
        for nb in range(len(timestamps)):
            #Iterates trough every HH:MM of the horizon
            
            this_ts=timestamps[nb]           
            totalParkingCars=0
            
            #Checks how many cars are at home state
            for carLabel in range(1,maxCarNo+1):
                           
                if departure[carLabel]<this_ts<arrival[carLabel]:
                    totalParkingCars+=0
                else:
                    totalParkingCars+=1

            #Use this as a proof for hosting n cars at HH:MM
            position_proof[this_ts,totalParkingCars]+=1/sampleNo
                    
    return position_proof


#%% 
      
def generate_stats_file(behavioral_model,filename):

    fileName='PMFs_'+filename+'.csv'
    
    with open(fileName,'w') as file:
        for ts,number in behavioral_model.keys():
            file.write(str(ts))
            file.write(",")
            file.write(str(number))
            file.write(",")
            file.write(str(behavioral_model[ts,number]))
            file.write('\n')
           
   
    

#%%
if __name__ == "__main__":
    """
    Sample statistics from:
    
    [1] B. Yang, L. F. Wang, C. L. Liao, and L. Ji, 
    “Coordinated charging method of electric vehicles to deal with uncertainty factors,” 
    IEEE Transp. Electrif. Conf. Expo, ITEC Asia-Pacific 2014 - Conf. Proc., pp. 1–6, 2014.
    """        
    dep_mu, dep_sigma = 7.32, 0.78
    arr_mu, arr_sigma = 18.76,1.30
    maxCars=7
    
    start=time.time()
    behaviorModel=mc_simulation(900,96,100000,dep_mu, dep_sigma,arr_mu, arr_sigma,maxCars)
    end=time.time()
    print("Simulation:",end-start)
    
    generate_stats_file(behaviorModel,'15M')