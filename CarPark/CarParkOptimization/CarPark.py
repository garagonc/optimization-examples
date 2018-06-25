# -*- coding: utf-8 -*-
"""
Created on Tue Jun 12 12:11:41 2018

@author: guemruekcue
"""
import numpy as np
from CarParkOptimization.DynamicProgram import MinimizeImport

class CarPark():
    
    def __init__(self,systemParameters,dpParameters,markovModel,coef1,coef2):#,ess_capacity,vir_capacity):

        #self.T=opt_horizon              #Optimization horizon
        #self.ess_capacity=ess_capacity  #capacity of energy storage system: kWh 
        #self.vir_capacity=vir_capacity  #capacity of virtual EV battery
        
        self.systemParameters=systemParameters  #Parameters of physical system
        self.dpParameters=dpParameters          #Parameters of stochastic dynamic programming such as behavioral model
        
        self.markov=markovModel
        self.coef1=coef1
        self.coef2=coef2
        
        ##### Arrays for data handling for the optimization ####
        self.p_grid =np.zeros(self.systemParameters.T)
        self.p_pv   =np.zeros(self.systemParameters.T)
        self.p_ess  =np.zeros(self.systemParameters.T)
        self.p_vir  =np.zeros(self.systemParameters.T)
        self.soc_ess=np.zeros(self.systemParameters.T)
        self.soc_vir=np.zeros(self.systemParameters.T)
        
        
        #### Keep the stochastic dynamic program data at each time step####
        self.dp={}
        
    def updatePdfModel(self,hour,numberofdrivingcar):
        nexthourstats={}
        
        maxnbofcars=self.dpParameters.max_nb_of_cars
        
        #Next time step
        for drivingcar in range(maxnbofcars+1):
            nexthourstats[0,drivingcar]=self.markov[hour,numberofdrivingcar-drivingcar]
  
        #Following time steps
        for t in range(1,24):
            
            markovtime=t+hour if t+hour<24 else t+hour-24
            
            for fin_state in range(maxnbofcars+1):         
                nexthourstats[t,fin_state]=sum(nexthourstats[t-1,ini_state]*self.markov[markovtime,ini_state-fin_state] for ini_state in range(maxnbofcars+1))
        
        return nexthourstats
           
    def calculate_control_action(self,ts,realTimeData,load_forecast,pv_forecast,solver):
            
        new_pmfs=self.updatePdfModel(ts,realTimeData.carsAway)
        
        self.dp[ts]=MinimizeImport(self.systemParameters,self.dpParameters,load_forecast,pv_forecast,new_pmfs,solver,self.coef1,self.coef2)
        optimal_decisions=self.dp[ts].control_action(realTimeData.ess_soc,realTimeData.vir_soc)

        self.p_pv[ts]=optimal_decisions[0]
        self.p_grid[ts]=optimal_decisions[1]
        self.p_ess[ts]=optimal_decisions[2]
        self.p_vir[ts]=optimal_decisions[3]
        self.soc_ess[ts]=realTimeData.ess_soc
        self.soc_vir[ts]=realTimeData.vir_soc
               

        
