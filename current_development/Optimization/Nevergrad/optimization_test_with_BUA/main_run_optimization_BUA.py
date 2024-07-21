"""
Main script to run optimization with Nevergrad using the BUA evaluation function
"""
import nevergrad as ng

from nevergrad.optimization.optimizerlib import OnePlusOne

from bua.utils.utils_import_simulation_steps_and_config_var import *

from current_development.Optimization.Nevergrad.optimization_test_with_BUA.eval_function import eval_func_wrapper
from current_development.Optimization.Nevergrad.optimization_test_with_BUA.fitness_functions import \
    environmental_oriented_fitness_func
from current_development.Optimization.Nevergrad.optimization_test_with_BUA.design_variable_definition_and_boundaries import \
    roof_inverter_sizing_ratio_dv, facades_inverter_sizing_ratio_dv, min_panel_eroi_dv, \
    replacement_frequency_dv, roof_panel_id_dv, facades_panel_id_dv
from current_development.Optimization.Nevergrad.optimization_test_with_BUA.json_result_dict_methods import init_json_results_dict, \
    finalize_json_results_dict


def run_optimization_bua(path_json_results_file: str,
                         optimization_algorithm=OnePlusOne,
                         fitness_function=environmental_oriented_fitness_func,
                         budget=20):
    """

    """
    # Initialize json file with the result from each iteration
    init_json_results_dict(path_json_file=path_json_results_file)

    # Read the Urban Canopy object (assumed to be in the default simulation folder)
    urban_canopy_object = SimulationCommonMethods.create_or_load_urban_canopy_object(
        path_simulation_folder=default_path_simulation_folder)

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
        eval_func_wrapper(urban_canopy_obj=urban_canopy_object, fitness_func=fitness_function,
                          path_json_results_file=path_json_results_file), verbosity=0)

    # # Print the best individual
    print(f"optimized value: \n")
    print(f"{variable} : {recommendation.kwargs[variable]} \n" for variable in list(recommendation.kwargs))

    # Save the best individual in the json file
    finalize_json_results_dict(path_json_file=path_json_results_file, recommendation=recommendation)


if __name__ == "__main__":
    run_optimization_bua(path_json_results_file="results.json",
                         optimization_algorithm=OnePlusOne,
                         fitness_function=environmental_oriented_fitness_func,
                         budget=5)
