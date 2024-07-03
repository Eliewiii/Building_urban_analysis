from ortools.linear_solver import pywraplp

def eval_function(x, y):
    # Define the objective function to maximize: f(x, y) = x + y
    return x**2 - y

def main():
    # Create the solver
    solver = pywraplp.Solver.CreateSolver('CBC')
    if not solver:
        return

    # Set solver parameters
    solver.SetTimeLimit(30000)  # Set a time limit of 30 seconds (in milliseconds)
    solver.SetNumThreads(1)     # Use 1 thread for solving

    # Define decision variables
    x = solver.IntVar(0, 10, 'x')
    y = solver.IntVar(0, 10, 'y')

    # Define the objective function to maximize using eval_function
    objective = solver.Maximize(eval_function(x, y))

    # Solve the problem
    status = solver.Solve()

    # Print the results
    if status == pywraplp.Solver.OPTIMAL:
        print(f'Optimal objective value = {solver.Objective().Value()}')
        print(f'Value of x: {x.solution_value()}')
        print(f'Value of y: {y.solution_value()}')
        print("\nAdvanced usage:")
        print(f"Problem solved in {solver.wall_time():d} milliseconds")
        print(f"Problem solved in {solver.iterations():d} iterations")
        print(f"Problem solved in {solver.nodes():d} branch-and-bound nodes")
    else:
        print('The problem does not have an optimal solution.')

if __name__ == '__main__':
    main()
