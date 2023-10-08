from unit_tests.utils_main_import_scripts import *

# Clear simulation temp folder
SimulationCommonMethods.clear_simulation_temp_folder()
# Create simulation folder
SimulationCommonMethods.make_simulation_folder()
# Create urban_canopy
urban_canopy_object = SimulationCommonMethods.create_or_load_urban_canopy_object(
    path_simulation_folder=default_path_simulation_folder)

# path_folder_json = None
path_file_json = r"C:\Users\eliem\OneDrive - Technion\Ministry of Energy Research\IBPSA US conference\buildings_hbjson\variation_1\merged\ResidentialBldg_1_merged.hbjson"

from honeybee.model import Model

model = Model.from_hbjson(path_file_json)

path_folder_json=None
# path_folder_json = r"C:\Users\eliem\OneDrive - Technion\Ministry of Energy Research\IBPSA US conference\hbjson_2\var_sub_optimal\merged_or"

SimulationLoadBuildingOrGeometry.add_buildings_from_hbjson_to_urban_canopy(
    urban_canopy_object=urban_canopy_object,
    path_folder_hbjson=path_folder_json,
    path_file_hbjson=path_file_json,
    are_buildings_targets=True,
    keep_context_from_hbjson=True)

# Export urban_canopy to pickle
SimulationCommonMethods.save_urban_canopy_object_to_pickle(urban_canopy_object=urban_canopy_object,
                                                           path_simulation_folder=default_path_simulation_folder)
# Export urban_canopy to json
SimulationCommonMethods.save_urban_canopy_to_json(urban_canopy_object=urban_canopy_object,
                                                  path_simulation_folder=default_path_simulation_folder)

