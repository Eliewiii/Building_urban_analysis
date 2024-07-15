import sys
import os

from urban_canopy.urban_canopy import UrbanCanopy

import nevergrad as ng
import numpy as np

from Optimization.Nevergrad.optimization_test_with_BUA.json_result_dict_methods import \
    update_json_results_dict
from Optimization.Nevergrad.optimization_test_with_BUA.design_variable_definition_and_boundaries import \
    ROOF_PANEL_TECHNOLOGIES_DICT, FACADES_PANEL_TECHNOLOGIES_DICT, REPLACEMENT_FREQUENCY_MULTIPLIER


def eval_func(urban_canopy_obj: UrbanCanopy, fitness_func, path_json_results_file: str,
              roof_panel_id: int, facades_panel_id: int, roof_inverter_sizing_ratio: float,
              facades_inverter_sizing_ratio: float, min_panel_eroi: float, replacement_frequency: int):
    """

    """
    # Adjust inputs
    roof_panel_id = ROOF_PANEL_TECHNOLOGIES_DICT[roof_panel_id]
    facades_panel_id = FACADES_PANEL_TECHNOLOGIES_DICT[facades_panel_id]
    replacement_frequency = replacement_frequency * REPLACEMENT_FREQUENCY_MULTIPLIER  # The replacement frequency is multiplied by 5

    # run BIPV simulation

    # Run KPI

    # extract the KPI dict
    kpi_dict = urban_canopy_obj.get_kpi()  # something like this

    fitness_value = fitness_func(kpi_dict)

    update_json_results_dict(path_json_results_file=path_json_results_file, fitness_value=fitness_value,
                             kpi_dict=kpi_dict)

    return fitness_value


# Function to wrap the eval_func with a custom object
def eval_func_wrapper(urban_canopy_obj, fitness_func, path_json_results_file):
    def wrapped_eval_func(**kwargs):
        return eval_func(urban_canopy_obj, fitness_func, path_json_results_file, **kwargs)

    return wrapped_eval_func


def suppress_print_wrapper(func, *args, **kwargs):
    # Save the current stdout so we can restore it later
    original_stdout = sys.stdout
    # Redirect stdout to null
    sys.stdout = open(os.devnull, 'w')
    try:
        result = func(*args, **kwargs)
    finally:
        # Restore stdout to its original state
        sys.stdout = original_stdout
    return result


if __name__ == "__main__":
    suppress_print_wrapper(print, "Hello, world!")
