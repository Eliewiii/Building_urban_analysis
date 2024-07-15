"""
todo
"""


def degrading_rate_efficiency_loss(initial_efficiency, age, first_year_degrading_rate=0.02, degrading_rate=0.005):
    """ loose 2% efficiency the first year and then 0.5% every year"""
    return initial_efficiency * (1-first_year_degrading_rate) * (1 - degrading_rate) ** (age-1)


def get_efficiency_loss_function_from_string(name_function):
    """todo"""
    if name_function == "degrading_rate_efficiency_loss":
        return degrading_rate_efficiency_loss
