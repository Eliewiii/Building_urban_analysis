import sys

from bua.urban_canopy.urban_canopy import UrbanCanopy

from unit_tests.utils_main_import_scripts import *

from Optimization.Nevergrad.optimization_test_with_BUA.json_result_dict_methods import \
    update_json_results_dict
from Optimization.Nevergrad.optimization_test_with_BUA.design_variable_definition_and_boundaries import \
    ROOF_PANEL_TECHNOLOGIES_DICT, FACADES_PANEL_TECHNOLOGIES_DICT, REPLACEMENT_FREQUENCY_MULTIPLIER


def eval_func(urban_canopy_object: UrbanCanopy, fitness_func, path_json_results_file: str,
              roof_panel_id: int, facades_panel_id: int, roof_inverter_sizing_ratio: float,
              facades_inverter_sizing_ratio: float, min_panel_eroi: float, replacement_frequency: int):
    """
    Function to compute the fitness value for the optimization.
    :param urban_canopy_object: UrbanCanopy object, urban canopy object to run the simulation
    :param fitness_func: function, fitness function to compute the fitness value
    :param path_json_results_file: str, path to the json file to update
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

    # Define bipv_scenario_identifier default
    bipv_scenario_identifier = "optimization_BUA"
    # run BIPV simulation
    SimFunSolarRadAndBipv.run_bipv_harvesting_and_lca_simulation(
        urban_canopy_object=urban_canopy_object,
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
    SimFunSolarRadAndBipv.run_kpi_simulation(urban_canopy_object=urban_canopy_object,
                                             bipv_scenario_identifier="replace_failed_panels_every_X_years",
                                             grid_ghg_intensity=default_grid_ghg_intensity,
                                             grid_energy_intensity=default_grid_energy_intensity,
                                             grid_electricity_sell_price=default_grid_electricity_sell_price,
                                             zone_area=None)

    # extract the KPI dict
    kpi_dict = urban_canopy_object.bipv_scenario_dict[
        bipv_scenario_identifier].urban_canopy_bipv_kpis_obj.to_dict()

    # Compute the fitness value
    fitness_value = fitness_func(kpi_dict)

    # Save the results in the json file
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
