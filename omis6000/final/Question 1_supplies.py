"""
@author: Group 12 Supplies
"""

from gurobipy import GRB
import gurobipy as gb
import pandas as pd

# Create the optimization model
model = gb.Model("Medical supplies distribution network")

# Objective function coefficients
cost = pd.read_csv(r'https://drive.google.com/uc?export=download&id=17F6H-WFOh3jOKqP4LLwSK195AfRAbsXv')
fixed = cost['Fixed']
variable = cost['Variable']

# Create three classes of five decision variables 
x = model.addVars(27, lb=0, vtype=GRB.INTEGER, name="units from warehouse to site")
z = model.addVars(27, vtype=GRB.BINARY, name="Potential sites")

# The objective function
fixed_costs = gb.quicksum(fixed[i]*z[i] for i in range(27))
variable_costs = gb.quicksum(variable[i]*x[i] for i in range(27))
model.setObjective(fixed_costs + variable_costs, GRB.MINIMIZE)

# Add the constraints

# Total number of units equal to the stock
model.addConstr(gb.quicksum(x[i] for i in range(27)) == 2900000, "distribution of stock")

# Each site cannot more than 375,000
model.addConstrs((x[i] <= 375000*z[i] for i in range(27)), "Max Unit Constraint")

# Each site cannot less than 175,000
model.addConstrs((x[i] >= 175000*z[i] for i in range(27)), "Min Unit Constraint")

# At least four site chosen from 6-16
model.addConstr(gb.quicksum(z[i] for i in range(5,16)) >= 4, "At least 4 from 6-16")

# No more than 6 sites from even numbered sites
model.addConstr(gb.quicksum(z[i] for i in range(1,27,2)) <= 6, "No more than six from even")

# If site 1 or 2 is chosen, site 5 - 7 cannot be chosen
for i in range(2):
    for j in range(4,7):
        model.addConstr(z[i] <= 1 - z[j], "If 1-2, then no 5-7")

# If any site from 19 to 22 is chosen, site 24, 26, 27 cannot be chosen
for i in range(18,22):
    for j in [23,25,26]:
        model.addConstr(z[i] <= 1 - z[j], "If 19-22, then no 24,26,27")

# If any site from 1-5, at least one odd site from 21-27
for i in range(5):
        model.addConstr(z[i] <= gb.quicksum(z[j] for j in range(20,27,2)), "If 1-5, at least one 21-27")

# Number of sites from 1-14 the same as number of sites 15-27
model.addConstr(gb.quicksum(z[i] for i in range(14)) == gb.quicksum(z[j] for j in range(14,27)), "Site 1-14 = 15-27")

# Number of  units from 1-9 the same as number of  unit 19-27
model.addConstr(gb.quicksum(x[i] for i in range(9)) == gb.quicksum(x[j] for j in range(18,27)), "Unit 1-9 = 19-27")
    
# Optimally solve the problem
model.optimize()

# Print the objective and decision variables
model.printAttr('X')

# The contirbution of each source of costs
print("Fixed Costs: ", fixed_costs.getValue())
print("Variable Costs: ", '%.2f' % variable_costs.getValue())