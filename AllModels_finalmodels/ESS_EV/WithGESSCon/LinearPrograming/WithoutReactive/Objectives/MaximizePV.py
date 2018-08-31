# -*- coding: utf-8 -*-
"""
Created on Thu Jun 21 13:44:42 2018

@author: guemruekcue
"""


from pyomo.environ import SolverFactory
from pyomo.core import *

class MaximizePVUtilization():
    """
    Class for the abstract optimization model
    Objective: Maximization of pv utilization
    Solvers  : "bonmin","ipopt"
    """
    
    def __init__(self,parameterdictlist=None):    
        if parameterdictlist==None:
            self.abstractmodel=self.build_abstract_model_withoutParameters()
        else:
            self.abstractmodel=self.build_abstract_model_withParameters()
       
    def build_abstract_model_withoutParameters(self):
        model = AbstractModel()

        model.N=Set()                                                   #Index Set for energy storage system devices
        model.T=Set()                                                   #Index Set for time steps of optimization horizon
        model.T_SoC=Set()                                               #SoC of the ESSs at the end of optimization horizon are also taken into account
        
        
        ##################################       PARAMETERS            #################################
        ################################################################################################                                               
        
        model.local_weight=Param(model.T,within=NonNegativeReals)
        model.global_weight=Param(model.T,within=NonNegativeReals)
        
        
        model.dT=Param(within=PositiveIntegers)                         #Number of seconds in one time step
        
        model.P_Load_Forecast=Param(model.T,within=NonNegativeReals)    #Active power demand forecast
        #TODO: Assign a default
        
        model.P_PV_Forecast=Param(model.T,within=NonNegativeReals)      #PV PMPP forecast
        model.PV_Inv_Max_Power=Param(within=PositiveReals)              #PV inverter capacity
        
        model.ESS_Min_SoC=Param(model.N,within=PositiveReals)           #Minimum SoC of ESSs
        model.ESS_Max_SoC=Param(model.N,within=PositiveReals)           #Maximum SoC of ESSs
        model.ESS_SoC_Value=Param(model.N,within=PositiveReals)         #SoC value of ESSs at the begining of optimization horizon
        model.ESS_Capacity=Param(model.N,within=PositiveReals)          #Storage Capacity of ESSs
        model.ESS_Max_Charge_Power=Param(model.N,within=PositiveReals)  #Max Charge Power of ESSs
        model.ESS_Max_Discharge_Power=Param(model.N,within=PositiveReals)#Max Discharge Power of ESSs
        model.ESS_Charging_Eff=Param(model.N,within=PositiveReals)      #Charging efficiency of ESSs
        model.ESS_Discharging_Eff=Param(model.N,within=PositiveReals)   #Discharging efficiency of ESSs
        
        model.P_Grid_Max_Export_Power=Param(within=NonNegativeReals)    #Max active power export
        
        model.Price_Forecast=Param(model.T)                             #Electric price forecast
        
        model.ESS_Command=Param(model.T,within=Reals)                   #DSO command for storage power
        
        ################################################################################################
        
        ##################################       VARIABLES             #################################
        ################################################################################################
        model.P_PV_Output=Var(model.T,within=NonNegativeReals,bounds=(0,model.PV_Inv_Max_Power))                                    #Active power output of PV
        model.P_Grid_Output=Var(model.T,within=Reals,bounds=(-model.P_Grid_Max_Export_Power,100000))  
        
        
        def ESS_Power_Bounds(model,n,t):
           return (-model.ESS_Max_Charge_Power[n], model.ESS_Max_Discharge_Power[n])
        model.P_ESS_Output = Var(model.N,model.T,within=Reals,bounds=ESS_Power_Bounds)
        
        def ESS_SOC_Bounds(model,n,t):
            return (model.ESS_Min_SoC[n], model.ESS_Max_SoC[n])
        model.SoC_ESS=Var(model.N,model.T_SoC,within=NonNegativeReals,bounds=ESS_SOC_Bounds)
                
        model.Deviation=Var(model.T)
        ################################################################################################
        
               
        ###########################################################################
        #######                         CONSTRAINTS                         #######
        #######                Rule1: P_power demand meeting                #######
        #######                Rule2: PV power limitation                   #######
        #######                Rule3: State of charge consistency           #######
        #######                Rule4: Initial State of charge               #######
        ###########################################################################
        def con_rule1(model,t):
            return model.P_Load_Forecast[t]==model.P_PV_Output[t]+ model.P_Grid_Output[t] + sum(model.P_ESS_Output[n,t] for n in model.N)  
        def con_rule2(model,t):
            return 0<=model.P_PV_Output[t]<=model.P_PV_Forecast[t]
        def con_rule3(model,n,t):
            return model.SoC_ESS[n,t+1]==model.SoC_ESS[n,t] - model.P_ESS_Output[n,t]*model.dT/model.ESS_Capacity[n]
        def con_rule4(model,n):
            return model.SoC_ESS[n,0]==model.ESS_SoC_Value[n]
        def con_rule5(model,t):
            return model.Deviation[t]==sum(model.P_ESS_Output[n,t] for n in model.N)-model.ESS_Command[t]
      
        model.con1=Constraint(model.T,rule=con_rule1)
        model.con2=Constraint(model.T,rule=con_rule2)
        model.con3=Constraint(model.N,model.T,rule=con_rule3)
        model.con4=Constraint(model.N,rule=con_rule4)
        model.con5=Constraint(model.T,rule=con_rule5)
        
        ###########################################################################
        #######                         OBJECTIVE                           #######
        ###########################################################################
        def obj_rule(model):  
            return sum(model.local_weight[t]*(model.P_PV_Forecast[t]-model.P_PV_Output[t])*(model.P_PV_Forecast[t]-model.P_PV_Output[t])
                       +model.global_weight[t]*model.Deviation[t]*model.Deviation[t] 
                       for t in model.T)
        model.obj=Objective(rule=obj_rule, sense = minimize)    
        
        return model

    
    def calculateOptimalTrajectory(self,data_file,solver):
        """
        Solves the optimization problem for given data_file
        """
        instance=self.abstractmodel.create_instance(data_file)
        solver.solve(instance)
        
        self.P_PV=[]
        self.P_ESS=dict.fromkeys(instance.N,[])
        self.P_GRID=[]
        
        for t in instance.T:
            self.P_PV.append(instance.P_PV_Output[t]())
            self.P_GRID.append(instance.P_Grid_Output[t]())
            for n in instance.N:
                self.P_ESS[n].append(instance.P_ESS_Output[n,t]())
                     

if __name__=="__main__":
    
    #Building the optimization model
    optimizationmodel=MaximizePVUtilization()
    opt1=SolverFactory('glpk',executable="C:/Users/guemruekcue/Anaconda3/pkgs/glpk-4.63-vc14_0/Library/bin/glpsol")
    opt2= SolverFactory("ipopt", executable="C:/Users/guemruekcue/Anaconda3/pkgs/ipopt-3.11.1-2/Library/bin/ipopt")
    opt3= SolverFactory("bonmin", executable="C:/cygwin/home/bonmin/Bonmin-1.8.6/build/bin/bonmin")
  
    #Loading the data file
    import os
    import time
    project_dir=os.path.dirname(__file__)
    data_file=project_dir+'/Scenario1.dat'
        
    #Constructing an instance of optimzation model
    start_time=time.time()
    optimizationmodel.calculateOptimalTrajectory(data_file,opt3)
    end_time=time.time()
    print("Computation time:",end_time-start_time,"seconds")
    
    with open('linear_MaximizePV.csv','w') as file:
        for ts in range(24):
            file.write(str(optimizationmodel.P_PV[ts]))
            file.write(",")
            file.write(str(optimizationmodel.P_ESS[0][ts]))
            file.write(",")
            file.write(str(optimizationmodel.P_GRID[ts]))
            file.write('\n')
    

    