import nevergrad as ng
import numpy as np

# Define categories for the categorical variable
CATEGORIES = ['A', 'B', 'C']


# Define the evaluation function
def eval_func(int_var_1=0,int_var_2=0,float_var_1=0,float_var_2=0,cat_var=0):
    print (int_var_1)
    # x = [kwargs[key] for key in kwargs.keys()]
    #
    # # Extract the integer variables with different boundaries
    # int_var_1 = int(x[0])
    # int_var_2 = int(x[1])
    #
    # # Extract the float variables with different boundaries
    # float_var_1 = x[2]
    # float_var_2 = x[3]
    #
    # # Extract the categorical variable index
    # cat_var_index = int(x[4])

    # Get the actual categorical value
    cat_var = CATEGORIES[cat_var]

    if cat_var == 'A':
        constraint = False
    else:
        constraint = True

    # For demonstration, print the values
    # print(f"Input vector: {x}")
    # print(f"Integer variables: {int_var_1}, {int_var_2}")
    # print(f"Float variables: {float_var_1}, {float_var_2}")
    # print(f"Categorical variable index: {cat_var_index}")
    # print(f"Categorical variable: {cat_var}\n")

    # Example objective function
    objective_value = int_var_1 + int_var_2 + float_var_1 + float_var_2 + (1 if cat_var == 'A' else 0)

    # print(
    #     f"Int_var_1: {int_var_1}, Int_var_2: {int_var_2}, Float_var_1: {float_var_1}, Float_var_2: {float_var_2}, Cat_var: {cat_var}, Objective: {objective_value}")

    # Note: Nevergrad minimizes the objective by default, so we negate it
    return -objective_value


# Define the search space with different boundaries
instrumentation = ng.p.Instrumentation(
    int_var_1=ng.p.Scalar(lower=0, upper=5).set_integer_casting(),  # Integer variable 1 with bounds 0 to 5
    int_var_2=ng.p.Scalar(lower=5, upper=10).set_integer_casting(),  # Integer variable 2 with bounds 5 to 10
    float_var_1=ng.p.Scalar(lower=0, upper=5),  # Float variable 1 with bounds 0 to 5
    float_var_2=ng.p.Scalar(lower=5, upper=10),  # Float variable 2 with bounds 5 to 10
    cat_var=ng.p.Choice(range(len(CATEGORIES)))  # Categorical variable with 3 categories
)

budget = 10

# Choose an optimizer
# optimizer = ng.optimizers.OnePlusOne(parametrization=instrumentation, budget=budget, num_workers=1)
# optimizer = ng.optimizers.NgIohTuned(parametrization=instrumentation, budget=budget, num_workers=1)
optimizer = ng.optimizers.DiscreteOnePlusOne(parametrization=instrumentation, budget=budget, num_workers=1)
# optimizer = ng.optimizers.PortfolioDiscreteOnePlusOne(parametrization=instrumentation, budget=budget, num_workers=1)


# Run the optimization
recommendation = optimizer.minimize(eval_func, verbosity=0)

# Extract the best individual
best_individual = recommendation.kwargs['int_var_1']
best_int_var_1 = int(best_individual)
best_int_var_2 = int(recommendation.kwargs['int_var_2'])
best_float_var_1 = recommendation.kwargs['float_var_1']
best_float_var_2 = recommendation.kwargs['float_var_2']
best_cat_var_index = int(recommendation.kwargs['cat_var'])
best_cat_var = CATEGORIES[best_cat_var_index]

# # Print the best individual
print(
    f"Best integer variables: {best_int_var_1}, {best_int_var_2}, Best float variables: {best_float_var_1}, "
    f"{best_float_var_2}, Best categorical variable index: {best_cat_var_index},"
    f"Best categorical variable: {best_cat_var}")

# print(recommendation.value)
