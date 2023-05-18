def linear_efficiency_loss(initial_efficiency, age):
    return initial_efficiency - age * 0.75


def get_efficiency_loss_function_from_string(name_function):
    if name_function == "linear_efficiency_loss":
        return linear_efficiency_loss()
