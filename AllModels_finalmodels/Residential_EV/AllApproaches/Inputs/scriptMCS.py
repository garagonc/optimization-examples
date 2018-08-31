# -*- coding: utf-8 -*-
"""
Created on Thu Aug  9 14:37:49 2018

@author: guemruekcue
"""
from datetime import *
import numpy as np
import pandas as pd
from itertools import product
import time

#%%
def mc_simulation(timeresolution,horizon,sampleNo,depMu,depStd,arrMu,arrStd):
    """
    Runs a Monte-Carlo simulation with given statistical parameters
    Returns a dictionary of markovModel
    
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
    """
    
    start=datetime(2018,1,1,0,0,0)
    d_range=pd.date_range(start, periods=horizon,freq=pd.Timedelta(seconds=timeresolution))
    timestamps=[]
    transition_proof={}
    position_proof={}
    markov_model={}
    for dt in d_range:
        #Iterate through the date range (for which we will calculate the markov model)
        
        mstr=str(dt).split(' ')[1]      
        timestamps.append(mstr[:5])      #Generate a list that contains the day times in HH:MM format
        transition_proof[mstr[:5],0,0]=0 #Number of the proofs of switching from away to away state at HH:MM in this simulation
        transition_proof[mstr[:5],0,1]=0 #Number of the proofs of switching from away to home state at HH:MM in this simulation
        transition_proof[mstr[:5],1,0]=0 #Number of the proofs of switching from home to away state at HH:MM in this simulation
        transition_proof[mstr[:5],1,1]=0 #Number of the proofs of switching from home to home state at HH:MM in this simulation
        position_proof[mstr[:5],0]=0     #Number of the proofs of having away state at HH:MM in this simulation
        position_proof[mstr[:5],1]=0
        markov_model[mstr[:5],0,0]=None
        markov_model[mstr[:5],0,1]=None
        markov_model[mstr[:5],1,0]=None
        markov_model[mstr[:5],1,1]=None
                                
    for n in range(sampleNo):  
        #Simulate many times
        
        overlap=True
        
        while overlap==True:
            #Draw random numbers for departure and arrival time until departure<arrival                   
            cand_dep = np.random.normal(depMu,depStd)
            cand_arr = np.random.normal(arrMu,arrStd)
            
            #If departure<arrival
            if cand_dep<cand_arr:
                overlap=False
                min_dep = cand_dep*60
                hou_dep, min_dep = divmod(min_dep, 60)
                min_arr = cand_arr*60
                hou_arr, min_arr = divmod(min_arr, 60)                
                
                #Convert float to HH:MM format
                departure="%02d:%02d"%(hou_dep, min_dep)
                arrival  ="%02d:%02d"%(hou_arr, min_arr)
                
            for nb in range(len(timestamps)):
                #Iterates trough every HH:MM of the horizon
                               
                this_ts=timestamps[nb]      
                next_ts=timestamps[nb+1] if nb<len(timestamps)-1 else '24:00'
                
                if this_ts<departure: #If this HH:MM is smaller than my departure time

                    position_proof[this_ts,1]+=1          #Counts as one proof for Home state at HH:MM                   
                    if next_ts<departure:   #If next hour (of HH:MM) is smaller than my departure time 
                        transition_proof[this_ts,1,1]+=1  #Counts as one proof for transition from home to home state during HH:MM
                    else:                   #Otherwise
                        transition_proof[this_ts,1,0]+=1  #Counts as one proof for transition from home to away state during HH:MM
                
                elif departure<this_ts<arrival: #If this HH:MM is between my departure and arrival times 
                    position_proof[this_ts,0]+=1          #Counts as one proof for Away state at HH:MM
                    if next_ts<arrival:    #If next hour (of HH:MM) is smaller than my arrival time
                        transition_proof[this_ts,0,0]+=1 #Counts as one proof for transition from away to away state during HH:MM
                    else:                  #Otherwise
                        transition_proof[this_ts,0,1]+=1  #Counts as one proof for transition from away to home state during HH:MM
                
                elif arrival<=this_ts:  #If this HH:MM is greater than my arrival time
                    position_proof[this_ts,1]+=1          #Counts as one proof for Home state at HH:MM
                    transition_proof[this_ts,1,1]+=1      #Counts as one proof for transition from home to home state during HH:MM
        

    for timestamp in timestamps:
        #Iterates through every HH:MM of the day(horizon)

        #Calculates the markov transition probabilities using transition and position proofs
        #e.g.
        #Transition probability(p) from away to away state at 6 AM
        #markov_model["06:00",0,0]=proof of this transition at 6 AM/ proof of away position at 6 AM
        #Note that if there is not any proof of away (0) position at 6 AM in whole simulation
        #Then both transitions are assummed to be equally possible:
        #markov_model["06:00",0,0]=markov_model["06:00",0,1]=0.5
        
        markov_model[timestamp,0,0]=transition_proof[timestamp,0,0]/position_proof[timestamp,0] if position_proof[timestamp,0]!=0 else 0.5
        markov_model[timestamp,0,1]=transition_proof[timestamp,0,1]/position_proof[timestamp,0] if position_proof[timestamp,0]!=0 else 0.5
        markov_model[timestamp,1,0]=transition_proof[timestamp,1,0]/position_proof[timestamp,1] if position_proof[timestamp,1]!=0 else 0.5
        markov_model[timestamp,1,1]=transition_proof[timestamp,1,1]/position_proof[timestamp,1] if position_proof[timestamp,1]!=0 else 0.5
                                       
    return markov_model


#%%        
def generate_markov_file(markov_model,filename):
    """
    Generates a csv file with the given MarkovModel dictionary
    """
    

    fileName='Markov_'+filename+'.csv'
    
    with open(fileName,'w') as file:
        for ts,ini_pos,fin_pos in markov_model.keys():
            file.write(str(ts))
            file.write(",")
            file.write(str(ini_pos))
            file.write(",")
            file.write(str(fin_pos))
            file.write(",")
            file.write(str(markov_model[ts,ini_pos,fin_pos]))
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
    
    start=time.time()
    markovModel=mc_simulation(60,24*60,1000,dep_mu, dep_sigma,arr_mu, arr_sigma)
    end=time.time()
    print("Simulation:",end-start)
    
    generate_markov_file(markovModel,'1M')