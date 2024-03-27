from unit_tests.utils_main_import_scripts import *

# Create simulation folder
SimulationCommonMethods.make_simulation_folder()
# Create urban_canopy
urban_canopy_object = SimulationCommonMethods.create_or_load_urban_canopy_object(
    path_simulation_folder=default_path_simulation_folder)

# Merge the face of the buildings to reduce the number of faces and the
SimulationBuildingManipulationFunctions.make_merged_face_of_buildings_in_urban_canopy(urban_canopy_object=urban_canopy_object)
#
SimFunSolarRadAndBipv.generate_sensor_grid(urban_canopy_object=urban_canopy_object)
#

# Export urban_canopy to pickle
SimulationCommonMethods.save_urban_canopy_object_to_pickle(urban_canopy_object=urban_canopy_object,
                                                           path_simulation_folder=default_path_simulation_folder)
# Export urban_canopy to json
SimulationCommonMethods.save_urban_canopy_to_json(urban_canopy_object=urban_canopy_object,
                                                  path_simulation_folder=default_path_simulation_folder)

