from unit_tests.utils_main_import_scripts import *

# Create urban_canopy
urban_canopy_object = SimulationCommonMethods.create_or_load_urban_canopy_object(
    path_folder_simulation=default_path_folder_simulation)


# Run radiation simulation on the Urban Canopy
SolarOrPanelSimulation.solar_radiation_simulation(urban_canopy_object=urban_canopy_object,
                                                  path_folder_simulation=default_path_folder_simulation,
                                                  path_weather_file=default_path_weather_file,
                                                  list_id=None,
                                                  grid_size=1.4,
                                                  offset_dist=default_offset_dist,
                                                  on_roof=default_on_roof,
                                                  on_facades=default_on_facades)

# Export urban_canopy to pickle
SimulationCommonMethods.save_urban_canopy_object_to_pickle(urban_canopy_object=urban_canopy_object,
                                                           path_folder_simulation=default_path_folder_simulation)
# Export urban_canopy to json
SimulationCommonMethods.save_urban_canopy_to_json(urban_canopy_object=urban_canopy_object,
                                                  path_folder_simulation=default_path_folder_simulation)
