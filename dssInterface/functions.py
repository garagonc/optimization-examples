# -*- coding: utf-8 -*-
"""
Created on Thu Feb 22 09:22:16 2018

@author: guemruekcue
"""

import pandas
from datetime import date, datetime, time, timedelta
from pyomo.environ import *
from pyomo.core import *
from pyomo.opt import SolverFactory


def thresholdPowerStorage(dssText,dss_circuit_load,charge=0.4,discharge=0.8):
    char_var=charge
    dis_var=discharge
    if dss_circuit_load <= char_var: 
        dssText.Command = 'Storage.AtPVNode.State = Charging';
        dssText.Command = '? Storage.AtPVNode.state';
        kwTarget_storage = "A:Charging R:" + dssText.Result;
        dssText.Command = '? Storage.AtPVNode.%stored'
        stored_storage = "%stored:" + dssText.Result
        return (kwTarget_storage,stored_storage,dss_circuit_load)
    elif dss_circuit_load >= dis_var:
        dssText.Command = 'Storage.AtPVNode.State = Discharging';
        dssText.Command = '? Storage.AtPVNode.state';
        kwTarget_storage = "A:Disharging R:" + dssText.Result;
        dssText.Command = '? Storage.AtPVNode.%stored'
        stored_storage = "%stored:" + dssText.Result
        return (kwTarget_storage,stored_storage,dss_circuit_load)
    else:
        dssText.Command = 'Storage.AtPVNode.State = Idling';
        dssText.Command = '? Storage.AtPVNode.state';
        kwTarget_storage = "A:NK R:" + dssText.Result;
        dssText.Command = '? Storage.AtPVNode.%stored'
        stored_storage = "%stored:" + dssText.Result
        return (kwTarget_storage,stored_storage,dss_circuit_load)

def thresholdVolStorage(dssText,dss_bus_volt,charge=1.02,discharge=0.98):
    char_var=charge
    dis_var=discharge
    if dss_bus_volt >= char_var: 
        dssText.Command = 'Storage.AtPVNode.State = Charging';
        dssText.Command = '? Storage.AtPVNode.state';
        kwTarget_storage = "A:Charging R:" + dssText.Result;
        return (kwTarget_storage,dss_bus_volt)
    elif dss_bus_volt <= dis_var:
        dssText.Command = 'Storage.AtPVNode.State = Discharging';
        dssText.Command = '? Storage.AtPVNode.state';
        kwTarget_storage = "A:Disharging R:" + dssText.Result;
        return (kwTarget_storage,dss_bus_volt)
    else:
        dssText.Command = 'Storage.AtPVNode.State = Idling';
        dssText.Command = '? Storage.AtPVNode.state';
        kwTarget_storage = "A:NK R:" + dssText.Result;
        return (kwTarget_storage,dss_bus_volt)
    
def saveArrayInExcel(array,directory,name_of_file="Standard"):
    dfName=pandas.DataFrame(array)
    writer = pandas.ExcelWriter(directory + name_of_file +'.xlsx', engine='xlsxwriter')
    dfName.to_excel(writer, sheet_name='Sheet 1')
    writer.save()
    return 1

def getLoadskw(dssCircuit,dssLoads,dssCktElement):
    dssLoads.first
    array=[]
    array.append(getTime(dssCircuit))
    while True:
        name=dssLoads.Name
        kW=dssCktElement.seqpowers[2]
        array.append(name)
        array.append(kW)
        if not dssLoads.Next > 0:
            break
    return array

def getLoadkwNo(dssLoads,dssCktElement,number):
    dssLoads.Name=number
    return dssCktElement.seqpowers[2]

def getPowerIntoNo(dssLoads,dssCktElement,number):
    dssLoads.Name=number
    return dssCktElement.Powers

def getTime(dssCircuit):
    return dssCircuit.Solution.dblHour

def getPVPower(dssPVsystems,PV_name):
    dssPVsystems.Name=PV_name
    PV_power=dssPVsystems.kw
    return PV_power

def getStoredStorage(dssText):
    dssText.Command = '? Storage.AtPVNode.%stored'
    stored_storage = dssText.Result
    return stored_storage

def getStoredStorage(dssText):
    dssText.Command = '? Storage.AtPVNode.%stored'
    stored_storage = dssText.Result
    return stored_storage

def getkWStorage(dssText):
    dssText.Command = '? Storage.AtPVNode.kWrated'
    kW_storage = dssText.Result
    return kW_storage

def getkWhStorage(dssText):
    dssText.Command = '? Storage.AtPVNode.kWhrated'
    kWh_storage= dssText.Result
    return kWh_storage

def controlRasmusStorage(dssText,SoC_Battery,PV_power, dss_circuit_load):
    low_load=0.4
    high_load=2
    low_SoC=40
    high_SoC=80
    PV_low=0.4
    PV_high=0.7
    circuit_power=float(dss_circuit_load)
    
    if (PV_power >= circuit_power) and (float(SoC_Battery) <= high_SoC):
        dssText.Command = 'Storage.AtPVNode.State = Charging';
        dssText.Command = '? Storage.AtPVNode.state';
        kwTarget_storage = "A:Charging R:" + dssText.Result;
        return (kwTarget_storage, SoC_Battery,PV_power,dss_circuit_load) 
    
    elif (PV_power >= circuit_power):
        dssText.Command = 'Storage.AtPVNode.State = Idling';
        dssText.Command = '? Storage.AtPVNode.state';
        kwTarget_storage = "A:Charging R:" + dssText.Result;
        return (kwTarget_storage, SoC_Battery,PV_power,dss_circuit_load)
    
    elif (PV_power <= circuit_power) and (float(SoC_Battery) <= low_SoC):
        dssText.Command = 'Storage.AtPVNode.State = Idling';
        dssText.Command = '? Storage.AtPVNode.state';
        kwTarget_storage = "A:Disharging R:" + dssText.Result;
        return (kwTarget_storage, SoC_Battery,PV_power,dss_circuit_load)
    
    elif (PV_power <= circuit_power):
        dssText.Command = 'Storage.AtPVNode.State = Discharging';
        dssText.Command = '? Storage.AtPVNode.state';
        kwTarget_storage = "A:Disharging R:" + dssText.Result;
        return (kwTarget_storage, SoC_Battery,PV_power,dss_circuit_load)
    
    else:
        dssText.Command = 'Storage.AtPVNode.State = Idling';
        dssText.Command = '? Storage.AtPVNode.state';
        kwTarget_storage = "A:NK R:" + dssText.Result;
        dssText.Command = '? Storage.AtPVNode.%stored'
        stored_storage = "%stored:" + dssText.Result
        return (kwTarget_storage,stored_storage,dss_circuit_load)

def controlOptimalStorage(dssText,SoC_Battery,PV_power, dss_circuit_load,batteryOutput,utilPV):
    #pOut: Output power of the battery ---> dis: positive, ch: negative 
    
    powstr=getkWStorage(dssText)
    storageRatedkW=float(powstr)
    
    if batteryOutput>0: 
        dssText.Command = 'Storage.AtPVNode.%discharge ='+str(batteryOutput/storageRatedkW*100)
        dssText.Command = 'Storage.AtPVNode.State = Discharging';
        dssText.Command = '? Storage.AtPVNode.state';
        kwTarget_storage = "A:Discharging R:" + dssText.Result;
        dssText.Command = '? Storage.AtPVNode.%discharge';
        dischargepower= dssText.Result;
        dssText.Command = '? Storage.AtPVNode.%charge';
        chargepower= dssText.Result;        
        return (kwTarget_storage, SoC_Battery,PV_power,dss_circuit_load,batteryOutput,utilPV)          
    elif batteryOutput<0:
        dssText.Command = 'Storage.AtPVNode.%charge ='+str(-batteryOutput/storageRatedkW*100)
        dssText.Command = 'Storage.AtPVNode.State = Charging';
        dssText.Command = '? Storage.AtPVNode.state';
        kwTarget_storage = "A:Charging R:" + dssText.Result;
        dssText.Command = '? Storage.AtPVNode.%discharge';
        dischargepower= dssText.Result;
        dssText.Command = '? Storage.AtPVNode.%charge';
        chargepower= dssText.Result;   
        return (kwTarget_storage, SoC_Battery,PV_power,dss_circuit_load,batteryOutput,utilPV)   
    else:
        dssText.Command = 'Storage.AtPVNode.State = Idling';
        dssText.Command = '? Storage.AtPVNode.state';
        kwTarget_storage = "A:NK R:" + dssText.Result;
        dssText.Command = '? Storage.AtPVNode.%stored'
        stored_storage = "%stored:" + dssText.Result
        dssText.Command = '? Storage.AtPVNode.%discharge';
        dischargepower= dssText.Result;
        dssText.Command = '? Storage.AtPVNode.%charge';
        chargepower= dssText.Result;   
        return (kwTarget_storage,stored_storage,PV_power,dss_circuit_load,batteryOutput,utilPV)


def controlPPV(dssText,modulation):
    dssText.Command ='PVSystem.PV_Menapace.pctPmpp ='+str(modulation*100)
    
    
def optimizeSelfConsumptionL(dssText,loadForecast,pvForecast,priceForecast,solver,timediscretization,target=1,socMin=0.20,socMax=0.95):
    
    ###########################################################################
    #######                  Read data from forecast files              #######
    ###########################################################################
    
    file_load = open(loadForecast, 'r')
    file_PV = open(pvForecast, 'r')
    file_price = open(priceForecast, 'r')      
    linesLoad = file_load.read().splitlines()
    linesPV = file_PV.read().splitlines()
    linesPrice = file_price.read().splitlines()
    
    if len(linesLoad)==len(linesPV):
        keys=range(len(linesPV))
        Pdem = {}
        PV = {}
        N=len(linesLoad)
        for i in keys:
            Pdem[keys[i]]=float(linesLoad[i])
            PV[keys[i]]=float(linesPV[i])
                      
    price=[]
    for row in linesPrice:
        price=price+[float(row)]*timediscretization


    ###########################################################################
    #######                  Parameters and Variables                   #######
    ###########################################################################
    socstr=getStoredStorage(dssText)
    captstr=getkWhStorage(dssText)
    powstr=getkWStorage(dssText)
    
    initialSOC=float(socstr)/100        #Percentage
    storageCapacity=float(captstr)*3600 #kWh
    storageRatedkW=float(powstr)
    dT=timediscretization
    N=1440                              #TODO: Choose via function argument
       
    model = ConcreteModel()
    model.lengthSoC=RangeSet(0,N)
    model.horizon=RangeSet(0,N-1)
    model.PBAT= Var(model.horizon,bounds=(-storageRatedkW,storageRatedkW),initialize=0)    
    model.PGRID=Var(model.horizon,initialize=0)                      
    model.SoC=Var(model.lengthSoC,bounds=(socMin,socMax))
    model.PVmod=Var(model.horizon,bounds=(0,1),initialize=1)
    
    ###########################################################################
    #######                         OBJECTIVE                           #######
    ###########################################################################
    def obj_rule(model):
        if target==1:   #Minimum exchange with grid    
            return sum(model.PGRID[m]*model.PGRID[m] for m in model.horizon)
        elif target==2: #Maximum utilization of PV potential
            return sum((1-model.PVmod[m])*PV[m] for m in model.horizon)
        elif target==3: #Minimum electricity bill
            return sum(price[m]*model.PGRID[m] for m in model.horizon)            
    model.obj=Objective(rule=obj_rule, sense = minimize)
        
    ###########################################################################
    #######                         CONSTRAINTS                         #######
    #######                Rule1: Power demand meeting                  #######
    #######                Rule2: State of charge consistency           #######
    #######                Rule3: Initial State of charge               #######
    ###########################################################################
    def con_rule1(model,m):
        return Pdem[m]==model.PVmod[m]*PV[m] + model.PBAT[m] + model.PGRID[m] 
    def con_rule2(model,m):
        return model.SoC[m+1]==model.SoC[m] - model.PBAT[m]*dT/storageCapacity 
    def con_rule3(model):
        return model.SoC[0]==initialSOC
    
    model.con1=Constraint(model.horizon,rule=con_rule1)
    model.con2=Constraint(model.horizon,rule=con_rule2)
    model.con3=Constraint(rule=con_rule3)

    ###########################################################################
    #######                         SOLVING                             #######
    ###########################################################################
    result=solver.solve(model)
    print(result)
    
    listsPStorageP = sorted(model.PBAT.items())
    x, y = zip(*listsPStorageP)
    PStorage=[]
    for value in y:
        PStorage.append(value.value)
        
    listsPVUtil = sorted(model.PVmod.items())
    x, y = zip(*listsPVUtil)
    PVUtil=[]
    for value in y:
        PVUtil.append(value.value)    

    return PStorage,PVUtil,model    
