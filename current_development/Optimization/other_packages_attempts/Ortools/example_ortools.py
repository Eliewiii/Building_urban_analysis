from ortools.linear_solver import pywraplp

# Define categories for the categorical variable
CATEGORIES = ['A', 'B', 'C']

def eval_func(int_var_1, int_var_2, float_var_1, float_var_2, cat_var_index):
    # Example evaluation function
    cat_var_index_val = int(cat_var_index.solution_value())
    cat_var_value = CATEGORIES[int(cat_var_index_val)]
    print(cat_var_value)

    objective_value = int_var_1 - int_var_2**2 + float_var_1 + float_var_2 + (1 if cat_var_value == 'A' else 0)
    constraint_value = int_var_1 * float_var_1 - int_var_2 * float_var_2
    return objective_value, constraint_value

def main():
    # Create the solver
    solver = pywraplp.Solver.CreateSolver('SAT')
    if not solver:
        return

    # Set solver parameters
    solver.SetTimeLimit(30000)  # Set a time limit of 30 seconds (in milliseconds)
    solver.SetNumThreads(1)     # Use 4 threads for solving

    # Define decision variables
    int_var_1 = solver.IntVar(0, 5, 'int_var_1')
    int_var_2 = solver.IntVar(5, 10, 'int_var_2')
    float_var_1 = solver.NumVar(0, 5, 'float_var_1')
    float_var_2 = solver.NumVar(5, 10, 'float_var_2')
    cat_var_index = solver.IntVar(0, len(CATEGORIES) - 1, 'cat_var')

    # # Define the objective function
    # objective = solver.Objective()
    # objective.SetCoefficient(int_var_1, 1)
    # objective.SetCoefficient(int_var_2, 1)
    # objective.SetCoefficient(float_var_1, 1)
    # objective.SetCoefficient(float_var_2, 1)
    # objective.SetCoefficient(cat_var_index, 0)  # Handled separately

    # Define additional variables for evaluation function results
    eval_objective = solver.NumVar(-solver.infinity(), solver.infinity(), 'eval_objective')
    eval_constraint = solver.NumVar(-solver.infinity(), solver.infinity(), 'eval_constraint')

    # Set evaluation function results as constraints
    objective_value, constraint_value = eval_func(int_var_1, int_var_2, float_var_1, float_var_2, cat_var_index)
    solver.Add(eval_objective == objective_value)
    solver.Add(eval_constraint == constraint_value)

    # Add constraint to ensure eval_constraint is non-negative
    solver.Add(eval_constraint >= 0)

    # Objective: maximize eval_objective
    solver.Maximize(eval_objective)

    # Solve the problem
    status = solver.Solve()

    # Print the results
    if status == pywraplp.Solver.OPTIMAL:
        print(f'Optimal objective value = {solver.Objective().Value()}')
        print(f'Best integer variables: {int(int_var_1.solution_value())}, {int(int_var_2.solution_value())}')
        print(f'Best float variables: {float_var_1.solution_value()}, {float_var_2.solution_value()}')
        print(f'Best categorical variable index: {int(cat_var_index.solution_value())}')
        print(f'Best categorical variable: {CATEGORIES[int(cat_var_index.solution_value())]}')
    else:
        print('The problem does not have an optimal solution.')

if __name__ == '__main__':
    main()
