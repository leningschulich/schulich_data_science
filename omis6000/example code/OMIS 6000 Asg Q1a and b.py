# -*- coding: utf-8 -*-
"""
Created on Fri Jan 26 02:32:58 2024

@author: oscar
"""
from gurobipy import GRB
import gurobipy as gb
import pandas as pd

# Create the optimization model
model = gb.Model("Transshipment Problem")

# Cost
costs_direct = pd.read_csv(r"C:\Users\oscar\Downloads\Cost_Production_to_Refinement.csv").pivot(index="ProductionFacility", columns="RefinementCenter", values="Cost")
costs_pdn_to_ts = pd.read_csv(r"C:\Users\oscar\Downloads\Cost_Production_to_Transshipment.csv").pivot(index="ProductionFacility", columns="TransshipmentHub", values="Cost")
costs_ts_to_rf = pd.read_csv(r"C:\Users\oscar\Downloads\Cost_Transshipment_to_Refinement.csv").pivot(index="TransshipmentHub", columns="RefinementCenter", values="Cost")

# Capacity
capacity_direct = pd.read_csv(r"C:\Users\oscar\Downloads\Capacity_for_Direct_Production_Facilities.csv", index_col="ProductionFacility")
capacity_tranship_pdn = pd.read_csv(r"C:\Users\oscar\Downloads\Capacity_for_Transship_Production_Facilities.csv", index_col="ProductionFacility")
capacity_tranship_ts = pd.read_csv(r"C:\Users\oscar\Downloads\Capacity_for_Transship_Distribution_Centers.csv", index_col="TransshipmentHub")

# Demand
demand_df = pd.read_csv(r"C:\Users\oscar\Downloads\Refinement_Demand.csv", index_col="RefinementCenter")

# Direct Production to RF
x1 = model.addVars(25, 5, lb=0, vtype=GRB.CONTINUOUS, name="Source Nodes_D")
# Production to Tranship
x2 = model.addVars(15, 2, lb=0, vtype=GRB.CONTINUOUS, name="Source Nodes_T")
# Tranship to RF
y = model.addVars(2, 5, lb=0, vtype=GRB.CONTINUOUS, name="Transshipment Nodes")

# The objective function
direct_pdn_objective = gb.quicksum(costs_direct.iloc[i,j]*x1[i,j] for i in range(25) for j in range(5))
tranship_pdn_objective = gb.quicksum(costs_pdn_to_ts.iloc[i,j]*x2[i,j] for i in range(15) for j in range(2))
tranship_ts_objective = gb.quicksum(costs_ts_to_rf.iloc[i,j]*y[i,j] for i in range(2) for j in range(5))
model.setObjective(direct_pdn_objective + tranship_pdn_objective + tranship_ts_objective, GRB.MINIMIZE)

# Add the Capacity constraints from source nodes
model.addConstrs((gb.quicksum(x1[i,j] for j in range(5)) <= capacity_direct.iloc[i] for i in range(25)), name="Supply Constraint_direct_pdn")
model.addConstrs((gb.quicksum(x2[i,j] for j in range(2)) <= capacity_tranship_pdn.iloc[i] for i in range(15)), name="Supply Constraint_tranship_pdn")
model.addConstrs((gb.quicksum(y[i,j] for j in range(5)) <= capacity_tranship_ts.iloc[i] for i in range(2)), name="Supply Constraint_tranship_ts")

# Add the flow balance constrainits
for k in range(2):
    model.addConstr(gb.quicksum(x2[i,k] for i in range(15)) == gb.quicksum(y[k,j] for j in range(5)), name="Flow Balance")

# Add the demand constraints
model.addConstrs((gb.quicksum(x1[i,k] for i in range(25)) + gb.quicksum(y[j,k] for j in range(2)) == demand_df.iloc[k] for k in range(5)), name="Demand Constraint")

# Optimally solve the problem
model.optimize()

# Number of variables in the model
print("Number of Decision Variables: ", model.numVars)

# Value of the objective function
print("Total Transportation cost: ", model.objVal)

# Print the decision variables
print(model.printAttr('X'))

# Q1(b)
# Ensure the model has been optimized before calculating
if model.status == GRB.OPTIMAL:
    # Calculate the total transshipped
    total_transshipped = sum(y[i,j].X for i in range(2) for j in range(5))
    
    # Calculate the total produced for transshipment
    total_produced_transship = sum(x2[i,j].X for i in range(15) for j in range(2))
    
    # Calculate the total produced directly to refinement centers
    total_produced_direct = sum(x1[i,j].X for i in range(25) for j in range(5))
    
    # Calculate the total production
    total_production = total_produced_transship + total_produced_direct
    
    # Calculate the proportion of transshipment
    proportion_transshipment = total_transshipped / total_production if total_production else 0
    
    print("Total Transshipped: ", total_transshipped)
    print("Total Production: ", total_production)
    print("Proportion of Transshipment: ", proportion_transshipment)
else:
    print("Model not solved to optimality. Cannot calculate proportions.")
    

