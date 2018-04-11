# -*- coding: utf-8 -*-
"""
Created on Wed Apr 11 09:52:18 2018

@author: guemruekcue
"""

from pyomo.environ import SolverFactory
from LinearModels import model
import os

project_dir=os.path.dirname(os.path.dirname(__file__))

data_file=project_dir+'/Scenario.dat'


instance = model.create_instance(data_file)

opt=SolverFactory("ipopt")
results=opt.solve(instance)

print(results)