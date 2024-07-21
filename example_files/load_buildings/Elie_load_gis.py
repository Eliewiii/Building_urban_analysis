from bua.utils.utils_import_simulation_steps_and_config_var import *

path_gis = r"C:\Users\elie-medioni\AppData\Local\Building_urban_analysis\Scripts\test\test_files\test_gis"



# Clear simulation temp folder
SimulationCommonMethods.clear_simulation_temp_folder()

# Create simulation folder
SimulationCommonMethods.make_simulation_folder()
# Create urban_canopy
urban_canopy_object = SimulationCommonMethods.create_or_load_urban_canopy_object(
    path_simulation_folder=default_path_simulation_folder)

# add GIS
SimulationLoadBuildingOrGeometry.add_2D_GIS_to_urban_canopy(urban_canopy=urban_canopy_object,
                                                            path_gis=path_gis,
                                                            path_additional_gis_attribute_key_dict=
                                                            None,
                                                            unit="deg")

# Move building to origin
SimulationBuildingManipulationFunctions.move_buildings_to_origin(urban_canopy_object=urban_canopy_object)



# Export urban_canopy to pickle
SimulationCommonMethods.save_urban_canopy_object_to_pickle(urban_canopy_object=urban_canopy_object,
                                                           path_simulation_folder=default_path_simulation_folder)
# Export urban_canopy to json
SimulationCommonMethods.save_urban_canopy_to_json(urban_canopy_object=urban_canopy_object,
                                                  path_simulation_folder=default_path_simulation_folder)
