import random

import win32com.client
#from pandas import *
import pandas
#from numpy import *
#from pylab import *
import matplotlib.pyplot as plt
import glob, os
#from os.path import expanduser, join

#import datetime as dt
#import pytz as tz
from datetime import date, datetime, time, timedelta

from pyomo.environ import *
from pyomo.opt import SolverFactory 
###########################################################################
#######               Functions
############################################################################

 
def thresholdPowerStorage(dss_circuit_load,charge=0.4,discharge=0.8):
    #return dss_circuit_load#print(str(dss_circuit_load))
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

def thresholdVolStorage(dss_bus_volt,charge=1.02,discharge=0.98):
    #return dss_circuit_load#print(str(dss_circuit_load))
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
    # Create a Pandas Excel writer using XlsxWriter as the engine.
    writer = pandas.ExcelWriter(directory + name_of_file +'.xlsx', engine='xlsxwriter')
    # Convert the dataframe to an XlsxWriter Excel object.
    dfName.to_excel(writer, sheet_name='Sheet 1')
    # Close the Pandas Excel writer and output the Excel file.
    writer.save()
    return 1

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

def getTime():
    #array=[]
    #array.append("Time")
    #array.append(dssCircuit.Solution.dblHour)
    return dssCircuit.Solution.dblHour

def getPVPower(PV_name):
    dssPVsystems.Name=PV_name
    PV_power=dssPVsystems.kw
    return PV_power

def getStoredStorage():
    dssText.Command = '? Storage.AtPVNode.%stored'
    stored_storage = dssText.Result
    return stored_storage

def getkWStorage():
    dssText.Command = '? Storage.AtPVNode.kW'
    kW_storage = dssText.Result
    return kW_storage

def controlRasmusStorage(SoC_Battery,PV_power, dss_circuit_load):
    #return dss_circuit_load#print(str(dss_circuit_load))
    low_load=0.4
    high_load=2
    low_SoC=40
    high_SoC=80
    PV_low=0.4
    PV_high=0.7
    circuit_power=float(dss_circuit_load)
    
    if (PV_power >= circuit_power) and (float(SoC_Battery) <= low_SoC):
        dssText.Command = 'Storage.AtPVNode.State = Charging';
        dssText.Command = '? Storage.AtPVNode.state';
        kwTarget_storage = "A:Charging R:" + dssText.Result;
        return (kwTarget_storage, SoC_Battery,PV_power,dss_circuit_load) 
    
    elif (PV_power >= circuit_power):
        dssText.Command = 'Storage.AtPVNode.State = Charging';
        dssText.Command = '? Storage.AtPVNode.state';
        kwTarget_storage = "A:Disharging R:" + dssText.Result;
        return (kwTarget_storage, SoC_Battery,PV_power,dss_circuit_load)
    
    elif (PV_power <= circuit_power) and (float(SoC_Battery) <= low_SoC):
        dssText.Command = 'Storage.AtPVNode.State = Idling';
        dssText.Command = '? Storage.AtPVNode.state';
        kwTarget_storage = "A:Disharging R:" + dssText.Result;
        return (kwTarget_storage, SoC_Battery,PV_power,dss_circuit_load)
    
    elif (PV_power <= circuit_power):
        dssText.Command = 'Storage.AtPVNode.State = DisCharging';
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
    
def controlStoragePriceOptimization(PStorage,SoC_Battery,PV_power, Pdem, price,timeInterval):

    model = ConcreteModel()


    model.x= Var(bounds=(0,6.4))

    model.obj= Objective(expr= sum( price*timeInterval(model.x+Pdem-PV_power)), sense = minimize )
    model.limits=ConstraintList()
    model.limits.add(SoC_Battery >= 20)
    model.limits.add(SoC_Battery <= 100)
    

    opt = SolverFactory('glpk',executable="C:/Users/garagon/Anaconda3/pkgs/glpk-4.63-vc14_0/Library/bin/glpsol")
# Create a model instance and optimize

    instance=model.create()
    results = opt.solve(instance)
    instance.solutions.load_from(results)
    instance.display()
    for key, value in instance.x.iteritems():
        print(key,value.value)
        
    print(instance.x['hammer'].value)
    return 1
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
#dssPowers=dssCktElement.powers
#dssMonitors=dssCircuit.Monitors
#dssCtrlQueue=dssCircuit.CtrlQueue ;
#dssSolution.MaxControlIterations=1000;
#dssSolution.maxiterations=1000;
#dssText.Command = 'Set controlmode=snap' ;
#dssText.Command = 'Set mode = daily stepsize=1m' ;

#dssCircuit.Solution.Stepsize=60

print ("Preparing compilation of main.dss")
os.chdir(r'U:\Projekte\UCC\Storage4Grid\Simulation\python')
OpenDSS_folder_path = r'U:\Projekte\UCC\Storage4Grid\Simulation\python'
filename = 'main.dss'
engine.ClearAll()
dssText.Command = "compile " + filename
print ("main.dss compiled")



#######################################################################
##########convierte el profile a cada minuto por un día 1440 valores
#######################################################################

os.chdir(r'U:\Projekte\UCC\Storage4Grid\Simulation\python\profiles')
file = 'residential.xlsx'
xls = pandas.ExcelFile(file)
df = xls.parse(xls.sheet_names[0])
tri_ph_load_model = []
for k in df['working days']:
    for i in range(15):
        tri_ph_load_model.append(k)
df3 = pandas.DataFrame(tri_ph_load_model, columns=['Active Power three phase (balance load)'])


#######################################################################
##########convierte el profile a cada minuto por un día 1440 valores
#######################################################################

profiles = []
for file in glob.glob('*.txt'):
    xls = profiles.append(file)
#rand_profile = profiles[random.randint(0,99)]
rand_profile = profiles[1]
df1 = pandas.read_csv(rand_profile, names=['Active Power phase R'])

one_ph_load_model = df1['Active Power phase R']

#######################################################################
##########Calculation without anything
#######################################################################
#def Calculate():
os.chdir(r'U:\Projekte\UCC\Storage4Grid\Simulation\python')
script_dir = os.path.dirname(__file__)
results_dir = os.path.join(os.path.dirname(__file__), 'results/')
voltages=[]
v11=[]
v12=[]
v13=[]
load_profile=[]
timestamp=[]
the_time =  datetime.combine(date.today(), time(0, 0))
resStorage=[]
LoadkW=[]
x=0
simTime=[]

#we want 1 solution for each iteration so we can interact with the solution
dssText.Command = 'disable Storage.AtPVNode'
dssText.Command = 'disable PVSystem.PV_Menapace'
dssText.Command = 'solve mode=snap'
dssText.Command = 'Set mode = daily stepsize=1m number=1'


dssCircuit.Solution.dblHour=0.0

#dssLoads.name='No52'
#dssLoads.kW = 500
#print(dssLoads.cfactor)
#print(dssLoads.allnames)
#print(dssLoads.kw)
#print(dssCircuit.ActiveCktElement.powers)
#print(dssCircuit.TotalPower)
#for i in range(len(tri_ph_load_model)):


num_steps=1440*2
for i in range(num_steps):
    LoadkW=getLoadskw()
    dssSolution.solve()
    #dssText.Command = 'Updatestorage'
    load_profile.append(LoadkW)
    #dssCircuit.SetActiveBus('82876')
    dssCircuit.SetActiveBus('121117')
    puList = dssBus.puVmagAngle[0::2]
    voltages.append(puList)
    v11.append(puList[0])
    v12.append(puList[1])
    v13.append(puList[2])
    timestamp.append(the_time)
    the_time = the_time + timedelta(minutes=1)

#dssCircuit.Loads.name ='No52'
#dssCircuit.Loads.kW = 0
#dssCircuit.Loads.name ='No52_S'
#dssCircuit.Loads.kW = 0
saveArrayInExcel(load_profile,results_dir,"LoadProfileControl")
#dssText.Command = 'CloseDI'

#######################################################################
##########Calculation only with PV
#######################################################################
#def Calculate():
os.chdir(r'U:\Projekte\UCC\Storage4Grid\Simulation\python')
script_dir = os.path.dirname(__file__)
results_dir = os.path.join(os.path.dirname(__file__), 'results/')
voltages=[]
v1=[]
v2=[]
v3=[]
load_profile=[]
timestamp=[]
the_time =  datetime.combine(date.today(), time(0, 0))
resStorage=[]
LoadkW=[]
x=0
simTime=[]

#we want 1 solution for each iteration so we can interact with the solution
dssText.Command = 'disable Storage.AtPVNode'
dssText.Command = 'enable PVSystem.PV_Menapace'
dssText.Command = 'solve mode=snap'
dssText.Command = 'Set mode = daily stepsize=1m number=1'


dssCircuit.Solution.dblHour=0.0

#dssLoads.name='No52'
#dssLoads.kW = 500
#print(dssLoads.cfactor)
#print(dssLoads.allnames)
#print(dssLoads.kw)
#print(dssCircuit.ActiveCktElement.powers)
#print(dssCircuit.TotalPower)
#for i in range(len(tri_ph_load_model)):
num_steps=1440*2
for i in range(num_steps):
    LoadkW=getLoadskw()
    #print(dssCktElement.seqpowers)
    dssSolution.solve()
    #dssText.Command = 'Updatestorage'
    load_profile.append(LoadkW)
    #dssCircuit.SetActiveBus('82876')
    dssCircuit.SetActiveBus('121117')
    puList = dssBus.puVmagAngle[0::2]
    voltages.append(puList)
    v1.append(puList[0])
    v2.append(puList[1])
    v3.append(puList[2])
    timestamp.append(the_time)
    the_time = the_time + timedelta(minutes=1)
    
#dssMonitors.Name=('m1')
#dssMonitors.show
#dssText.Command('Plot monitor object=m1 channels=(1 )')
#dssCircuit.Loads.name ='No52'
#dssCircuit.Loads.kW = 0
#dssCircuit.Loads.name ='No52_S'
#dssCircuit.Loads.kW = 0
saveArrayInExcel(load_profile,results_dir,"LoadProfileControlPV")
#dssText.Command = 'CloseDI'

#######################################################################
##########Calculation with PV and storage
#######################################################################
#def Calculate():
os.chdir(r'U:\Projekte\UCC\Storage4Grid\Simulation\python')
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
dssText.Command = 'enable Storage.AtPVNode'
dssText.Command = 'solve mode=snap'
dssText.Command = 'Set mode = daily stepsize=1m number=1'


dssCircuit.Solution.dblHour=0.0

#dssLoads.name='No52'
#dssLoads.kW = 500
#print(dssLoads.cfactor)
#print(dssLoads.allnames)
#print(dssLoads.kw)
#print(dssCircuit.ActiveCktElement.powers)
#print(dssCircuit.TotalPower)
#for i in range(len(tri_ph_load_model)):

print(dssPVsystems.Count)
print(dssPVsystems.Idx)
dssPVsystems.Name='PV_Menapace'
print("Este es el nombre: "+dssPVsystems.Name)

print("Este es el power: "+str(dssPVsystems.kw))
num_steps=1440*2
for i in range(num_steps):
    
    if i > 0:
        LoadkW=getLoadskw()
        current_value=getLoadkwNo(54)
        #resStorage.append(thresholdPowerStorage(current_value,0.7,2.2))
        SoC_Battery=getStoredStorage()
        PV_power=getPVPower('PV_Menapace')
        resStorage.append(controlRasmusStorage(SoC_Battery,PV_power, current_value))
    #dssCircuit.SetActiveBus('121117')
    #puList = dssBus.puVmagAngle[0::2]
    #current_value=puList[2]
    #resStorage.append(thresholdVolStorage(current_value,1.01,0.98))
    #print(dssCktElement.seqpowers)
    dssSolution.solve()
    #dssText.Command = 'Updatestorage'
    load_profile.append(LoadkW)
    #dssCircuit.SetActiveBus('82876')
    dssCircuit.SetActiveBus('121117')
    puList = dssBus.puVmagAngle[0::2]
    voltages.append(puList)
    vS1.append(puList[0])
    vS2.append(puList[1])
    vS3.append(puList[2])
    timestamp.append(the_time)
    the_time = the_time + timedelta(minutes=1)

#dssCircuit.Loads.name ='No52'
#dssCircuit.Loads.kW = 0
#dssCircuit.Loads.name ='No52_S'
#dssCircuit.Loads.kW = 0
saveArrayInExcel(load_profile,results_dir,"LoadProfileControlStorage")
saveArrayInExcel(resStorage,results_dir,"StorageControl")
dssText.Command = 'CloseDI'

#######################################################################
##########Calculation with PV and storage and optimization of price
#######################################################################
#def Calculate():
os.chdir(r'U:\Projekte\UCC\Storage4Grid\Simulation\python')
script_dir = os.path.dirname(__file__)
results_dir = os.path.join(os.path.dirname(__file__), 'results/')
voltages=[]
vS1_opt=[]
vS2_opt=[]
vS3_opt=[]
load_profile=[]
timestamp=[]
the_time =  datetime.combine(date.today(), time(0, 0))
resStorage=[]
LoadkW=[]
x=0
simTime=[]

#we want 1 solution for each iteration so we can interact with the solution
dssText.Command = 'enable Storage.AtPVNode'
dssText.Command = 'solve mode=snap'
dssText.Command = 'Set mode = daily stepsize=1m number=1'


dssCircuit.Solution.dblHour=0.0

#dssLoads.name='No52'
#dssLoads.kW = 500
#print(dssLoads.cfactor)
#print(dssLoads.allnames)
#print(dssLoads.kw)
#print(dssCircuit.ActiveCktElement.powers)
#print(dssCircuit.TotalPower)
#for i in range(len(tri_ph_load_model)):

print(dssPVsystems.Count)
print(dssPVsystems.Idx)
dssPVsystems.Name='PV_Menapace'
print("Este es el nombre: "+dssPVsystems.Name)

print("Este es el power: "+str(dssPVsystems.kw))

print("Este el power de storage: "+str(getkWStorage()))
num_steps=1440*2
for i in range(num_steps):
    
    if i > 0:
        LoadkW=getLoadskw()
        Pdem=getLoadkwNo(54)
        #resStorage.append(thresholdPowerStorage(current_value,0.7,2.2))
        SoC_Battery=getStoredStorage()
        #print("Este el power de storage: "+str(getkWStorage()))
        PV_power=getPVPower('PV_Menapace')
        
        controlStoragePriceOptimization(getkWStorage(),SoC_Battery,PV_power, Pdem, 0.3,1)
        #resStorage.append(controlRasmusStorage(SoC_Battery,PV_power, Pdem))
    #dssCircuit.SetActiveBus('121117')
    #puList = dssBus.puVmagAngle[0::2]
    #current_value=puList[2]
    #resStorage.append(thresholdVolStorage(current_value,1.01,0.98))
    #print(dssCktElement.seqpowers)
    dssSolution.solve()
    #dssText.Command = 'Updatestorage'
    load_profile.append(LoadkW)
    #dssCircuit.SetActiveBus('82876')
    dssCircuit.SetActiveBus('121117')
    puList = dssBus.puVmagAngle[0::2]
    voltages.append(puList)
    vS1.append(puList[0])
    vS2.append(puList[1])
    vS3.append(puList[2])
    timestamp.append(the_time)
    the_time = the_time + timedelta(minutes=1)

#dssCircuit.Loads.name ='No52'
#dssCircuit.Loads.kW = 0
#dssCircuit.Loads.name ='No52_S'
#dssCircuit.Loads.kW = 0
saveArrayInExcel(load_profile,results_dir,"LoadProfileControlStorage")
saveArrayInExcel(resStorage,results_dir,"StorageControl")
dssText.Command = 'CloseDI'

#######################################################################
##########calculation with electric vehicle 
#######################################################################
'''
v_r=[]
v_s=[]
v_t=[]
EV_charger_step = 0
charger_per_step = 0
EV_full=14.5
dod=0.8
EV_eighty_energy = round(((EV_full * dod)/3.3)*60)
charger = 0
#h = random.randint(0,23)
#m = random.randint(0,59)
h=18
m=25
EV_plug_time = datetime.combine(date.today(), time(h, m))
for i in range(len(tri_ph_load_model)):
    dssCircuit.Loads.name ='54'
    #dssCircuit.Loads.kW = tri_ph_load_model[i]
    #dssCircuit.Loads.name ='No52_S'
    #dssCircuit.Loads.kW = one_ph_load_model[i]
    if EV_plug_time.time() == the_time.time():
        charger = 3.3
        charger_per_step = 1
    dssCircuit.Loads.kW = dssCircuit.Loads.kW + charger
    EV_charger_step += charger_per_step
    if EV_charger_step >= EV_eighty_energy:
        charger = 0
        
    current_value=dssCircuit.Loads.kW
   
    #resStorage.append(thresholdStorage(current_value,20,40))
    dssSolution.solve()
    dssCircuit.SetActiveBus('121117')
    puList = dssBus.puVmagAngle[0::2]
    voltages.append(puList)
    v_r.append(puList[0])
    v_s.append(puList[1])
    v_t.append(puList[2])
    the_time = the_time + timedelta(minutes=1)
    load_profile.append(dssCircuit.Loads.kW)
'''

#######################################################################
##########plot of the voltage vectors
#######################################################################

os.chdir(r'U:\Projekte\UCC\Storage4Grid\Simulation\python')
script_dir = os.path.dirname(__file__)
results_dir = os.path.join(os.path.dirname(__file__), 'results/')
file_name="Analysis by Giggi"


styles1 = ['b','r','g']
styles2 = ['b:','r:','g:']
styles3 = ['b--','r--','g--']

df1 = pandas.DataFrame(list(zip(timestamp, v1, v2,v3)), columns=['time','R (PV)','S (PV)','T (PV)'])
#df2 = pandas.DataFrame(list(zip(timestamp, v_r, v_s,v_t)), columns=['time','R (dumb charging)','S (dumb charging)','T (dumb charging)'])
df2 = pandas.DataFrame(list(zip(timestamp, vS1, vS2,vS3)), columns=['time','R (storage)','S (storage)','T (storage)'])
df4 = pandas.DataFrame(list(zip(timestamp, v11, v12, v13)), columns=['time','R','S','T'])
#dfLM=pandas.DataFrame(list(zip(timestamp, one_ph_load_model)),columns=['time','Load profile'])
fig, ax = plt.subplots(figsize=(12, 8), dpi=120)
df1.plot(x='time',y=['R (PV)','S (PV)','T (PV)'],rot=90, style=styles1, ax=ax)
#df2.plot(x='time',y=['R (storage)','S (storage)','T (storage)'],rot=90, style=styles2, ax=ax)
df4.plot(x='time',y=['R','S','T'],rot=90, style=styles3, ax=ax)
#dfLM.plot(x='time',y=['Load profile'],rot=90, style=styles3, ax=ax)

plt.gcf().autofmt_xdate()
plt.ylabel('Voltage (p.u.)', fontsize=18)
plt.xlabel('Time', fontsize=18)
plt.title(file_name)
plt.rc('axes', titlesize=20)

plt.show()

if not os.path.isdir(results_dir):
    os.makedirs(results_dir)

fig.savefig(results_dir + file_name + ".jpg")

#######################################################################
##########saving info as an excel file
#######################################################################


# Create a Pandas Excel writer using XlsxWriter as the engine.
writer = pandas.ExcelWriter(results_dir + file_name+'.xlsx', engine='xlsxwriter')

# Convert the dataframe to an XlsxWriter Excel object.
df1.to_excel(writer, sheet_name='No EV')
#df2.to_excel(writer, sheet_name='EV')

# Close the Pandas Excel writer and output the Excel file.
writer.save()