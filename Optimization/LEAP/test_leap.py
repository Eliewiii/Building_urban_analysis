import random
from leap_ec import ops
from leap_ec import context, Individual, Representation
from leap_ec.algorithm import generational_ea
from leap_ec import ops
from leap_ec.real_rep.ops import mutate_gaussian
from leap_ec.int_rep.ops import mutate_randint
from leap_ec.problem import FunctionProblem
from leap_ec.decoder import IdentityDecoder

from leap_ec.util import wrap_curry
from leap_ec.ops import compute_expected_probability, iteriter_op, random_bernoulli_vector

import math
from collections.abc import Iterable
from typing import Iterator, List, Tuple, Union



# Define categories for the categorical variable
CATEGORIES = ['A', 'B', 'C']


# Define the evaluation function
def eval_func(individual):
    x = individual.genome
    int_var_1 = int(x[0])
    int_var_2 = int(x[1])
    float_var_1 = x[2]
    float_var_2 = x[3]
    cat_var_index = int(x[4])

    # Ensure cat_var_index is within valid range
    if cat_var_index < 0 or cat_var_index >= len(CATEGORIES):
        raise ValueError(
            f"Invalid cat_var_index: {cat_var_index}. Must be within range [0, {len(CATEGORIES) - 1}]")

    # Get the actual categorical value
    cat_var = CATEGORIES[cat_var_index]

    # For demonstration, print the values
    print(f"Input vector: {x}")
    print(f"Integer variables: {int_var_1}, {int_var_2}")
    print(f"Float variables: {float_var_1}, {float_var_2}")
    print(f"Categorical variable index: {cat_var_index}")
    print(f"Categorical variable: {cat_var}\n")

    # Example objective function
    objective_value = int_var_1 + int_var_2 + float_var_1 + float_var_2 + (1 if cat_var == 'A' else 0)

    return objective_value

# Define the problem
problem = FunctionProblem(eval_func, maximize=False)


# Custom initialization function
def initialize_genome(bounds):
    genome = []
    for i, bound in enumerate(bounds):
        if types[i] == 'int':
            genome.append(random.randint(bound[0], bound[1]))
        else:
            genome.append(random.uniform(bound[0], bound[1]))
    return genome

# Custom mutation function
@wrap_curry
@iteriter_op
def custom_mutation(individual, p_mutation=0.1, bounds=None, types=None):
    for i in range(len(individual.genome)):
        if random.random() < p_mutation:
            if types[i] == 'int':
                individual.genome[i] = random.randint(bounds[i][0], bounds[i][1])
            else:
                individual.genome[i] = random.uniform(bounds[i][0], bounds[i][1])
    return individual


@wrap_curry
@iteriter_op
def custom_mutation(next_individual: Iterator,
                    std,
                    bounds=(-math.inf, math.inf),
                    transform_slope: float = 1.0,
                    transform_intercept: float = 0.0) -> Iterator:
    """Mutate and return an Individual with a real-valued representation.

    This operators on an iterator of Individuals:
    :param next_individual: to be mutated
    :param std: standard deviation to be equally applied to all individuals;
        this can be a scalar value or a "shadow vector" of standard deviations
    :param expected_num_mutations: if an int, the *expected* number of mutations per
        individual, on average.  If 'isotropic', all genes will be mutated.
    :param bounds: to clip for mutations; defaults to (- ∞, ∞)
    :return: a generator of mutated individuals.
    """
    if expected_num_mutations is None:
        raise ValueError(
            "No value given for expected_num_mutations.  Must be either a float or the string 'isotropic'.")

    genome_mutator = genome_mutate_gaussian(std=std,
                                            expected_num_mutations=expected_num_mutations,
                                            bounds=bounds,
                                            transform_slope=transform_slope,
                                            transform_intercept=transform_intercept)

    while True:
        individual = next(next_individual)

        individual.genome = genome_mutator(individual.genome)
        # invalidate fitness since we have new genome
        individual.fitness = None

        yield individual


##############################
# Function genome_mutate_gaussian
##############################
@wrap_curry
def genome_mutate_gaussian(genome,
                           std: float,
                           expected_num_mutations,
                           bounds: Tuple[float, float] =
                           (-math.inf, math.inf),
                           transform_slope: float = 1.0,
                           transform_intercept: float = 0.0):
    """Perform Gaussian mutation directly on real-valued genes (rather than
    on an Individual).

    This used to be inside `mutate_gaussian`, but was moved outside it so that
    `leap_ec.segmented.ops.apply_mutation` could directly use this function,
    thus saving us from doing a copy-n-paste of the same code to the segmented
    sub-package.

    :param genome: of real-valued numbers that will potentially be mutated
    :param std: the mutation width—either a single float that will be used for
        all genes, or a list of floats specifying the mutation width for
        each gene individually.
    :param expected_num_mutations: on average how many mutations are expected
    :return: mutated genome
    """
    assert (std is not None)
    assert (isinstance(std, Iterable) or (std >= 0.0))
    assert (expected_num_mutations is not None)

    if isinstance(std, Iterable):
        std = np.array(std)

    # compute actual probability of mutation based on expected number of
    # mutations and the genome length

    if not isinstance(genome, np.ndarray):
        raise ValueError(("Expected genome to be a numpy array. "
                          f"Got {type(genome)}."))

    if expected_num_mutations == 'isotropic':
        # Default to isotropic Gaussian mutation
        p = 1.0
    else:
        p = compute_expected_probability(expected_num_mutations, genome)

    # select which indices to mutate at random
    indices_to_mutate = random_bernoulli_vector(shape=genome.shape, p=p)

    # Pick out just the std values we need for the mutated genes
    std_selected = std if not isinstance(std, Iterable) else std[indices_to_mutate]

    # Apply additive Gaussian noise to the selected genes
    new_gene_values = transform_slope * (genome[indices_to_mutate] \
                                         + np.random.normal(size=sum(indices_to_mutate)) \
                                         # scalar multiply if scalar; element-wise if std is an ndarray
                                         * std_selected) \
                      + transform_intercept
    genome[indices_to_mutate] = new_gene_values

    # Implement hard bounds
    genome = apply_hard_bounds(genome, bounds)

    return genome


# Max number of generations
generations = 50

# Define genome bounds
bounds = [
    (0, 5),  # Integer variable 1 with bounds 0 to 5
    (5, 10),  # Integer variable 2 with bounds 5 to 10
    (0, 5),  # Float variable 1 with bounds 0 to 5
    (5, 10),  # Float variable 2 with bounds 5 to 10
    (0, len(CATEGORIES) - 1)  # Categorical variable with 3 categories
]


types = ['int', 'int', 'float', 'float', 'int']

# Create the initial population
pop_size = 1
population = iter([Individual(initialize_genome(bounds=bounds))])


# Define the problem
problem = FunctionProblem(eval_func, maximize=False)


mutate_gauss_op = mutate_gaussian(std=1.0, bounds=bounds, expected_num_mutations=1)
custom_mutation_op = custom_mutation(bounds=bounds, types=types)

# Create an evolutionary algorithm
ea = generational_ea(
    max_generations=generations,
    pop_size=pop_size,
    k_elites=1,
    problem=problem,
    representation=Representation(
        individual_cls=Individual,
        initialize=initialize_genome(bounds=bounds),
        decoder=IdentityDecoder()
    ),
    pipeline=[
        ops.tournament_selection,
        ops.clone,
        ops.UniformCrossover(p_swap=0.5),
        mutate_gauss_op,
        custom_mutation_op(bounds=bounds, types=types),
        ops.evaluate
    ]
)

# Run the evolutionary algorithm
final_population = ea(population)

# Extract the best individual
best_individual = min(final_population, key=lambda ind: ind.fitness)
best_int_var_1 = int(best_individual.genome[0])
best_int_var_2 = int(best_individual.genome[1])
best_float_var_1 = best_individual.genome[2]
best_float_var_2 = best_individual.genome[3]
best_cat_var_index = int(best_individual.genome[4])
best_cat_var = CATEGORIES[best_cat_var_index]

# Print the best individual
print(f"Best integer variables: {best_int_var_1}, {best_int_var_2}")
print(f"Best float variables: {best_float_var_1}, {best_float_var_2}")
print(f"Best categorical variable index: {best_cat_var_index}")
print(f"Best categorical variable: {best_cat_var}")
