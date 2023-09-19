from unit_tests.utils_main_import_scripts import *

# Create urban_canopy
urban_canopy_object = SimulationCommonMethods.create_or_load_urban_canopy_object(
    path_simulation_folder=default_path_simulation_folder)

SimFunSolarRadAndBipv.run_bipv_harvesting_and_lca_simulation(
    urban_canopy_object=urban_canopy_object,
    efficiency_computation_method=default_efficiency_computation_method,
    minimum_panel_eroi=default_minimum_panel_eroi,
    start_year=2023,
    end_year=2025,
    continue_simulation=False,
    update_panel_technology=False,
    replacement_frequency_in_years=default_replacement_frequency_in_years)

# # Export urban_canopy to pickle
# SimulationCommonMethods.save_urban_canopy_object_to_pickle(urban_canopy_object=urban_canopy_object,
#                                                            path_simulation_folder=default_path_simulation_folder)
# # Export urban_canopy to json
# SimulationCommonMethods.save_urban_canopy_to_json(urban_canopy_object=urban_canopy_object,
#                                                   path_simulation_folder=default_path_simulation_folder)
