# -*- coding: utf-8 -*-
"""
Created on Mon Feb 26 20:48:34 2024

@author: oscar
"""
# 2a
from gurobipy import GRB
import gurobipy as gb
import pandas as pd

# Read the dataset
df = pd.read_csv(r"C:\Users\oscar\Downloads\BasketballPlayers.csv", index_col='Number')

# Initialize the smallest number of invitations
initial_invitations = 21

def create_selection_model(number_invite):
    model = gb.Model("FIBA")

    # Create decision variables
    x = model.addVars(150, vtype=gb.GRB.BINARY, name="player")

    # Position constraints
    guard_indices = df[(df['Position'] == 'G') | (df['Position'] == 'G/F')].index.tolist()
    model.addConstr(gb.quicksum(x[i] for i in guard_indices) >= 0.3 * number_invite, "Guard")

    forward_center_indices = df[(df['Position'] == 'F') | (df['Position'] == 'C') | (df['Position'] == 'F/C')].index.tolist()
    if forward_center_indices:
        model.addConstr(gb.quicksum(x[i] for i in forward_center_indices if i < 150) >= 0.4 * number_invite, "Forward/Center")

    # Set the objective function
    model.setObjective(gb.quicksum(df.iloc[i, 1:8].sum() * x[i] for i in range(150)), gb.GRB.MAXIMIZE)

    # Capacity constraint
    model.addConstr(gb.quicksum(x[i] for i in range(150)) == number_invite, "Total Players")

    # Average score constraints
    for j in range(7):
        model.addConstr((gb.quicksum(df.iloc[i, j+1] * x[i] for i in range(150)) / number_invite) >= 2.05, f"Average Score {j}")

    # Constraint: if any 20-24, not all 72-78
    for i in range(19, 24):
        model.addConstr(x[i] <= 1 - gb.quicksum(x[j] for j in range(71, 78)), "If any 20-24, not all 72-78")

    # Constraint: if any 105-114, at least one 45-49 and at least one 60-69
    for i in range(104, 114):
        model.addConstr(x[i] <= gb.quicksum(x[j] for j in range(44, 49)), "If any 105-114, at least 45-49")
        model.addConstr(x[i] <= gb.quicksum(x[j] for j in range(64, 69)), "If any 105-114, at least 65-69")

    # We need at least one player from every 10 players
    for i in range(14):
        model.addConstr(gb.quicksum(x[i*10 + j] for j in range(10)) >= 1, "At least one player from")
        
    return model

# run the model with initial invitation number
final_model = create_selection_model(initial_invitations)

final_model.optimize()

# Print the objective and decision variables
final_model.printAttr('X')

# Print the model status
print("Model Status: ", final_model.status)

# Count and print the number of guards invited
selected = [i for i, var in enumerate(final_model.getVars()) if var.x != 0]
no_guards = sum(1 for i in selected if df.iloc[i]['Position'] in ['G', 'G/F'])
print(f'Number of G and G/F: {no_guards}')


# 2h
# Initialize the smallest number of invitations
initial_invitations = 21
    
# Iterate to find the smallest number of invitations before infeasibility
while True:
    # Set the number of invitations to the current value
    model = create_selection_model(initial_invitations)
    
    # Solve the model
    model.optimize()
    
    # Check feasibility status

    if model.status != GRB.Status.OPTIMAL:
        # Infeasible solution found, break the loop
        break
    
    # Increment the number of invitations for the next iteration
    initial_invitations -= 1

# Print the result
print("Smallest number of invitations before infeasible solution:", initial_invitations + 1)



