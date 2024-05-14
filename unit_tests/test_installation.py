from unit_tests.utils_main_import_scripts import *

# Clear simulation temp folder
SimulationCommonMethods.clear_simulation_temp_folder()

# Create simulation folder
SimulationCommonMethods.make_simulation_folder()
# Create urban_canopy
urban_canopy_object = SimulationCommonMethods.create_or_load_urban_canopy_object(
    path_simulation_folder=default_path_simulation_folder)

# # add GIS
SimulationLoadBuildingOrGeometry.add_2D_GIS_to_urban_canopy(urban_canopy=urban_canopy_object,
                                                            path_gis=default_path_gis,
                                                            unit="m")

# Move building to origin
SimulationBuildingManipulationFunctions.move_buildings_to_origin(urban_canopy_object=urban_canopy_object)

# Load Buildings from json
SimulationLoadBuildingOrGeometry.add_buildings_from_hbjson_to_urban_canopy(
    urban_canopy_object=urban_canopy_object,
    path_folder_hbjson=None,
    path_file_hbjson=default_path_hbjson,
    are_buildings_targets=True)


# Export urban_canopy to pickle
SimulationCommonMethods.save_urban_canopy_object_to_pickle(urban_canopy_object=urban_canopy_object,
                                                           path_simulation_folder=default_path_simulation_folder)
# Export urban_canopy to json
SimulationCommonMethods.save_urban_canopy_to_json(urban_canopy_object=urban_canopy_object,
                                                  path_simulation_folder=default_path_simulation_folder)
print("Sample simulation succeeded")

# Clear simulation temp folder
SimulationCommonMethods.clear_simulation_temp_folder()