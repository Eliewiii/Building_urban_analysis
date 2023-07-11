"""
todo
"""

def degrading_rate_efficiency_loss(initial_efficiency, age, degrading_rate=0.005):
    """ todo"""
    return initial_efficiency * (1 - degrading_rate)**age


def get_efficiency_loss_function_from_string(name_function):
    """todo"""
    if name_function == "degrading_rate_efficiency_loss":
        return degrading_rate_efficiency_loss
