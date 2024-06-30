import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import differential_evolution
import time

progress = []
progress_obj = []


def my_rosenbrock(x):
    y = 100 * (x[1] - x[0] ** 2) ** 2 + (1 - x[0]) ** 2
    return y


def cb(x, convergence):
    progress.append(x)
    f = my_rosenbrock(x)
    progress_obj.append(f)
    return False


bounds = [(-2, 2), (-2, 2)]
my_population = 50
my_maxiter = 1000
start = time.time()

result = differential_evolution(func=my_rosenbrock, bounds=bounds, popsize=my_population, maxiter=my_maxiter,
                                disp=True, polish=False, updating='immediate',
                                callback=cb, atol=1e-5, tol=1e-5)

end = time.time()

print('Optimization finished!')
print(result)
print('Results from optimizer:')
print(result.x, result.fun)
print('Elapsed time [min]: ', (end - start) / 60.0)

plt.figure()
plt.plot(progress_obj)
plt.xlabel('iteration')
plt.ylabel('Obj')
plt.savefig("opt_hist.jpg")
plt.show()
