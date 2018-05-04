# -*- coding: utf-8 -*-
"""
Created on Wed May  2 14:38:51 2018

@author: guemruekcue
"""

import pandas as pd
import os
import shutil

# Assign spreadsheet filename to `file`
file = 'Likely2HappenScenarios.xlsx'

# Load spreadsheet
xl = pd.ExcelFile(file)
sh_parkhome=pd.read_excel(xl,"ParkHome")
sh_parkaway=pd.read_excel(xl,"ParkAway")
sh_drive=pd.read_excel(xl,"Drive")

sh_deterministicparameters=pd.read_excel(xl,"Deterministic")

earliest_arrival=15

def construct_scenario1(start,SoC_ESS,SoC_EV):
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
            myfile.write(str(ts)+' '+str(sh_deterministicparameters[ts][0]))
            myfile.write("\n")
        myfile.write(";\n")        
        myfile.write('param P_PV_Forecast := \n')
        for ts in range(start,24):
            myfile.write(str(ts)+' '+str(sh_deterministicparameters[ts][1]))
            myfile.write("\n")
        myfile.write(";\n")
        myfile.write('param Price_Forecast := \n')
        for ts in range(start,24):
            myfile.write(str(ts)+' '+str(sh_deterministicparameters[ts][1]))
            myfile.write("\n")
        myfile.write(";\n")  
    
    nodedata_dir = os.path.join(os.path.dirname(__file__), foldername)
    for index in range(9):
        filename=nodedata_dir+sh_parkhome['Scenario'][index]+'Node'+'.dat'
        with open(filename,'w') as out:
            out.write('param EV_ParkAtHome_Forecast  := ')
            out.write("\n")
            out.write(str(start)+' 1')
            out.write("\n")
            for ts in range(start+1,24):
                out.write(str(ts)+' '+str(sh_parkhome[ts][index]))
                out.write("\n")
            out.write(";")
            out.write("\n")
            out.write("\n") 
            out.write('param EV_ParkAway_Forecast  := ')
            out.write("\n")
            out.write(str(start)+' 0')
            out.write("\n")
            out.write(str(start+1)+' 0')
            out.write("\n")
            for ts in range(start+2,24):
                out.write(str(ts)+' '+str(sh_parkaway[ts][index]))
                out.write("\n")
            out.write(";")
            out.write("\n")
            out.write("\n")
            out.write('param P_EV_DriveDemand  := ')
            out.write("\n")
            out.write(str(start)+' 0')
            out.write("\n")
            for ts in range(start+1,24):
                out.write(str(ts)+' '+str(sh_drive[ts][index]))
                out.write("\n")
            out.write(";")
            out.write("\n")
            out.write("\n")


def construct_scenario2(start,SoC_ESS,SoC_EV):
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
            myfile.write(str(ts)+' '+str(sh_deterministicparameters[ts][0]))
            myfile.write("\n")
        myfile.write(";\n")        
        myfile.write('param P_PV_Forecast := \n')
        for ts in range(start,24):
            myfile.write(str(ts)+' '+str(sh_deterministicparameters[ts][1]))
            myfile.write("\n")
        myfile.write(";\n")
        myfile.write('param Price_Forecast := \n')
        for ts in range(start,24):
            myfile.write(str(ts)+' '+str(sh_deterministicparameters[ts][1]))
            myfile.write("\n")
        myfile.write(";\n")  
   
    nodedata_dir = os.path.join(os.path.dirname(__file__), foldername)
    for index in range(9):
        filename=nodedata_dir+sh_parkhome['Scenario'][index]+'Node'+'.dat'
        with open(filename,'w') as out:
            out.write('param EV_ParkAtHome_Forecast  := ')
            out.write("\n")
            out.write(str(start)+' 0')
            out.write("\n")
            for ts in range(start+1,24):
                if ts<earliest_arrival:
                    out.write(str(ts)+' 0')
                    out.write("\n")
                else:                       
                    out.write(str(ts)+' '+str(sh_parkhome[ts][index]))
                    out.write("\n")
            out.write(";")
            out.write("\n")
            out.write("\n") 
            out.write('param EV_ParkAway_Forecast  := ')
            out.write("\n")
             
            if start==earliest_arrival-1:
                out.write(str(start)+' 0')
                out.write("\n")
            else:
                out.write(str(start)+' 1')
                out.write("\n")                
            for ts in range(start+1,24):                   
                out.write(str(ts)+' '+str(sh_parkaway[ts][index]))
                out.write("\n")
            out.write(";")
            out.write("\n")
            out.write("\n")
            out.write('param P_EV_DriveDemand  := ')
            out.write("\n")  
            for ts in range(start,24):
                out.write(str(ts)+' '+str(sh_drive[ts][index]))
                out.write("\n")
            out.write(";")
            out.write("\n")
            out.write("\n")


####Examples############
construct_scenario1(7,0.35,0.4)
#construct_scenario2(7,0.35,0.4)
""""""