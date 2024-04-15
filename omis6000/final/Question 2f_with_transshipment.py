"""
@author: Group 12 Baffin Bay
"""

# Modules required for this class
from gurobipy import GRB
import gurobipy as gb
import pandas as pd
import random
import numpy as np

# Read data
distribution = pd.read_csv(r'https://drive.google.com/uc?export=download&id=1gEVBUCwo9oCpGsJbCMe3-umlCiIhIvlU')
cost_matrix = pd.read_csv(r'https://drive.google.com/uc?export=download&id=1Vbx2eDyWSVQVTY2V61SyezoCF5O7ugVr')

# Descriptive statistics
distribution.describe()
cost_matrix.describe()

# Model parameters
n = distribution['n']
p = distribution['p']
mean = distribution['Mean']
store = cost_matrix.shape[0]

# Step 1 of EEV calculation with average demand

y = round(mean)

# # Step 2 of EEV calcualtion: Stochastic Model with y from Step 1

# Initialize model 
model = gb.Model("Baffin Bay")

# The sum of all objectives and decision variables
objectives = 0

# The number of scenarios per trial
samples = 500
    
# Add the capacity decision variable (common to all problems)

x = model.addVars(15, 15, samples, lb=0, vtype=GRB.INTEGER, name="from row to columns")

# Deviational variables in the average model 
d_plus = model.addVars(store, samples, lb=0, vtype=GRB.INTEGER, name="excess inventory")
d_minus = model.addVars(store, samples, lb=0, vtype=GRB.INTEGER, name="excess demand")    

# Deterministic objective function 
underage_cost = 1.0/samples * gb.quicksum((24.44)*d_minus[i,n] for i in range(store) for n in range(samples))
overage_cost = 1.0/samples * gb.quicksum((25.55)*d_plus[i, n] for i in range(store) for n in range(samples))
tran_cost = 1.0/samples * gb.quicksum(cost_matrix.iloc[i,j]*x[i,j, s] for i in range(store) for j in range(store) for s in range(samples))
model.setObjective(underage_cost + overage_cost + tran_cost, GRB.MINIMIZE)

# Demand constraint
for s in range(samples):
    for i in range(store):
        model.addConstr(y[i] + d_minus[i, s] + gb.quicksum(x[k,i,s] for k in range(store)) == np.random.binomial(n[i], p[i]) + d_plus[i, s] + gb.quicksum(x[i,k,s] for k in range(store)))

# Optimally solve the problem
model.optimize()

objectives = model.objVal
    
print("Objective: ", objectives)

print("SP Objective Function Value:",  1199.01)
print("EEV Objective Function Value: ", model.objval)
print("EVPI = SP - EEV = ", model.objval - 1199.01)