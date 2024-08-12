"""

"""

import sys

from typing import Callable, List, Tuple

from concurrent.futures import ProcessPoolExecutor

from bua.utils.utils_import_simulation_steps_and_config_var import *

from bua.urban_canopy.urban_canopy import UrbanCanopy

from current_development.vf_computation_with_radiance.vf_computation_with_radiance.utils.utils_parallel_computing_with_return import \
    parallel_computation_in_batches_with_return

from current_development.Optimization.Nevergrad.optimization_test_with_BUA.json_result_dict_methods import \
    update_json_results_dict
from current_development.Optimization.Nevergrad.optimization_test_with_BUA.design_variable_definition_and_boundaries import \
    ROOF_PANEL_TECHNOLOGIES_DICT, FACADES_PANEL_TECHNOLOGIES_DICT, REPLACEMENT_FREQUENCY_MULTIPLIER

from current_development.Optimization.Nevergrad.optimization_test_with_BUA.average_dict import average_dicts


def eval_func_with_multiple_run(urban_canopy_and_path_sim_folder_tuple_list: List[Tuple[UrbanCanopy, str]],
                                fitness_func: Callable,
                                path_json_results_file: str,
                                num_workers: int,
                                roof_panel_id: int, facades_panel_id: int, roof_inverter_sizing_ratio: float,
                                facades_inverter_sizing_ratio: float, min_panel_eroi: float,
                                replacement_frequency: int) -> float:
    """
    Function to compute the fitness value for the optimization.
    :param urban_canopy_and_path_sim_folder_tuple_list: tuple of UrbanCanopy object and associated simulation folder path,
        urban canopy object to run the simulation
    :param fitness_func: function, fitness function to compute the fitness value
    :param path_json_results_file: str, path to the json file to update
    :param num_workers: int, number of workers
    :param roof_panel_id: int, id of the roof panel technology
    :param facades_panel_id: int, id of the facades panel technology
    :param roof_inverter_sizing_ratio: float, inverter sizing ratio for the roof
    :param facades_inverter_sizing_ratio: float, inverter sizing ratio for the facades
    :param min_panel_eroi: float, minimum panel eroi
    :param replacement_frequency: int, replacement frequency in years
    :return: float, fitness value
    """
    # Adjust inputs
    roof_panel_id = ROOF_PANEL_TECHNOLOGIES_DICT[roof_panel_id]
    facades_panel_id = FACADES_PANEL_TECHNOLOGIES_DICT[facades_panel_id]
    replacement_frequency = replacement_frequency * REPLACEMENT_FREQUENCY_MULTIPLIER  # The replacement frequency is multiplied by 5

    fitness_value_and_kpi_dict_tuple_list = parallel_computation_in_batches_with_return(
        func=run_bipv_and_kpi_simulation,
        input_tables=urban_canopy_and_path_sim_folder_tuple_list,
        executor_type=ProcessPoolExecutor, batch_size=1,
        num_workers=num_workers,
        fitness_func=fitness_func,
        roof_panel_id=roof_panel_id,
        facades_panel_id=facades_panel_id,
        roof_inverter_sizing_ratio=roof_inverter_sizing_ratio,
        facades_inverter_sizing_ratio=facades_inverter_sizing_ratio,
        min_panel_eroi=min_panel_eroi,
        replacement_frequency=replacement_frequency)

    # fitness_value_and_kpi_dict_tuple_list = run_bipv_and_kpi_simulation(
    #     urban_canopy_object=urban_canopy_and_path_sim_folder_tuple_list[0][0],
    #     path_simulation_folder=urban_canopy_and_path_sim_folder_tuple_list[0][1],
    #     fitness_func=fitness_func,
    #     roof_panel_id=roof_panel_id,
    #     facades_panel_id=facades_panel_id,
    #     roof_inverter_sizing_ratio=roof_inverter_sizing_ratio,
    #     facades_inverter_sizing_ratio=facades_inverter_sizing_ratio,
    #     min_panel_eroi=min_panel_eroi,
    #     replacement_frequency=replacement_frequency)

    # Compute the average of the fitness and KPI values
    average_fitness_value = sum(
        [fitness_value for fitness_value, kpi_dict in fitness_value_and_kpi_dict_tuple_list]) / len(
        fitness_value_and_kpi_dict_tuple_list)
    average_kpi_dict = average_dicts(
        [kpi_dict for fitness_value, kpi_dict in fitness_value_and_kpi_dict_tuple_list])

    # Save the results in the json file
    update_json_results_dict(path_json_file=path_json_results_file, fitness_value=average_fitness_value,
                             kpi_dict=average_kpi_dict, roof_panel_id=roof_panel_id,
                             facades_panel_id=facades_panel_id,
                             roof_inverter_sizing_ratio=roof_inverter_sizing_ratio,
                             facades_inverter_sizing_ratio=facades_inverter_sizing_ratio,
                             min_panel_eroi=min_panel_eroi, replacement_frequency=replacement_frequency)

    return average_fitness_value


def run_bipv_and_kpi_simulation(urban_canopy_object: UrbanCanopy, path_simulation_folder: str,
                                fitness_func: Callable, roof_panel_id: int, facades_panel_id: int,
                                roof_inverter_sizing_ratio: float, facades_inverter_sizing_ratio: float,
                                min_panel_eroi: float, replacement_frequency: int) -> Tuple[float, dict]:
    """
    Function to run the BIPV and KPI simulation for the optimization.
    :param urban_canopy_object: UrbanCanopy object, urban canopy object to run the simulation
    :param path_simulation_folder: str, path to the simulation folder
    :param fitness_func: function, fitness function to compute the fitness value
    :param roof_panel_id: int, id of the roof panel technology
    :param facades_panel_id: int, id of the facades panel technology
    :param roof_inverter_sizing_ratio: float, inverter sizing ratio for the roof
    :param facades_inverter_sizing_ratio: float, inverter sizing ratio for the facades
    :param min_panel_eroi: float, minimum panel eroi
    :param replacement_frequency: int, replacement frequency in years
    :return Tuple[float, dict], fitness value and KPI dict
    """
    # Define bipv_scenario_identifier default
    bipv_scenario_identifier = "optimization_BUA"
    # run BIPV simulation
    suppress_print_wrapper(SimFunSolarRadAndBipv.run_bipv_harvesting_and_lca_simulation,
                           urban_canopy_object=urban_canopy_object,
                           path_simulation_folder=path_simulation_folder,
                           bipv_scenario_identifier=bipv_scenario_identifier,
                           roof_id_pv_tech=roof_panel_id,
                           facades_id_pv_tech=facades_panel_id,
                           roof_inverter_sizing_ratio=roof_inverter_sizing_ratio,
                           facades_inverter_sizing_ratio=facades_inverter_sizing_ratio,
                           minimum_panel_eroi=min_panel_eroi,
                           start_year=0,
                           end_year=50,
                           replacement_scenario="replace_failed_panels_every_X_years",
                           continue_simulation=False,
                           update_panel_technology=False,
                           replacement_frequency_in_years=replacement_frequency
                           )
    # Run KPI computation
    suppress_print_wrapper(SimFunSolarRadAndBipv.run_kpi_simulation, urban_canopy_object=urban_canopy_object,
                           path_simulation_folder=path_simulation_folder,
                           bipv_scenario_identifier=bipv_scenario_identifier,
                           grid_ghg_intensity=default_grid_ghg_intensity,
                           grid_energy_intensity=default_grid_energy_intensity,
                           grid_electricity_sell_price=default_grid_electricity_sell_price,
                           zone_area=None)

    # extract the KPI dict
    kpi_dict = urban_canopy_object.bipv_scenario_dict[
        bipv_scenario_identifier].urban_canopy_bipv_kpis_obj.to_dict()["kpis"]

    # Compute the fitness value
    fitness_value = fitness_func(kpi_dict)

    return [fitness_value, kpi_dict]


# Function to wrap the eval_func with a custom object
def eval_func_with_multiple_run_wrapper(urban_canopy_and_path_sim_folder_tuple_list, fitness_func,
                                        path_json_results_file, num_workers):
    def wrapped_eval_func_with_multiple_run(**kwargs):
        return eval_func_with_multiple_run(urban_canopy_and_path_sim_folder_tuple_list, fitness_func,
                                           path_json_results_file, num_workers, **kwargs)

    return wrapped_eval_func_with_multiple_run


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
