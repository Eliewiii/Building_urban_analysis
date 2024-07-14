import sys
import os

from urban_canopy.urban_canopy import UrbanCanopy

import nevergrad as ng
import numpy as np



def eval_func(urban_canopy_obj : UrbanCanopy,fitness_func ,id_roof_technology :str =""):
    """

    """
    # run BIPV simulation

    #Run KPI

    # extract the KPI dict
    kpi_dict = urban_canopy_obj.get_kpi()  # something like this

    eval_it = fitness_func(kpi_dict)

    return "zob"





# Function to wrap the eval_func with a custom object
def eval_func_wrapper(urban_canopy_obj,fitness_func,path_json_results_file):
    def wrapped_eval_func(**kwargs):
        return eval_func(urban_canopy_obj,fitness_func,path_json_results_file, **kwargs)
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

if __name__=="__main__":
    suppress_print_wrapper(print, "Hello, world!")

