# -*- coding: utf-8 -*-
"""
Created on Tue Apr 17 15:22:05 2018

@author: guemruekcue
"""

from subprocess import call
call("runph --model-directory=models --instance-directory=scenariodata --default-rho=1 --solver=ipopt --solution-writer=pyomo.pysp.plugins.csvsolutionwriter")
