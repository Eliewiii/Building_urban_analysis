from unit_tests.utils_main_import_scripts import *

# Create urban_canopy
urban_canopy_object = SimulationCommonMethods.create_or_load_urban_canopy_object(
    path_simulation_folder=default_path_simulation_folder)


# Run radiation simulation on the Urban Canopy
SolarOrPanelSimulation.solar_radiation_simulation(urban_canopy_object=urban_canopy_object,
                                                  path_simulation_folder=default_path_simulation_folder,
                                                  path_weather_file=default_path_weather_file,
                                                  list_id=None,
                                                  grid_size=1.5,
                                                  offset_dist=default_offset_dist,
                                                  on_roof=default_on_roof,
                                                  on_facades=default_on_facades)

# Export urban_canopy to pickle
SimulationCommonMethods.save_urban_canopy_object_to_pickle(urban_canopy_object=urban_canopy_object,
                                                           path_simulation_folder=default_path_simulation_folder)
# Export urban_canopy to json
SimulationCommonMethods.save_urban_canopy_to_json(urban_canopy_object=urban_canopy_object,
                                                  path_simulation_folder=default_path_simulation_folder)
