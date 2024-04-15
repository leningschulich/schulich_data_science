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
store = cost_matrix.shape[0]

# Initialize model 
model = gb.Model("Baffin Bay")

# The sum of all objectives and decision variables
objectives = 0
capacities = [0] * 15

# The number of trials to perform
trials = 50

# The number of scenarios per trial
samples = 100
    
for trial in range(trials):

    # The scenarios in this trial
    scenarios = range(samples)

    # Add the capacity decision variable (common to all problems)
    y = model.addVars(15, lb=0, vtype=GRB.INTEGER, name="order")

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

    for s in range(samples):
        for k in range(store):
            model.addConstr(gb.quicksum(x[i,k,s] for i in range(store)) <= y[k])

    # Optimally solve the problem
    model.optimize()
    
    # The running total
    objectives += model.objVal
    capacities = [capacities[i] + y[i].x for i in range(store)]
    
    # Reset the model
    model.reset(0)
    
print("Objective: ", objectives/trials)
for idx, capacity in enumerate(capacities):
    print(f"Optimal Capacity at store {idx}: {capacity/trials}")