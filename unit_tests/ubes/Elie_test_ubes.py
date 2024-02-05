from unit_tests.utils_main_import_scripts import *

# Inputs
path_gis = r"C:\Users\elie-medioni\OneDrive\OneDrive - Technion\BUA\Context_filter\Samples\Sample GIS\sample_gis_context_filter_1"
path_hbjson_file_1 = r"C:\Users\elie-medioni\OneDrive\OneDrive - Technion\BUA\Context_filter\Samples\Sample hbjsons\example_1.hbjson"
path_hbjson_file_2 = r"C:\Users\elie-medioni\OneDrive\OneDrive - Technion\BUA\Context_filter\Samples\Sample hbjsons\example_2.hbjson"

# Clear simulation temp folder
SimulationCommonMethods.clear_simulation_temp_folder()
# Create simulation folder
SimulationCommonMethods.make_simulation_folder()
# Create urban_canopy
urban_canopy_object = SimulationCommonMethods.create_or_load_urban_canopy_object(
    path_simulation_folder=default_path_simulation_folder)

# # add GIS
# SimulationLoadBuildingOrGeometry.add_2D_GIS_to_urban_canopy(urban_canopy=urban_canopy_object,
#                                                             path_gis=path_gis,
#                                                             path_additional_gis_attribute_key_dict=
#                                                             None,
#                                                             unit="m")
# # Move building to origin
# SimulationBuildingManipulationFunctions.move_buildings_to_origin(urban_canopy_object=urban_canopy_object)

# Load Buildings from json
SimulationLoadBuildingOrGeometry.add_buildings_from_hbjson_to_urban_canopy(
    urban_canopy_object=urban_canopy_object,
    path_folder_hbjson=None,
    path_file_hbjson=path_hbjson_file_1,
    are_buildings_targets=True)
SimulationLoadBuildingOrGeometry.add_buildings_from_hbjson_to_urban_canopy(
    urban_canopy_object=urban_canopy_object,
    path_folder_hbjson=None,
    path_file_hbjson=path_hbjson_file_2,
    are_buildings_targets=True)

# Load epw and simulation parameters
UrbanBuildingEnergySimulationFunctions.load_epw_and_hb_simulation_parameters_for_ubes_in_urban_canopy(
    urban_canopy_obj=urban_canopy_object,
    # path_simulation_folder=default_path_simulation_folder,
    # path_hbjson_simulation_parameter_file=default_path_hbjson_simulation_parameter_file,
    # path_file_epw=default_path_weather_file,
    # ddy_file=None,
    overwrite=True)

# Write IDF
UrbanBuildingEnergySimulationFunctions.generate_idf_files_for_ubes_with_openstudio_in_urban_canopy(
    urban_canopy_obj=urban_canopy_object,
    path_simulation_folder=default_path_simulation_folder,
    overwrite=False,
    silent=True)

# Run IDF through EnergyPlus
UrbanBuildingEnergySimulationFunctions.run_idf_files_with_energyplus_for_ubes_in_urban_canopy(
    urban_canopy_obj=urban_canopy_object,
    path_simulation_folder=default_path_simulation_folder,
    overwrite=False,
    silent=True)





# # Export urban_canopy to pickle
# SimulationCommonMethods.save_urban_canopy_object_to_pickle(urban_canopy_object=urban_canopy_object,
#                                                            path_simulation_folder=default_path_simulation_folder)
# # Export urban_canopy to json
# SimulationCommonMethods.save_urban_canopy_to_json(urban_canopy_object=urban_canopy_object,
#                                                   path_simulation_folder=default_path_simulation_folder)
