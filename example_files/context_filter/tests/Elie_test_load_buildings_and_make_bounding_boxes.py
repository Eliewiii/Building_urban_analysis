from bua.utils.utils_import_simulation_steps_and_config_var import *


# Inputs
path_gis = r"C:\Users\eliem\OneDrive - Technion\BUA\Context_filter\Sample GIS\sample_gis_context_filter_1"
path_hbjson_file = r"C:\Users\eliem\OneDrive - Technion\BUA\Samples\Elie\hb_model\complex_hb_model.hbjson"




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
                                                            unit="m")
# Move building to origin
SimulationBuildingManipulationFunctions.move_buildings_to_origin(urban_canopy_object=urban_canopy_object)
# Load Buildings from json
SimulationLoadBuildingOrGeometry.add_buildings_from_hbjson_to_urban_canopy(
    urban_canopy_object=urban_canopy_object,
    path_folder_hbjson=None,
    path_file_hbjson=path_hbjson_file,
    are_buildings_targets=True)

# Make bounding boxes
SimulationBuildingManipulationFunctions.make_oriented_bounding_boxes_of_buildings_in_urban_canopy(
    urban_canopy_object=urban_canopy_object, overwrite=True)

# Export urban_canopy to pickle
SimulationCommonMethods.save_urban_canopy_object_to_pickle(urban_canopy_object=urban_canopy_object,
                                                           path_simulation_folder=default_path_simulation_folder)
# Export urban_canopy to json
SimulationCommonMethods.save_urban_canopy_to_json(urban_canopy_object=urban_canopy_object,
                                                  path_simulation_folder=default_path_simulation_folder)

