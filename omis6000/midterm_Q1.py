from gurobipy import GRB
import gurobipy as gb
import pandas as pd

# Define file paths
nutrient_requirements_path = "/Users/frieda/Desktop/midterm/nutrient_requirements.csv"
nutrient_content_path = "/Users/frieda/Desktop/midterm/nutrient_content.csv"
food_preferences_path = "/Users/frieda/Desktop/midterm/food_preferences.csv"
food_categories_path = "/Users/frieda/Desktop/midterm/food_categories.csv"

# Load data from CSV files
nutrient_requirements = pd.read_csv(nutrient_requirements_path)
nutrient_content = pd.read_csv(nutrient_content_path)
food_preferences = pd.read_csv(food_preferences_path)
food_categories = pd.read_csv(food_categories_path)

print("Food preferences DataFrame:")
print(food_preferences.head())
print("Nutrient requirements DataFrame:")
print(nutrient_requirements.head())
print("Food categories DataFrame:")
print(food_categories.head())

# Instantiate our optimization problem
model = gb.Model("OptiDiet")

# Define the decision variables
x = {}
for i in range(1, 121):
    for j in range(1, 61):
        x[i, j] = model.addVar(lb=0, vtype=GRB.CONTINUOUS, name=f"x[{i},{j}]")

# Define objective function
costs = food_categories['Cost_per_gram']

# Set the objective function
model.setObjective(sum(costs[i] * x[i+1, j] for i in range(120) for j in range(1, 61)), GRB.MINIMIZE)

# Define the nutritional balance constraints
for j in range(1, 61):
    model.addConstr(sum(x[i, j] for i in range(1, 121)) >= nutrient_requirements['Min_Requirement'][j-1])
    model.addConstr(sum(x[i, j] for i in range(1, 121)) <= nutrient_requirements['Max_Requirement'][j-1])

# Define the dietary preference constraints for each food item
for k, row in food_preferences.iterrows():
    for pref_column in ['Veggie_grams', 'Vegan_grams', 'Kosher_grams', 'Halal_grams', 'All_grams']:
        pref_name = pref_column.split('_')[0]  # Extract dietary preference name
        model.addConstr(sum(x[i, j] for j in range(1, 61)) <= row[pref_column], name=f"Dietary_Preference_{pref_name}_Constraint_{k}")

# Define the variety constraint
for i in range(1, 121):
    model.addConstr(sum(x[i, j] for j in range(1, 61)) <= 0.03 * sum(x[i, j] for j in range(1, 61)))

# Optimize the model
model.optimize()
