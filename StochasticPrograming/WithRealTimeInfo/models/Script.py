# -*- coding: utf-8 -*-
"""
Created on Fri Mar 16 15:05:36 2018

@author: guemruekcue
"""

from pyomo.environ import SolverFactory
from ReferenceModel import model
import os

project_dir=os.path.dirname(os.path.dirname(__file__))

data_file=project_dir+'/scenariodata/EarlyLeaveEarlyArrival.dat'


instance = model.create_instance(data_file)
instance.pprint()

opt=SolverFactory("ipopt")
results=opt.solve(instance)

print(results)
