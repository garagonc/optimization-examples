Solve a certain scenario (deterministic): pyomo solve --solver=SolverName models/ReferenceModel.py scenariodata/ScenarioName.dat

Solve the stochastic problem: runph --model-directory=models --instance-directory=scenariodata --default-rho=1 --solver=ipopt