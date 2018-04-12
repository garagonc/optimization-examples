# -*- coding: utf-8 -*-
"""
Created on Thu Apr 12 09:44:18 2018

@author: guemruekcue
"""

from MinimizeGridExchange import MinimizeGridExchange
from pyomo.environ import SolverFactory

"""
Example:
    Abstract model is defined with variable parameters: SOC and foreacats
    Fixed parameters are loaded from data file during instance generation
"""


###########################################################################
#Dictionaries for setting soc and forecast parameters with function arguments: build_abstract_model_withSomeParameters()    

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

essInput={0:{}}
essInput[0]['iniSoC']=0.35


dictlist=[loadInput,pvInput,essInput,marketInput]
###########################################################################

#Building the abstract model with SOC and forecast data
optimizationmodel2=MinimizeGridExchange(dictlist)

if __name__=="__main__":
    import os

    #The file with fixed parameters such as battery capacity, inverter rate etc.
    project_dir=os.path.dirname(__file__)
    data_file_2=project_dir+'/data_fixedParametersInFile.dat'
    
    
    #Constructing an instance of optimzation model
    instance2 = optimizationmodel2.abstractmodel.create_instance(data_file_2)
        
    #Solving the optimization problem
    opt=SolverFactory("ipopt")
    results2=opt.solve(instance2)
    
    #Printing the results
    print(results2)