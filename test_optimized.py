# -*- coding: utf-8 -*-
"""
Created on Wed Feb  7 09:14:54 2018

@author: guemruekcue
"""

import random

import win32com.client
import pandas
import matplotlib.pyplot as plt
import glob, os
from datetime import date, datetime, time, timedelta

from pyomo.environ import *
from pyomo.opt import SolverFactory

###########################################################################
#######               Functions
############################################################################
def saveArrayInExcel(array,directory,name_of_file="Standard"):
    dfName=pandas.DataFrame(array)
    # Create a Pandas Excel writer using XlsxWriter as the engine.
    writer = pandas.ExcelWriter(directory + name_of_file +'.xlsx', engine='xlsxwriter')
    # Convert the dataframe to an XlsxWriter Excel object.
    dfName.to_excel(writer, sheet_name='Sheet 1')
    # Close the Pandas Excel writer and output the Excel file.
    writer.save()
    return 1

def getTime():
    return dssCircuit.Solution.dblHour

def getLoadskw():
    dssLoads.first
    array=[]
    array.append(getTime())
    while True:
        name=dssLoads.Name
        #kW=dssLoads.kw#dssPowers(1)
        kW=dssCktElement.seqpowers[2]
        array.append(name)
        array.append(kW)
       # print(
        #        'Name={name} \t kW={kW}'.format(
         #      name=dssLoads.Name,
         #      kW=dssLoads.kW
         #      )
         #       )
        if not dssLoads.Next > 0:
            break
    return array

def getLoadkwNo(number):
    dssLoads.Name=number
    return dssCktElement.seqpowers[2]

def getPVPower(PV_name):
    dssPVsystems.Name=PV_name
    PV_power=dssPVsystems.kw
    return PV_power

def getStoredStorage():
    dssText.Command = '? Storage.AtPVNode.%stored'
    stored_storage = dssText.Result
    return stored_storage

def getkWStorage():
    dssText.Command = '? Storage.AtPVNode.kWrated'
    kW_storage = dssText.Result
    return kW_storage

def getkWhStorage():
    dssText.Command = '? Storage.AtPVNode.kWhrated'
    kWh_storage= dssText.Result
    return kWh_storage

def optimizeZero(loadForecast,pvForecast,solver):
    
    ###########################################################################
    #######                  Read data from forecast files              #######
    ###########################################################################
    
    file_load = open(loadForecast, 'r')
    file_PV = open(pvForecast, 'r')       
    linesLoad = file_load.read().splitlines()
    linesPV = file_PV.read().splitlines()
    
    if len(linesLoad)==len(linesPV):
        keys=range(len(linesPV))
        Pdem = {}
        PV = {}
        N=len(linesLoad)
        for i in keys:
            Pdem[keys[i]]=float(linesLoad[i])
            PV[keys[i]]=float(linesPV[i])
    #TODO: if not len(linesLoad)==len(linesPV)
    
    ###########################################################################
    #######                  PV Power delivered to load                 #######
    ###########################################################################
    Ppv_dem={}
    for i,value in Pdem.items():
        if Pdem[i]<=PV[i]:
            Ppv_dem[i]=Pdem[i]
        else:
            Ppv_dem[i]=PV[i]

    ###########################################################################
    #######                  Parameters and Variables                   #######
    ###########################################################################
    socstr=getStoredStorage()
    captstr=getkWhStorage()
    powstr=getkWStorage()
    initialSOC=float(socstr)/100        #Percentage
    storageCapacity=float(captstr)*3600 #kWh
    storageRatedkW=float(powstr)
       
    model = ConcreteModel()
    model.lengthSoC=RangeSet(0,N)
    model.horizon=RangeSet(0,N-1)
    model.PBAT= Var(model.horizon,bounds=(-storageRatedkW,storageRatedkW),initialize=0)    
    model.PGRID=Var(model.horizon)                      
    model.SoC=Var(model.lengthSoC,bounds=(0.20,0.95))
    
    ###########################################################################
    #######                         OBJECTIVE                           #######
    #######             Minimization of import-export                   #######
    ###########################################################################
    def obj_rule(model):
        return sum(model.PGRID[m]*model.PGRID[m] for m in model.horizon)
    model.obj=Objective(rule=obj_rule, sense = minimize)
        
    ###########################################################################
    #######                         CONSTRAINTS                         #######
    #######                Rule1: Power demand meeting                  #######
    #######                Rule2: State of charge consistency           #######
    #######                Rule3: Initial State of charge               #######
    ###########################################################################
    def con_rule1(model,m):
        return Pdem[m]==Ppv_dem[m] + model.PBAT[m] + model.PGRID[m] 
    def con_rule2(model,m):
        return model.SoC[m+1]==model.SoC[m] - model.PBAT[m]*15*60/storageCapacity 
    def con_rule3(model):
        return model.SoC[0]==initialSOC
    
    model.con1=Constraint(model.horizon,rule=con_rule1)
    model.con2=Constraint(model.horizon,rule=con_rule2)
    model.con3=Constraint(rule=con_rule3)

    ###########################################################################
    #######                         SOLVING                             #######
    ###########################################################################
    solver.solve(model)
    
    listsPStorageP = sorted(model.PBAT.items()) # sorted by key, return a list of tuples
    x4, y = zip(*listsPStorageP) # unpack a list of pairs into two tuples
    PStorage=[]
    for value in y:
        PStorage.append(value.value)

    return PStorage

def controlOptimalStorage(pOut,SoC_Battery,PV_power, dss_circuit_load):
    #pOut: Output power of the battery ---> dis: positive, ch: negative 
    
    powstr=getkWStorage()
    storageRatedkW=float(powstr)
    
    if pOut>0:
        dssText.Command = 'Storage.AtPVNode.State = Discharging';
        dssText.Command = 'Storage.AtPVNode.%discharge ='+str(pOut/storageRatedkW);
        dssText.Command = '? Storage.AtPVNode.state';
        kwTarget_storage = "A:Charging R:" + dssText.Result;
        return (kwTarget_storage, SoC_Battery,PV_power,dss_circuit_load)   
        
    elif pOut<0:
        dssText.Command = 'Storage.AtPVNode.State = Charging';
        dssText.Command = '? Storage.AtPVNode.%charge ='+str(-pOut/storageRatedkW);
        dssText.Command = '? Storage.AtPVNode.state';
        kwTarget_storage = "A:Charging R:" + dssText.Result;
        return (kwTarget_storage, SoC_Battery,PV_power,dss_circuit_load)   
    else:
        dssText.Command = 'Storage.AtPVNode.State = Idling';
        dssText.Command = '? Storage.AtPVNode.state';
        kwTarget_storage = "A:Charging R:" + dssText.Result;
        return (kwTarget_storage, SoC_Battery,PV_power,dss_circuit_load)   

      

##########################################################################
###########
###########################################################################
print("Program started")
engine = win32com.client.Dispatch("OpenDSSEngine.DSS")
engine.Start("0")
dssText = engine.Text
print("DSS Engine started")
dssCircuit = engine.ActiveCircuit
dssSolution = dssCircuit.Solution
dssCktElement = dssCircuit.ActiveCktElement
dssBus = dssCircuit.ActiveBus
dssMeters = dssCircuit.Meters
dssPDElement = dssCircuit.PDElements
dssLoads = dssCircuit.Loads
dssLines = dssCircuit.Lines
dssTransformers = dssCircuit.Transformers
dssGenerators=dssCircuit.Generators
dssPVsystems=dssCircuit.PVSystems

print ("Preparing compilation of main.dss")
os.chdir(r'C:\Users\guemruekcue\internship\optimization-agent')
OpenDSS_folder_path = r'C:\Users\guemruekcue\internship\optimization-agent'
filename = 'main.dss'
engine.ClearAll()
dssText.Command = "compile " + filename
print ("main.dss compiled")

#######################################################################
##########Convert the profile to 15 minute resolution
#######################################################################

os.chdir(r'C:\Users\guemruekcue\internship\optimization-agent\profiles')
file = 'residential.xlsx'
xls = pandas.ExcelFile(file)
df = xls.parse(xls.sheet_names[0])
tri_ph_load_model = []
for k in df['working days']:
    for i in range(15):
        tri_ph_load_model.append(k)
df3 = pandas.DataFrame(tri_ph_load_model, columns=['Active Power three phase (balance load)'])

#######################################################################
##########Convert the profile to 15 minute resolution
#######################################################################

profiles = []
for file in glob.glob('*.txt'):
    xls = profiles.append(file)
#rand_profile = profiles[random.randint(0,99)]
rand_profile = profiles[1]
df1 = pandas.read_csv(rand_profile, names=['Active Power phase R'])

one_ph_load_model = df1['Active Power phase R']

#######################################################################
#######################################################################
##########Calculation with PV and storage
#######################################################################
os.chdir(r'C:\Users\guemruekcue\internship\optimization-agent')
script_dir = os.path.dirname(__file__)
results_dir = os.path.join(os.path.dirname(__file__), 'results/')
voltages=[]
vS1=[]
vS2=[]
vS3=[]
load_profile=[]
timestamp=[]
the_time =  datetime.combine(date.today(), time(0, 0))
resStorage=[]
LoadkW=[]
x=0
simTime=[]

#we want 1 solution for each iteration so we can interact with the solution
dssText.Command = 'enable PVSystem.PV_Menapace'
dssText.Command = 'enable Storage.AtPVNode'
dssText.Command = 'solve mode=snap'
dssText.Command = 'Set mode = daily stepsize=1m number=1'


dssCircuit.Solution.dblHour=0.0


print(dssPVsystems.Count)
print(dssPVsystems.Idx)
dssPVsystems.Name='PV_Menapace'
print("Name: "+dssPVsystems.Name)
print("Power of PV system: "+str(dssPVsystems.kw))
num_steps=1440

#%%

ldsrc="C:/Users/guemruekcue/Projects/new/optimization-agent/profiles/load_profile_1.txt"
pvsrc="C:/Users/guemruekcue/Projects/new/optimization-agent/profiles/PV_profile3.txt"
optimizer=SolverFactory("ipopt", executable="C:/Users/guemruekcue/Anaconda3/pkgs/ipopt-3.11.1-2/Library/bin/ipopt")


#%%
batt=optimizeZero(ldsrc,pvsrc,optimizer)
#%%
for i in range(num_steps):
    
    if i > 0:
        LoadkW=getLoadskw()
        current_value=getLoadkwNo(54)
        SoC_Battery=getStoredStorage()
        PV_power=getPVPower('PV_Menapace')
        resStorage.append(controlOptimalStorage(batt[i],SoC_Battery,PV_power, current_value))
    
    dssSolution.solve()
    load_profile.append(LoadkW)
    dssCircuit.SetActiveBus('121117')
    puList = dssBus.puVmagAngle[0::2]
    voltages.append(puList)
    vS1.append(puList[0])
    vS2.append(puList[1])
    vS3.append(puList[2])
    timestamp.append(the_time)
    the_time = the_time + timedelta(minutes=1)

saveArrayInExcel(load_profile,results_dir,"LoadProfileControlStorage_Optimized")
saveArrayInExcel(resStorage,results_dir,"StorageControl_Optimized")
dssText.Command = 'CloseDI'


