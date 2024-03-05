
from sympy import symbols, Eq, solve

# Define symbols
p1, p2, lambda1, lambda2, s1, s2 = symbols('p1 p2 lambda1 lambda2 s1 s2')

# Define the objective function
objective_function = p1 * (35234.5458 - 45.8964 * p1) + p2 * (37790.2408 - 8.2278 * p2)

# Define slack variables
slack1 = 35234.5458 - 45.8964 * p1 - s1
slack2 = 37790.2408 - 8.2278 * p2 - s2
slack3 = p1 - p2

# Define KKT conditions
kkt_condition1 = Eq(objective_function.diff(p1) + lambda1 * slack1, 0)
kkt_condition2 = Eq(objective_function.diff(p2) + lambda2 * slack2, 0)
kkt_condition3 = Eq(slack1 * lambda1, 0)
kkt_condition4 = Eq(slack2 * lambda2, 0)

# 解决方案字典
solution = solve((kkt_condition1, kkt_condition2, kkt_condition3, kkt_condition4), (p1, p2, lambda1, lambda2), dict=True)[0]

# 提取并打印最优价格
optimal_p1 = solution[p1]
optimal_p2 = solution[p2]

print("Optimal Price for P1:", optimal_p1)
print("Optimal Price for P2:", optimal_p2)


