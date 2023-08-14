from unit_tests.utils_main_import_scripts import *

# Create urban_canopy
# urban_canopy_object = SimulationCommonMethods.create_or_load_urban_canopy_object(
#    path_simulation_folder=default_path_simulation_folder)


# Load Buildings from json
path_folder_json = None
path_file_json = None
# path_file_json = "C:\\Users\\User\\OneDrive - Technion\\BUA\\Elie\\Samples\\hb_model\\sample_simple_hb_model.hbjson"
# path_folder_json = "C:\\Users\\User\\OneDrive - Technion\\BUA\\Elie\\Samples\\hb_model"
# path_file_json = "C:\\Users\\User\\OneDrive - Technion\\BUA\\Hilany\\Samples\\model_with_shades_small_win_corr.hbjson"
# path_file_json = "C:\\Users\\elie-medioni\\OneDrive\\OneDrive - Technion\\BUA\\Hilany\\Samples\\model_with_shades_small_win_corr.hbjson"
# path_file_json = "C:\\Users\\elie-medioni\\OneDrive\\OneDrive - Technion\\BUA\\Hilany\\Samples\\model_with_shades_small_win.hbjson"

# path_folder_json = "C:\\Users\\User\\OneDrive - Technion\BUA\\Hilany\\Samples"
# urban_canopy_object = SimulationCommonMethods.create_or_load_urban_canopy_object(
#    path_simulation_folder=path_folder_json)

urban_canopy_object = SimulationCommonMethods.create_or_load_urban_canopy_object(
    path_simulation_folder=default_path_simulation_folder)

#path_folder_json = "C:\\Users\\elie-medioni\\OneDrive\\OneDrive - Technion\\BUA\\Hilany\\Samples\\mesh_issue"
#SimulationLoadBuildingOrGeometry.add_buildings_from_hbjson_to_urban_canopy(urban_canopy_object=urban_canopy_object,
#                                                                           path_file_hbjson=path_file_json,
#                                                                           path_folder_hbjson=path_folder_json,
#                                                                          are_buildings_targets=True)


# Run radiation simulation on the Urban Canopy
SolarOrPanelSimulation.solar_radiation_simulation(urban_canopy_object=urban_canopy_object,
                                                  path_simulation_folder=default_path_simulation_folder,
                                                  path_weather_file=default_path_weather_file,
                                                  list_id=None,
                                                  grid_size=0.8,
                                                  offset_dist=default_offset_dist,
                                                  on_roof=default_on_roof,
                                                  on_facades=default_on_facades)

# Export urban_canopy to pickle
SimulationCommonMethods.save_urban_canopy_object_to_pickle(urban_canopy_object=urban_canopy_object,
                                                           path_simulation_folder=default_path_simulation_folder)
# Export urban_canopy to json
SimulationCommonMethods.save_urban_canopy_to_json(urban_canopy_object=urban_canopy_object,
                                                  path_simulation_folder=default_path_simulation_folder)
