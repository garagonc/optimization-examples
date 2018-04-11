# -*- coding: utf-8 -*-
"""
Created on Wed Apr 11 16:38:45 2018

@author: guemruekcue
"""

from pyomo.environ import SolverFactory
from pyomo.core import *

class MinimizePowerBill():
    """
    Class for the abstract optimization model
    Objective: Minimization of the electric power bill
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
        
        model.dT=Param(within=PositiveIntegers)                         #Number of seconds in one time step
        
        model.P_Load_Forecast=Param(model.T,within=NonNegativeReals)    #Active power demand forecast
        model.Q_Load_Forecast=Param(model.T,within=Reals)               #Reactive demand forecast
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
        model.Q_Grid_Max_Export_Power=Param(within=NonNegativeReals)    #Max reactive power export
        
        model.Price_Forecast=Param(model.T)                             #Electric price forecast
        
        
        model.Grid_VGEN=Param(within=NonNegativeReals)
        model.Grid_R=Param(within=NonNegativeReals)
        model.Grid_X=Param(within=NonNegativeReals)
        model.Grid_dV_Tolerance=Param(within=PositiveReals)      
        ################################################################################################
        
        ##################################       VARIABLES             #################################
        ################################################################################################
        model.P_PV_Output=Var(model.T,within=NonNegativeReals,bounds=(0,model.PV_Inv_Max_Power))                                    #Active power output of PV
        model.Q_PV_Output=Var(model.T,within=Reals,bounds=(-model.PV_Inv_Max_Power,model.PV_Inv_Max_Power))                         #Reactive power output of PV
        
        def ESS_Power_Bounds(model,n,t):
           return (-model.ESS_Max_Charge_Power[n], model.ESS_Max_Discharge_Power[n])
        model.P_ESS_Output = Var(model.N,model.T,within=Reals,bounds=ESS_Power_Bounds)
        
        def ESS_SOC_Bounds(model,n,t):
            return (model.ESS_Min_SoC[n], model.ESS_Max_SoC[n])
        model.SoC_ESS=Var(model.N,model.T_SoC,within=NonNegativeReals,bounds=ESS_SOC_Bounds)
        
        
        model.P_Grid_Output=Var(model.T,within=Reals,bounds=(-model.P_Grid_Max_Export_Power,100000))                                 #Active power exchange with grid
        model.Q_Grid_Output=Var(model.T,within=Reals,bounds=(-model.Q_Grid_Max_Export_Power,100000))                                 #Reactive power exchange with grid
        
        model.dV=Var(model.T,within=Reals,bounds=(-model.Grid_dV_Tolerance,model.Grid_dV_Tolerance))       
        ################################################################################################
        
               
        ###########################################################################
        #######                         CONSTRAINTS                         #######
        #######                Rule1: P_power demand meeting                #######
        #######                Rule2: Q_power demand meeting                #######
        #######                Rule3: State of charge consistency           #######
        #######                Rule4: Initial State of charge               #######
        #######                Rule5: ppv+j.qpv <= PB                       #######  
        #######                Rule6: Voltage drop                          #######
        ###########################################################################
        def con_rule1(model,t):
            return model.P_Load_Forecast[t]==model.P_PV_Output[t]+ model.P_Grid_Output[t] + sum(model.P_ESS_Output[n,t] for n in model.N)  
        def con_rule2(model,t):
            return model.Q_Load_Forecast[t]==model.Q_PV_Output[t]+ model.Q_Grid_Output[t] 
        def con_rule3(model,n,t):
            return model.SoC_ESS[n,t+1]==model.SoC_ESS[n,t] - model.P_ESS_Output[n,t]*model.dT/model.ESS_Capacity[n]
        def con_rule4(model,n):
            return model.SoC_ESS[n,0]==model.ESS_SoC_Value[n]
        def con_rule5(model,t):
            return model.P_PV_Output[t]*model.P_PV_Output[t]+model.Q_PV_Output[t]*model.Q_PV_Output[t] <= model.P_PV_Forecast[t]*model.P_PV_Forecast[t]
        def con_rule6(model,t):
            return model.dV[t]==(model.Grid_R*model.P_Grid_Output[t]+model.Grid_X*model.Q_Grid_Output[t])/model.Grid_VGEN
        
        model.con1=Constraint(model.T,rule=con_rule1)
        model.con2=Constraint(model.T,rule=con_rule2)
        model.con3=Constraint(model.N,model.T,rule=con_rule3)
        model.con4=Constraint(model.N,rule=con_rule4)
        model.con5=Constraint(model.T,rule=con_rule5)
        model.con6=Constraint(model.T,rule=con_rule6)
        
        ###########################################################################
        #######                         OBJECTIVE                           #######
        ###########################################################################
        def obj_rule(model):  
            return sum(model.P_Grid_Output[t]*model.P_Grid_Output[t]+model.Q_Grid_Output[t]*model.Q_Grid_Output[t] for t in model.T)
        model.obj=Objective(rule=obj_rule, sense = minimize)    
        
        return model        
        
    """
    def build_abstract_model_withParameters(self,timeInput,loadInput,pvInput,essInput,gridInput,marketInput):
        
        Time_dT=timeInput['dT']
        Time_horizon=timeInput['horizon']
        Load_PForecast=loadInput['P']
        Load_QForecast=loadInput['Q'] if loadInput['Q']!=None else 0.95 #defaultPF
        PV_Forecast=pvInput['Pmpp']
        PV_Inverter=pvInput['Pmax']
        ESS_MinSoC={}
        ESS_MaxSoC={}
        ESS_IniSoC={}
        ESS_Capacity={}
        ESS_MaxCh={}
        ESS_MaxDis={}
        ESS_ChEff={}
        ESS_DisEff={}
        for key in essInput.keys()
            ESS_MinSoC[key]=essInput[key]['minSoC']
            ESS_MaxSoC[key]=essInput[key]['maxSoC']
            ESS_IniSoC[key]=essInput[key]['iniSoC']
            ESS_Capacity[key]=essInput[key]['capacity']
            ESS_MaxCh[key]=essInput[key]['maxCh']
            ESS_MaxDis[key]=essInput[key]['maxDis']
            ESS_ChEff[key]=essInput[key]['chargeEff']
            ESS_DisEff[key]=essInput[key]['chargeEff']
        Grid_P_Max_Exp=gridInput['maxPExport']
        Grid_Q_Max_Exp=gridInput['maxQExport']
        Grid_V_Nom=gridInput['Vnom']
        Grid_R=gridInput['R']
        Grid_X=gridInput['X']
        Grid_dV=gridInput['voltagedropTolerance']
        Market_Forecast=marketInput['elePrice']

        model = AbstractModel()        
        
        
        model.dT=Param(within=PositiveIntegers,initalize=Time_dT)                            #Number of seconds in one time step
        model.T=Set(initialize=set(range(0,Time_horizon)))                                   #Number of time steps in optimization horizon
        model.T_SoC=Set(initialize=set(range(0,Time_horizon+1)))                             #SoC of the ESSs at the end of optimization horizon are also taken into account
        
        ##################################       PARAMETERS            #################################
        
        model.P_Load_Forecast=Param(model.T,within=NonNegativeReals,initalize=Load_PForecast)#Active power demand forecast
        model.Q_Load_Forecast=Param(model.T,within=Reals,initalize=Load_QForecast)           #Reactive demand forecast
        
        model.P_PV_Forecast=Param(model.T,within=NonNegativeReals,initalize=PV_Forecast)     #PV PMPP forecast
        model.PV_Inv_Max_Power=Param(within=PositiveReals,initalize=PV_Inverter)             #PV inverter capacity
        
        model.ESS_Min_SoC=Param(model.N,within=PositiveReals,initalize=ESS_MinSoC)           #Minimum SoC of ESSs
        model.ESS_Max_SoC=Param(model.N,within=PositiveReals,initalize=ESS_MaxSoC)           #Maximum SoC of ESSs
        model.ESS_SoC_Value=Param(model.N,within=PositiveReals,initalize=ESS_IniSoC)         #SoC value of ESSs at the begining of optimization horizon
        model.ESS_Capacity=Param(model.N,within=PositiveReals,initalize=ESS_Capacity)        #Storage Capacity of ESSs
        model.ESS_Max_Charge_Power=Param(model.N,within=PositiveReals,initalize=ESS_MaxCh)   #Max Charge Power of ESSs
        model.ESS_Max_Discharge_Power=Param(model.N,within=PositiveReals,initalize=ESS_MaxDis)#Max Discharge Power of ESSs
        model.ESS_Charging_Eff=Param(model.N,within=PositiveReals,initalize=ESS_ChEff)       #Charging efficiency of ESSs
        model.ESS_Discharging_Eff=Param(model.N,within=PositiveReals,initalize=ESS_DisEff)   #Discharging efficiency of ESSs
        
        model.P_Grid_Max_Export_Power=Param(within=NonNegativeReals,initalize=Grid_P_Max_Exp)#Max active power export
        model.Q_Grid_Max_Export_Power=Param(within=NonNegativeReals,initalize=Grid_Q_Max_Exp)#Max reactive power export        
        
        model.Grid_VGEN=Param(within=NonNegativeReals,initalize=Grid_V_Nom)
        model.Grid_R=Param(within=NonNegativeReals,initalize=Grid_R)
        model.Grid_X=Param(within=NonNegativeReals,initalize=Grid_X)
        model.Grid_dV_Tolerance=Param(within=PositiveReals,initalize=Grid_dV)
        
        model.Price_Forecast=Param(model.T,initalize=Market_Forecast)                        #Electric price forecast
    
        
        ##################################       VARIABLES             #################################
        
        model.P_PV_Output=Var(model.T,within=NonNegativeReals,bounds=(0,model.PV_Inv_Max_Power))           #Active power output of PV
        model.Q_PV_Output=Var(model.T,within=Reals,bounds=(-model.PV_Inv_Max_Power,model.PV_Inv_Max_Power))#Reactive power output of PV


        def ESS_Power_Bounds(model,n,t):
            return (-model.ESS_Max_Charge_Power[n], model.ESS_Max_Discharge_Power[n])
        model.P_ESS_Output = Var(model.N,model.T,within=Reals,bounds=ESS_Power_Bounds)

        def ESS_SOC_Bounds(model,n,t):
            return (model.ESS_Min_SoC[n], model.ESS_Max_SoC[n])
        model.SoC_ESS=Var(model.N,model.T_SoC,within=NonNegativeReals,bounds=ESS_SOC_Bounds)


        model.P_Grid_Output=Var(model.T,within=Reals,bounds=(-model.P_Grid_Max_Export_Power,100000))    #Active power exchange with grid
        model.Q_Grid_Output=Var(model.T,within=Reals,bounds=(-model.Q_Grid_Max_Export_Power,100000))    #Reactive power exchange with grid

        model.dV=Var(model.T,within=Reals,bounds=(-model.Grid_dV_Tolerance,model.Grid_dV_Tolerance))
        
        
        ##################################       CONSTRAINTS             #################################
        def con_rule1(model,t):
            return model.P_Load_Forecast[t]==model.P_PV_Output[t]+ model.P_Grid_Output[t] + sum(model.P_ESS_Output[n,t] for n in model.N)  
        def con_rule2(model,t):
            return model.Q_Load_Forecast[t]==model.Q_PV_Output[t]+ model.Q_Grid_Output[t] 
        def con_rule3(model,n,t):
            return model.SoC_ESS[n,t+1]==model.SoC_ESS[n,t] - model.P_ESS_Output[n,t]*model.dT/model.ESS_Capacity[n]
        def con_rule4(model,n):
            return model.SoC_ESS[n,0]==model.ESS_SoC_Value[n]
        def con_rule5(model,t):
            return model.P_PV_Output[t]*model.P_PV_Output[t]+model.Q_PV_Output[t]*model.Q_PV_Output[t] <= model.P_PV_Forecast[t]*model.P_PV_Forecast[t]
        def con_rule6(model,t):
            return model.dV[t]==(model.Grid_R*model.P_Grid_Output[t]+model.Grid_X*model.Q_Grid_Output[t])/model.Grid_VGEN
        
        model.con1=Constraint(model.T,rule=con_rule1)
        model.con2=Constraint(model.T,rule=con_rule2)
        model.con3=Constraint(model.N,model.T,rule=con_rule3)
        model.con4=Constraint(model.N,rule=con_rule4)
        model.con5=Constraint(model.T,rule=con_rule5)
        model.con6=Constraint(model.T,rule=con_rule6)

        #######                         OBJECTIVE                           #######
        def obj_rule(model):
            return sum(model.P_Grid_Output[t]*model.P_Grid_Output[t]+model.Q_Grid_Output[t]*model.Q_Grid_Output[t] for t in model.T)
        model.obj=Objective(rule=obj_rule, sense = minimize)    
        
        return model
        
        """

if __name__=="__main__":
    
    #Building the optimization model
    optimizationmodel=MinimizePowerBill()
    
    #Loading the data file
    import os
    project_dir=os.path.dirname(__file__)
    data_file=project_dir+'/Scenario1.dat'
    
    #Constructing an instance of optimzation model
    instance = optimizationmodel.abstractmodel.create_instance(data_file)
    
    #Solving the optimization problem
    opt=SolverFactory("ipopt")
    results=opt.solve(instance)
    
    #Printing the results
    print(results)
    