def linear_efficiency_loss(initial_efficiency, age, degrading_rate=0.75):
    return initial_efficiency - age * degrading_rate


def get_efficiency_loss_function_from_string(name_function):
    if name_function == "linear_efficiency_loss":
        return linear_efficiency_loss()
