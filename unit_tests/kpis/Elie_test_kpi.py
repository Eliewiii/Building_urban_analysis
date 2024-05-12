from unit_tests.utils_main_import_scripts import *

# Create simulation folder
SimulationCommonMethods.make_simulation_folder()
# Create urban_canopy
urban_canopy_object = SimulationCommonMethods.create_or_load_urban_canopy_object(
    path_simulation_folder=default_path_simulation_folder)

# Run KPI computation
SimFunSolarRadAndBipv.run_kpi_simulation(urban_canopy_object=urban_canopy_object,
                                         bipv_scenario_identifier="zob_2",
                                         grid_ghg_intensity=default_grid_ghg_intensity,
                                         grid_energy_intensity=default_grid_energy_intensity,
                                         grid_electricity_sell_price=default_grid_electricity_sell_price,
                                         zone_area=None)

# # Export urban_canopy to pickle
# SimulationCommonMethods.save_urban_canopy_object_to_pickle(urban_canopy_object=urban_canopy_object,
#                                                            path_simulation_folder=default_path_simulation_folder)
# # Export urban_canopy to json
# SimulationCommonMethods.save_urban_canopy_to_json(urban_canopy_object=urban_canopy_object,
#                                                   path_simulation_folder=default_path_simulation_folder)
#
# print("End of the script")
