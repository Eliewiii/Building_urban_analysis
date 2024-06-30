import random
from deap import base, creator, tools, algorithms

# Define categories for the categorical variable
CATEGORIES = ['A', 'B', 'C']


# Define the evaluation function
def eval_func(individual):
    int_var_1 = int(individual[0])
    int_var_2 = int(individual[1])
    float_var_1 = individual[2]
    float_var_2 = individual[3]
    cat_var_index = int(individual[4])

    # Get the actual categorical value
    cat_var = CATEGORIES[cat_var_index]

    # Example objective function
    objective_value = int_var_1 + int_var_2 + float_var_1 + float_var_2 + (1 if cat_var == 'A' else 0)

    return objective_value


# Configure DEAP
creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
creator.create("Individual", list, fitness=creator.FitnessMin)

toolbox = base.Toolbox()
toolbox.register("attr_int", random.randint, 0, 5)  # Integer attribute with bounds 0 to 5
toolbox.register("attr_float", random.uniform, 0, 5)  # Float attribute with bounds 0 to 5
toolbox.register("attr_cat", random.randint, 0, len(CATEGORIES) - 1)  # Categorical attribute index

toolbox.register("individual", tools.initCycle, creator.Individual,
                 (toolbox.attr_int, toolbox.attr_int, toolbox.attr_float, toolbox.attr_float,
                  toolbox.attr_cat), n=1)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

toolbox.register("evaluate", eval_func)
toolbox.register("mate", tools.cxBlend, alpha=0.5)  # Blend crossover for numerical values
toolbox.register("mutate", tools.mutGaussian, mu=0, sigma=1,
                 indpb=0.2)  # Gaussian mutation for numerical values
toolbox.register("select", tools.selBest)


def main():
    pop = toolbox.population(n=50)
    algorithms.eaSimple(pop, toolbox, cxpb=0.5, mutpb=0.2, ngen=50, verbose=False)

    best_individual = tools.selBest(pop, k=1)[0]
    best_int_var_1 = int(best_individual[0])
    best_int_var_2 = int(best_individual[1])
    best_float_var_1 = best_individual[2]
    best_float_var_2 = best_individual[3]
    best_cat_var_index = int(best_individual[4])
    best_cat_var = CATEGORIES[best_cat_var_index]

    print("Best integer variables:", best_int_var_1, best_int_var_2)
    print("Best float variables:", best_float_var_1, best_float_var_2)
    print("Best categorical variable index:", best_cat_var_index)
    print("Best categorical variable:", best_cat_var)


if __name__ == "__main__":
    main()
