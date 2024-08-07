"""
Main script to run optimization with Nevergrad using the BUA evaluation function
"""
from typing import Callable, List, Tuple

import nevergrad as ng

from nevergrad.optimization.optimizerlib import OnePlusOne

from bua.utils.utils_import_simulation_steps_and_config_var import *

from current_development.Optimization.Nevergrad.optimization_test_with_BUA.in_parallel.eval_function_parallel import \
    eval_func_with_multiple_run_wrapper
from current_development.Optimization.Nevergrad.optimization_test_with_BUA.fitness_functions import \
    environmental_oriented_fitness_func, eroi_only_fitness_func
from current_development.Optimization.Nevergrad.optimization_test_with_BUA.design_variable_definition_and_boundaries import \
    roof_inverter_sizing_ratio_dv, facades_inverter_sizing_ratio_dv, min_panel_eroi_dv, \
    replacement_frequency_dv, roof_panel_id_dv, facades_panel_id_dv
from current_development.Optimization.Nevergrad.optimization_test_with_BUA.json_result_dict_methods import \
    init_json_results_dict, finalize_json_results_dict

from current_development.Optimization.Nevergrad.optimization_test_with_BUA.utils_opt import duplicate_folder


def run_optimization_bua(path_json_results_file: str,
                         optimization_algorithm=OnePlusOne,
                         fitness_function: Callable = environmental_oriented_fitness_func,
                         budget: int = 20,
                         path_optimization_simulation_folder: str = r"D:\Simulation",
                         nb_run_per_iteration: int = 1,
                         num_workers: int = 1):
    """

    """
    # Initialize json file with the result from each iteration
    init_json_results_dict(path_json_file=path_json_results_file)

    # Duplicate the default simulation folder for each run in the optimization simulation folder
    list_path_run_folders = []
    for i in range(nb_run_per_iteration):
        path_it_simulation_folder = os.path.join(path_optimization_simulation_folder, f"run_{i}")
        duplicate_folder(src_folder=default_path_simulation_folder, dest_folder=path_it_simulation_folder, overwrite=True)
        list_path_run_folders.append(path_it_simulation_folder)

    # Read the Urban Canopy objects
    urban_canopy_object_list = [ SimulationCommonMethods.create_or_load_urban_canopy_object(
        path_simulation_folder=path_it_simulation_folder) for path_it_simulation_folder in
        list_path_run_folders]

    # Convert the Urban Canopy objects to a list of tuples with the associated simulation folder path
    urban_canopy_and_path_sim_folder_tuple_list = [(urban_canopy_object, path_it_simulation_folder) for
                                                   urban_canopy_object, path_it_simulation_folder in
                                                   zip(urban_canopy_object_list, list_path_run_folders)]
    # Define the instrumentation
    instrumentation = ng.p.Instrumentation(
        roof_panel_id=roof_panel_id_dv,
        facades_panel_id=facades_panel_id_dv,
        roof_inverter_sizing_ratio=roof_inverter_sizing_ratio_dv,
        facades_inverter_sizing_ratio=facades_inverter_sizing_ratio_dv,
        min_panel_eroi=min_panel_eroi_dv,
        replacement_frequency=replacement_frequency_dv
    )

    # Define the search space with different boundaries
    optimizer = optimization_algorithm(parametrization=instrumentation, budget=budget,
                                       num_workers=1)

    # Run the optimization
    recommendation = optimizer.minimize(
        eval_func_with_multiple_run_wrapper(urban_canopy_and_path_sim_folder_tuple_list=urban_canopy_and_path_sim_folder_tuple_list, fitness_func=fitness_function,
                          path_json_results_file=path_json_results_file,num_workers=num_workers), verbosity=1)

    # # Print the best individual
    print(f"optimized value: \n")
    print(f"{variable} : {recommendation.kwargs[variable]} \n" for variable in list(recommendation.kwargs))

    # Save the best individual in the json file
    finalize_json_results_dict(path_json_file=path_json_results_file, recommendation=recommendation)


if __name__ == "__main__":
    # run_optimization_bua(path_json_results_file="results.json",
    #                      optimization_algorithm=OnePlusOne,
    #                      fitness_function=environmental_oriented_fitness_func,
    #                      budget=20)

    run_optimization_bua(path_json_results_file=r"../Saved_results/results_test_Nicolo.json",
                         optimization_algorithm=OnePlusOne,
                         fitness_function=eroi_only_fitness_func,
                         budget=100,
                         num_workers=8,
                         nb_run_per_iteration=8
                         )
