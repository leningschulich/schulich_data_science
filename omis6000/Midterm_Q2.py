from gurobipy import Model, GRB
import pandas as pd

# Load data from CSV file
df = pd.read_csv("/Users/frieda/Desktop/midterm/non_profits.csv")

# Extract data from the DataFrame
custom_alpha = df['alpha_i'].values
custom_beta = df['beta_i'].values
num_customers = len(custom_alpha)

# Create a new model
model = Model("NonProfit")

# Add decision variables
allocation = model.addVars(num_customers, lb=0, vtype=GRB.CONTINUOUS, name="allocation")

# Add auxiliary variables
aux_vars = model.addVars(num_customers, lb=0, vtype=GRB.CONTINUOUS, name="auxiliary")

# Set auxiliary variable constraints using piecewise linear approximation
for i in range(num_customers):
    model.addGenConstrPow(aux_vars[i], allocation[i], 2.0 / 3.0, 1500)

# Set objective function
obj_expr = 2 * sum(aux_vars[i] for i in range(num_customers))
model.setObjective(obj_expr, GRB.MAXIMIZE)

# Add budget constraint
model.addConstr(allocation.sum() <= 50000000, "BudgetConstraint")

# Optimize model
model.optimize()


# Print optimal solution
print("Optimal solution:")


