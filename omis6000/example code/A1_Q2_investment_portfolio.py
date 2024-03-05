"""
@author: Group 12 (2024 Winter)
"""

from gurobipy import GRB
import gurobipy as gb

# Create the optimization model
model = gb.Model("Sunnyshore Bay")

IR = [1 + 1.75/100, 1 + 2.25/100, 1 + 2.75/100]

# Create the three classes of decision variables where each Python
# variable represents a different number of Gurobi decision variables
B1 = model.addVars(3, lb=0, vtype=GRB.CONTINUOUS, name="Borrow_May")
B2 = model.addVars(2, lb=0, vtype=GRB.CONTINUOUS, name="Borrow_Jun")
B3 = model.addVars(1, lb=0, vtype=GRB.CONTINUOUS, name="Borrow_Jul")

# auxiliary decision variables (cash balance at the end of period)
w = model.addVars(4, lb=0, vtype=GRB.CONTINUOUS, name="Wealth")

# The objective function
Loan_may = gb.quicksum(B1[i]*IR[i] for i in range(3))
Loan_jun = gb.quicksum(B2[i]*IR[i] for i in range(2))
Loan_jul = B3[0]*IR[0]
model.setObjective(Loan_may + Loan_jun + Loan_jul, GRB.MINIMIZE)

# Add the constraints
model.addConstr(w[0] == 140000 + 180000 + B1[0] + B1[1] + B1[2] - 300000, "May Constraint")
model.addConstr(w[1] == w[0] + B2[0] + B2[1] + 260000 - IR[0]*B1[0] - 400000, "Jun Constraint")
model.addConstr(w[2] == w[1] + B3[0] + 420000 - 350000 - IR[1]*B1[1] - B2[0]*IR[0], "Jul Constraint")
model.addConstr(w[3] == w[2] + 580000 - 200000 - B1[2]*IR[2] - B2[1]*IR[1] - B3[0]*IR[0], "Aug Constraint")

# We could also define these constraints as upper bounds in the definition of the decision variables
model.addConstr(B1[0] + B1[1] + B1[2] <= 250000, "Borrowing Constraint May")
model.addConstr(B2[0] + B2[1] <= 150000, "Borrowing Constraint Jun")
model.addConstr(B3[0] <= 350000, "Borrowing Constraint May")

# Cash balance constraint
cash_may = model.addConstr(w[0] >= 25000, "Cash Constraint May")
cash_jun = model.addConstr(w[1] >= 20000, "Cash Constraint Jun")
cash_jul = model.addConstr(w[2] >= 35000, "Cash Constraint Jul")
cash_aug = model.addConstr(w[3] >= 18000, "Cash Constraint Aug")
cash_ratio = model.addConstr(w[2] >= (w[0] + w[1])*0.65, "Cash ratio constraint")

# Optimally solve the problem
model.optimize()

# Number of variables in the model
print("Number of Decision Variables: ", model.numVars)

# Number of constraints in the model
print("Number of Constraints: ", model.numConstrs)

# The status of the model
print("Model Status: ", model.status)

# Value of the objective function
print("Loan repayment:", model.objVal)

# Print the decision variables
print(model.printAttr('X'))

# Print sensitivity information
print("")
print(f"Sensitivity Information for Jun cash {cash_jun.pi:.2f}:")
print("(LHS, RHS, Slack): ", (model.getRow(cash_jun).getValue(), cash_jun.RHS, cash_jun.slack))
print("Shadow Price: ", cash_jun.pi)
print("Range of Feasibility: ", (cash_jun.SARHSUp, cash_jun.SARHSLow))

print("Additional repayment due to $7.5k increase in Jun cash: ", cash_jun.pi*7500)
print("Total repayment after: ", cash_jun.pi*7500 + model.objVal)

print("")
print("List of Shawdow Price")
for constr in model.getConstrs():
    print(f"{constr.ConstrName}: {constr.Pi}")