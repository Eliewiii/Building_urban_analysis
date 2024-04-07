from unit_tests.utils_main_import_scripts import *

path_gis = r"C:\Users\elie-medioni\OneDrive\OneDrive - Technion\BUA\Context_filter\Samples\Sample GIS\sample_gis_context_filter_1"

# Elie Technion
# path_hbjson_file_1 = r"C:\Users\elie-medioni\OneDrive\OneDrive - Technion\Ministry of Energy Research\Papers\IBPSA US conference\Full paper\Simulation\TA_Neighborhood_27.9.2023\HBJSON_Models\Low_Density_Context\Buil_TA_1.hbjson"
# path_hbjson_file_2 = r"C:\Users\elie-medioni\OneDrive\OneDrive - Technion\Ministry of Energy Research\Papers\IBPSA US conference\Full paper\Simulation\TA_Neighborhood_27.9.2023\HBJSON_Models\Low_Density_Context\Buil_TA_2.hbjson"

# # Elie Home
path_hbjson_file_1 = r"D:\OneDrive - Technion\Ministry of Energy Research\Papers\IBPSA US conference\Full paper\Simulation\TA_Neighborhood_27.9.2023\HBJSON_Models\Low_Density_Context\Buil_TA_1.hbjson"
path_hbjson_file_2 = r"D:\OneDrive - Technion\Ministry of Energy Research\Papers\IBPSA US conference\Full paper\Simulation\TA_Neighborhood_27.9.2023\HBJSON_Models\Low_Density_Context\Buil_TA_2.hbjson"


# Clear simulation temp folder
SimulationCommonMethods.clear_simulation_temp_folder()

# Create simulation folder
SimulationCommonMethods.make_simulation_folder()
# Create urban_canopy
urban_canopy_object = SimulationCommonMethods.create_or_load_urban_canopy_object(
    path_simulation_folder=default_path_simulation_folder)

# # add GIS
# SimulationLoadBuildingOrGeometry.add_2D_GIS_to_urban_canopy(urban_canopy=urban_canopy_object,
#                                                             path_gis=default_path_gis,
#                                                             path_additional_gis_attribute_key_dict=
#                                                             None,
#                                                             unit="m")
#
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


# Export urban_canopy to pickle
SimulationCommonMethods.save_urban_canopy_object_to_pickle(urban_canopy_object=urban_canopy_object,
                                                           path_simulation_folder=default_path_simulation_folder)
# Export urban_canopy to json
SimulationCommonMethods.save_urban_canopy_to_json(urban_canopy_object=urban_canopy_object,
                                                  path_simulation_folder=default_path_simulation_folder)
