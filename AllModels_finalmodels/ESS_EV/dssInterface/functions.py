# -*- coding: utf-8 -*-
"""
Created on Thu Feb 22 09:22:16 2018

@author: guemruekcue
"""

from datetime import date, datetime, time, timedelta

def makelist(sortedlist):
    x, y = zip(*sortedlist)
    output=[]
    for value in y:
        output.append(value.value)
    return output
   
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

def controlOptimalStorage(dssText,batteryOutput):
    #pOut: Output power of the battery ---> dis: positive, ch: negative 
    
    powstr=getkWStorage(dssText)
    storageRatedkW=float(powstr)
    
    if batteryOutput>0: 
        dssText.Command = 'Storage.AtPVNode.%discharge ='+str(batteryOutput/storageRatedkW*100)
        dssText.Command = 'Storage.AtPVNode.State = Discharging';
    elif batteryOutput<0:
        dssText.Command = 'Storage.AtPVNode.%charge ='+str(-batteryOutput/storageRatedkW*100)
        dssText.Command = 'Storage.AtPVNode.State = Charging';

def controlPPV(dssText,modulation,powerfactor):
    dssText.Command ='PVSystem.PV_Menapace.pctPmpp ='+str(modulation*100)
    dssText.Command ='PVSystem.PV_Menapace.kvar =' +str(powerfactor)
