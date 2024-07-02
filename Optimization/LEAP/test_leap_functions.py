from leap_ec.individual import Individual
from leap_ec.real_rep.ops import mutate_gaussian
import numpy as np

pop = iter([Individual(np.array([1.0, 0.0]))])

op = mutate_gaussian(std=1.0, expected_num_mutations='isotropic', bounds=(-5, 5))
mutated = next(op(pop))

pop = iter([Individual(np.array([1.0, 0.0]))])
bounds = [(-1, 1), (-10, 10)]
op = mutate_gaussian(std=1.0, bounds=bounds, expected_num_mutations=1)
print(type(op))
mutated = next(op(pop))
