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
import numpy as np

def makelist(sortedlist):
    x, y = zip(*sortedlist)
    output=[]
    for value in y:
        output.append(value.value)
    return output

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
    P_power=dssPVsystems.kw
    Q_power=dssPVsystems.kvar
    return P_power,Q_power

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

def controlPPV(dssText,modulation,powerfactor):
    dssText.Command ='PVSystem.PV_Menapace.pctPmpp ='+str(modulation*100)
    dssText.Command ='PVSystem.PV_Menapace.kvar =' +str(powerfactor)
    
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
        Pdem = []
        Qdem = []
        PV = []
        N=len(linesLoad)
        for i in keys:
            Pdem.append(float(linesLoad[i]))
            Qdem.append(float(linesLoad[i])*0.312)  #PF=0.95
            PV.append(float(linesPV[i]))
                      
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
    
    R=0.67                              #TODO: Choose by pointing the circuit
    X=0.282
    VGEN=0.4
       
    model = ConcreteModel()
    model.lengthSoC=RangeSet(0,N)
    model.horizon=RangeSet(0,N-1)
 
    model.PBAT= Var(model.horizon,bounds=(-storageRatedkW,storageRatedkW),initialize=0)
    
    model.PGRID=Var(model.horizon,bounds=(-10.0,10.0),initialize=0)
    model.QGRID=Var(model.horizon,bounds=(-10.0,10.0),initialize=0)
    
    model.Ppv=Var(model.horizon,initialize=0)
    model.Qpv=Var(model.horizon,initialize=0)
    
                         
    model.SoC=Var(model.lengthSoC,bounds=(socMin,socMax))
    model.dV=Var(model.horizon)#,bounds=(-0.2,0.2))
    
    ###########################################################################
    #######                         OBJECTIVE                           #######
    ###########################################################################
    def obj_rule(model):
        if target==1:   #Minimum exchange with grid    
            return sum(model.PGRID[m]*model.PGRID[m] for m in model.horizon)
        elif target==2: #Maximum utilization of PV potential
            return sum(PV[m]-model.Ppv[m] for m in model.horizon)
        elif target==3: #Minimum electricity bill
            return sum(price[m]*model.PGRID[m] for m in model.horizon)
        elif target==4: #Minimum voltage drop
            return sum(model.dV[m]*model.dV[m] for m in model.horizon)           
    model.obj=Objective(rule=obj_rule, sense = minimize)
        
    ###########################################################################
    #######                         CONSTRAINTS                         #######
    #######                Rule1: P_power demand meeting                #######
    #######                Rule2: Q_power demand meeting                #######
    #######                Rule3: State of charge consistency           #######
    #######                Rule4: Initial State of charge               #######
    #######                Rule5: ppv+j.qpv <= PB                       #######  
    #######                Rule6: Voltage drop                          #######
    ###########################################################################
    def con_rule1(model,m):
        return Pdem[m]==model.Ppv[m]+ model.PGRID[m] + model.PBAT[m]  
    def con_rule2(model,m):
        return Qdem[m]==model.Qpv[m]+ model.QGRID[m] 
    def con_rule3(model,m):
        return model.SoC[m+1]==model.SoC[m] - model.PBAT[m]*dT/storageCapacity 
    def con_rule4(model):
        return model.SoC[0]==initialSOC
    def con_rule5(model,m):
        return model.Ppv[m]*model.Ppv[m]+model.Qpv[m]*model.Qpv[m] <= PV[m]*PV[m]
    def con_rule6(model,m):
        return model.dV[m]==(R*model.PGRID[m]+X*model.QGRID[m])/VGEN
    
    model.con1=Constraint(model.horizon,rule=con_rule1)
    model.con2=Constraint(model.horizon,rule=con_rule2)
    model.con3=Constraint(model.horizon,rule=con_rule3)
    model.con4=Constraint(rule=con_rule4)
    model.con5=Constraint(model.horizon,rule=con_rule5)
    model.con6=Constraint(model.horizon,rule=con_rule6)
    
    ###########################################################################
    #######                         SOLVING                             #######
    ###########################################################################
    result=solver.solve(model)
    print(result)
    
    listPpv=sorted(model.Ppv.items()) 
    listQpv=sorted(model.Qpv.items()) 
    listsPStorageP = sorted(model.PBAT.items()) 
    listsSOC= sorted(model.SoC.items()) 
    listsPImport = sorted(model.PGRID.items())
    listsQImport = sorted(model.QGRID.items())  
    listsdV= sorted(model.dV.items())
    
    ppv=makelist(listPpv)
    qpv=makelist(listQpv)
    Pbat=makelist(listsPStorageP)
    soc=makelist(listsSOC)
    Pimp=makelist(listsPImport)
    Qimp=makelist(listsQImport)
    vdrop=makelist(listsdV)
    
    x=range(len(linesPV))
    pf=[0 if ppv[m]==0 else np.cos(np.arctan(qpv[m]/ppv[m])) for m in x]
    
    dataframe=pandas.DataFrame(data={'SOC':soc[0:len(x)],'dV':vdrop,'importP':Pimp,'importQ':Qimp,'dem':Pdem,'PVpot':PV,'PVp':ppv,'PVq':qpv})
    
    return Pbat,ppv,pf,PV,dataframe    
