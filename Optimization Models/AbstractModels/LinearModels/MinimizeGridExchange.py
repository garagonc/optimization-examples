# -*- coding: utf-8 -*-
"""
Created on Wed Apr 11 14:42:11 2018

@author: guemruekcue
"""

from pyomo.environ import SolverFactory
from pyomo.core import *

class MinimizeGridExchange():
    """
    Class for the abstract optimization model
    Objective: Minimization of the grid exchange
    Solvers  : "bonmin","ipopt"
    """
    
    def __init__(self,parameterdictlist=None):    
        if parameterdictlist==None:
            self.abstractmodel=self.build_abstract_model_withoutParameters()
        else:
            timeInput=parameterdictlist[0]
            loadInput=parameterdictlist[1]
            pvInput=parameterdictlist[2]
            essInput=parameterdictlist[3]
            gridInput=parameterdictlist[4]
            marketInput=parameterdictlist[5]
            self.abstractmodel=self.build_abstract_model_withParameters(timeInput,loadInput,pvInput,essInput,gridInput,marketInput)
       
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
        for key in essInput.keys():
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
        
        
        model.dT=Param(initialize=Time_dT)                            #Number of seconds in one time step
        model.T=Set(initialize=set(range(0,Time_horizon)))                                   #Number of time steps in optimization horizon
        model.T_SoC=Set(initialize=set(range(0,Time_horizon+1)))                             #SoC of the ESSs at the end of optimization horizon are also taken into account
        model.N=Set(initialize=essInput.keys())
        
        ##################################       PARAMETERS            #################################
        
        model.P_Load_Forecast=Param(model.T,within=NonNegativeReals,initialize=Load_PForecast)#Active power demand forecast
        model.Q_Load_Forecast=Param(model.T,within=Reals,initialize=Load_QForecast)           #Reactive demand forecast
        
        model.P_PV_Forecast=Param(model.T,within=NonNegativeReals,initialize=PV_Forecast)     #PV PMPP forecast
        model.PV_Inv_Max_Power=Param(within=PositiveReals,initialize=PV_Inverter)             #PV inverter capacity
        
        model.ESS_Min_SoC=Param(model.N,within=PositiveReals,initialize=ESS_MinSoC)           #Minimum SoC of ESSs
        model.ESS_Max_SoC=Param(model.N,within=PositiveReals,initialize=ESS_MaxSoC)           #Maximum SoC of ESSs
        model.ESS_SoC_Value=Param(model.N,within=PositiveReals,initialize=ESS_IniSoC)         #SoC value of ESSs at the begining of optimization horizon
        model.ESS_Capacity=Param(model.N,within=PositiveReals,initialize=ESS_Capacity)        #Storage Capacity of ESSs
        model.ESS_Max_Charge_Power=Param(model.N,within=PositiveReals,initialize=ESS_MaxCh)   #Max Charge Power of ESSs
        model.ESS_Max_Discharge_Power=Param(model.N,within=PositiveReals,initialize=ESS_MaxDis)#Max Discharge Power of ESSs
        model.ESS_Charging_Eff=Param(model.N,within=PositiveReals,initialize=ESS_ChEff)       #Charging efficiency of ESSs
        model.ESS_Discharging_Eff=Param(model.N,within=PositiveReals,initialize=ESS_DisEff)   #Discharging efficiency of ESSs
        
        model.P_Grid_Max_Export_Power=Param(within=NonNegativeReals,initialize=Grid_P_Max_Exp)#Max active power export
        model.Q_Grid_Max_Export_Power=Param(within=NonNegativeReals,initialize=Grid_Q_Max_Exp)#Max reactive power export        
        
        model.Grid_VGEN=Param(within=NonNegativeReals,initialize=Grid_V_Nom)
        model.Grid_R=Param(within=NonNegativeReals,initialize=Grid_R)
        model.Grid_X=Param(within=NonNegativeReals,initialize=Grid_X)
        model.Grid_dV_Tolerance=Param(within=PositiveReals,initialize=Grid_dV)
        
        model.Price_Forecast=Param(model.T,initialize=Market_Forecast)                        #Electric price forecast
    
        
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
        
        

if __name__=="__main__":
    """
    #Building the optimization model
    optimizationmodel=MinimizeGridExchange()
    
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
    """
    
    #Constructing the dictionaries for the parameter setting
    timeInput={}
    timeInput['dT']=900
    timeInput['horizon']=24
    
    loadInput={}
    loadInput['P']={
            0:	0.057,
            1:	0.0906,
            2:	0.0906,
            3:	0.070066667,
            4:	0.077533333,
            5:	0.0906,
            6:	0.0906,
            7:	0.10935,
            8:	0.38135,
            9:	1.473716667,
            10:	0.988183333,
            11:	2.4413,
            12:	0.4216,
            13:	0.21725,
            14:	0.4536,
            15:	0.4899,
            16:	0.092466667,
            17:	0.088733333,
            18:	0.0906,
            19:	0.47475,
            20:	0.48255,
            21:	1.051866667,
            22:	1.296316667,
            23:	0.200733333}
    loadInput['Q']={
            0:	0.0,
            1:	0.0,
            2:	0.0,
            3:	0.0,
            4:	0.0,
            5:	0.0,
            6:	0.0,
            7:	0.0,
            8:	0.0,
            9:	0.0,
            10:	0.0,
            11:	0.0,
            12:	0.0,
            13:	0.0,
            14:	0.0,
            15:	0.0,
            16:	0.0,
            17:	0.0,
            18:	0.0,
            19:	0.0,
            20:	0.0,
            21:	0.0,
            22:	0.0,
            23:	0.0}
    
    pvInput={}
    pvInput['Pmpp']={
            0:	0,
            1:	0,
            2:	0,
            3:	0,
            4:	0,
            5:	0,
            6:	0,
            7:	0,
            8:	1.13248512,
            9:	3.016735616,
            10:4.823979947,
            11	:6.329861639,
            12	:7.06663104,
            13	:7.42742784,
            14	:7.420178035,
            15	:7.077290784,
            16	:5.99361984,
            17	:4.036273408,
            18	:1.462618829,
            19	:0,
            20	:0,
            21	:0,
            22	:0,
            23	:0}
    pvInput['Pmax']=10
    
    essInput={0:{}}
    essInput[0]['minSoC']=0.2
    essInput[0]['maxSoC']=0.9
    essInput[0]['iniSoC']=0.35
    essInput[0]['capacity']=9.6*3600
    essInput[0]['maxCh']=6.4
    essInput[0]['maxDis']=6.4
    essInput[0]['chargeEff']=0.9
    essInput[0]['chargeEff']=0.85
    
    gridInput={}
    gridInput['maxPExport']=10
    gridInput['maxQExport']=10
    gridInput['Vnom']=0.4
    gridInput['R']=0.67
    gridInput['X']=0.282
    gridInput['voltagedropTolerance']=0.1
    
    marketInput={}
    marketInput['elePrice']={
        0:   34.61,
        1:   33.28,
        2:   33.03,
        3:   32.93,
        4:   31.96,
        5:   33.67,
        6:   40.45,
        7:   47.16,
        8:   47.68,
        9:   46.23,
        10:  43.01,
        11:  39.86,
        12:  37.64,
        13:  37.14,
        14:  39.11,
        15:  41.91,
        16:  44.11,
        17:  48.02,
        18:  51.65,
        19:  48.73,
        20:  43.56,
        21:  38.31,
        22:  37.66,
        23:  36.31}
    
    dictlist=[timeInput,loadInput,pvInput,essInput,gridInput,marketInput]
    optimizationmodel=MinimizeGridExchange(dictlist)
    
    #Constructing an instance of optimzation model
    instance = optimizationmodel.abstractmodel.create_instance()
    
    #Solving the optimization problem
    opt=SolverFactory("ipopt")
    results=opt.solve(instance)
    
    #Printing the results
    print(results)
    
    