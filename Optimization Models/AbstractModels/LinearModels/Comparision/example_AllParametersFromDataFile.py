# -*- coding: utf-8 -*-
"""
Created on Thu Apr 12 09:36:40 2018

@author: guemruekcue
"""

from MinimizeGridExchange import MinimizeGridExchange
from pyomo.environ import SolverFactory

"""
Example:
    Abstract model is defined without parameters
    All the parameters are loaded from data file during instance generation
"""

#Building the abstract model without any parameter data
optimizationmodel1=MinimizeGridExchange()


if __name__=="__main__":
    import os
    #A data file with all parameters
    project_dir=os.path.dirname(__file__)
    data_file_1=project_dir+'/data_allParametersInFile.dat'
    
    #Constructing an instance of optimzation model
    instance1 = optimizationmodel1.abstractmodel.create_instance(data_file_1)
        
    #Solving the optimization problem
    opt=SolverFactory("ipopt")
    results1=opt.solve(instance1)
    
    #Printing the results
    print(results1)