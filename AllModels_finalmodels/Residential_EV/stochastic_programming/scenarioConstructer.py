# -*- coding: utf-8 -*-
"""
Created on Wed May  2 14:38:51 2018

@author: guemruekcue
"""

import pandas as pd
import os
import shutil
import fileinput
from analysispy import *

earliest_arrival=15
#%%
def construct_scenario1(start,SoC_ESS,SoC_EV,position,scenarios,drives,probabilities):
    
    actualscenarios=scenarios[start]
    actualdrives=drives[start]
    actualprobs=probabilities[start]
   
    foldername='nodedata_'+str(start)+'/'
    if not os.path.exists(foldername):
        os.makedirs(foldername)
    shutil.copy2('nodedata/ScenarioStructure.dat', foldername+'ScenarioStructure.dat')
    shutil.copy2('nodedata/RootNode.dat', foldername+'RootNode.dat')
    with open(foldername+'RootNode.dat', "a") as myfile:                  
        myfile.write("\n\n")    
        myfile.write('set iniT := '+str(start)+';')
        myfile.write("\n")
        recTstr=' '.join(str(e) for e in range(start+1,24))
        myfile.write('set recT := '+recTstr+';')
        myfile.write("\n")
        Tstr=' '.join(str(e) for e in range(start,24)) 
        myfile.write('set T := '+Tstr+';')
        myfile.write("\n")
        T_SoCstr=' '.join(str(e) for e in range(start,25))
        myfile.write('set T_SoC := '+T_SoCstr+';')
        myfile.write("\n\n")
        myfile.write("#Real-time data\n")
        myfile.write('param ESS_SoC_Value := '+str(SoC_ESS)+';\n')          
        myfile.write('param EV_SoC_Value := '+str(SoC_EV)+';\n')            
        myfile.write('param P_Load_Forecast := \n')
        for ts in range(start,24):
            myfile.write(str(ts)+' '+str(df_de[ts][0]))
            myfile.write("\n")
        myfile.write(";\n")        
        myfile.write('param P_PV_Forecast := \n')
        for ts in range(start,24):
            myfile.write(str(ts)+' '+str(df_de[ts][1]))
            myfile.write("\n")
        myfile.write(";\n")
        myfile.write('param Price_Forecast := \n')
        for ts in range(start,24):
            myfile.write(str(ts)+' '+str(df_de[ts][2]))
            myfile.write("\n")
        myfile.write(";\n")  
    
    nodedata_dir = os.path.join(os.path.dirname(__file__), foldername)
    for index in range(1,4):
        filename=nodedata_dir+'Node'+str(index)+'.dat'
        with open(filename,'w') as out:
            out.write('param EV_ParkAtHome_Forecast  := ')
            out.write("\n")
            out.write(str(start)+' '+str(position))                           
            out.write("\n")
            for ts in range(start+1,24):
                out.write(str(ts)+' '+str(int(actualscenarios['s'+str(index)][ts-start-1])))   
                out.write("\n")
            out.write(";")
            out.write("\n")
            out.write("\n") 
            out.write('param P_EV_DriveDemand  := ')
            out.write("\n")
            out.write(str(start)+' '+str(int(actualdrives['s'+str(index)][0])))  
            out.write("\n")
            for ts in range(start+1,24):
                out.write(str(ts)+' '+str(int(actualdrives['s'+str(index)][ts-start-1]))) 
                out.write("\n")
            out.write(";")
            out.write("\n")
            out.write("\n")
    
    foldername='nodedata_'+str(start)
    scenariofile=foldername+'/ScenarioStructure.dat'                
    with fileinput.FileInput(scenariofile, inplace=True) as file:
        for line in file:
            print(line.replace('weight_scenario1', str(actualprobs['s1'])), end='')
    with fileinput.FileInput(scenariofile, inplace=True) as file:    
        for line in file:
            print(line.replace('weight_scenario2', str(actualprobs['s2'])), end='')
    with fileinput.FileInput(scenariofile, inplace=True) as file:  
        for line in file:
            print(line.replace('weight_scenario3', str(actualprobs['s3'])), end='')

####Examples############
construct_scenario1(15,0.35,0.4,1,ScenariosOfRealization1,DrivesOfRealization1,ScenarioProbabilitiesforRealization1)
