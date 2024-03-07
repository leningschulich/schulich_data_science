from gurobipy import GRB
import gurobipy as gb
import pandas as pd

# Load data from CSV file
df = pd.read_csv(r"/Users/frieda/Desktop/midterm/nurse_shift_costs.csv")
shift_hours_per_day = 12

# Create optimization model
model = gb.Model("Nurse")

# Define decision variables
work_assignment = {}
for nurse_id in range(1, 27):
    for shift_number in range(1, 15):
        work_assignment[nurse_id, shift_number] = model.addVar(vtype=GRB.BINARY, name=f"work_{nurse_id}_{shift_number}")

shift_coverage = {}
for shift_number in range(1, 15):
    shift_coverage[shift_number] = model.addVar(vtype=GRB.BINARY, name=f"shift_coverage_{shift_number}")

rest_between_shifts = {}
for i in range(1, 27):
    for j in range(1, 15):
        rest_between_shifts[i, j] = model.addVar(vtype=GRB.BINARY, name=f"rest_{i}_{j}")

# Set objective function
total_cost = 0
for nurse_id in range(1, 27):
    for shift_number in range(1, 15):
        total_cost += work_assignment[nurse_id, shift_number] * df.loc[nurse_id - 1, 'Cost_Weekday']

max_overtime_cost = df['Cost_Overtime'].max()  # Get maximum overtime cost
# Track the total number of overtime shifts
total_overtime_shifts = sum(rest_between_shifts[i, j] for i in range(1, 27) for j in range(1, 14))
#total_overtime_shifts = sum(rest_between_shifts[nurse_id, shift_number] for nurse_id in range(1, 27) for shift_number in range(1, 14))
model.setObjective(total_cost + max_overtime_cost * total_overtime_shifts, GRB.MINIMIZE)

# Add constraints
for shift_number in range(1, 15):
    model.addConstr(sum(work_assignment[nurse_id, shift_number] for nurse_id in range(1, 27)) >= 6)

for nurse_id in range(1, 27):
    model.addConstr(sum(work_assignment[nurse_id, shift_number] * shift_hours_per_day for shift_number in range(1, 15)) >= 36)
    model.addConstr(sum(work_assignment[nurse_id, shift_number] * shift_hours_per_day for shift_number in range(1, 15)) <= 60)

for shift_number in range(1, 15):
    model.addConstr(sum(work_assignment[nurse_id, shift_number] for nurse_id in range(1, 27)) >= shift_coverage[shift_number])

for nurse_id in range(1, 27):
    for shift_number in range(1, 13):
        model.addConstr(rest_between_shifts[nurse_id, shift_number] + rest_between_shifts[nurse_id, shift_number + 1] <= 1)

# Solve the model
model.optimize()

# Print results
if model.status == GRB.OPTIMAL:
    print("Optimal solution found.")
    print("Total staffing cost:", model.objVal)
    print("Number of overtime shifts:", total_overtime_shifts)
else:
    print("No optimal solution found.")


