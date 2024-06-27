import numpy as np


def generate_inverse_squared_values(N, min_value):
    # Ensure min_value is not zero to avoid division by zero
    if min_value == 0:
        raise ValueError("Minimum value cannot be zero.")

    # Generate N values uniformly spaced between 0 and 1
    inverse_values = np.array([1/i for i in range(1,N+1)])
    inverse_squared_values = inverse_values ** 2.

    return inverse_values,inverse_squared_values



# Example usage
N = 30
min_value = 0.1

values = generate_inverse_squared_values(N, min_value)
print(values[0])
print(values[1])
