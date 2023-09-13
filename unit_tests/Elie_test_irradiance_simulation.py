from unit_tests.utils_main_import_scripts import *

# Clear simulation temp folder
SimulationCommonMethods.clear_simulation_temp_folder()
# Create simulation folder
SimulationCommonMethods.make_simulation_folder()
# Create urban_canopy
urban_canopy_object = SimulationCommonMethods.create_or_load_urban_canopy_object(
    path_simulation_folder=default_path_simulation_folder)


# add GIS
SimulationLoadBuildingOrGeometry.add_2D_GIS_to_urban_canopy(urban_canopy=urban_canopy_object,
                                                            path_gis=default_path_gis,
                                                            path_additional_gis_attribute_key_dict=
                                                            None,
                                                            unit="m")

# Move building to origin
SimulationBuildingManipulationFunctions.move_buildings_to_origin(urban_canopy_object=urban_canopy_object)


# Load Buildings from json

# path_folder_json = None
path_file_json = r"C:\Users\elie-medioni\OneDrive\OneDrive - Technion\Ministry of Energy Research\IBPSA US conference\hbjson_2\var_optimal\Buil_TA_0.hbjson"

path_folder_json=None
# path_folder_json = r"C:\Users\eliem\OneDrive - Technion\Ministry of Energy Research\IBPSA US conference\hbjson_2\var_sub_optimal\merged_or"

SimulationLoadBuildingOrGeometry.add_buildings_from_hbjson_to_urban_canopy(
    urban_canopy_object=urban_canopy_object,
    path_folder_hbjson=path_folder_json,
    path_file_hbjson=path_file_json,
    are_buildings_targets=True)

# Merge facades
SimulationBuildingManipulationFunctions.make_merged_face_of_buildings_in_urban_canopy(urban_canopy_object=urban_canopy_object)

# Generate sensor grid
SimFunSolarRadAndBipv.generate_sensor_grid(urban_canopy_object=urban_canopy_object)

# Run annual solar irradiance simulation
SimFunSolarRadAndBipv.run_annual_solar_irradiance_simulation(urban_canopy_object=urban_canopy_object)

# Export urban_canopy to pickle
SimulationCommonMethods.save_urban_canopy_object_to_pickle(urban_canopy_object=urban_canopy_object,
                                                           path_simulation_folder=default_path_simulation_folder)
# Export urban_canopy to json
SimulationCommonMethods.save_urban_canopy_to_json(urban_canopy_object=urban_canopy_object,
                                                  path_simulation_folder=default_path_simulation_folder)

