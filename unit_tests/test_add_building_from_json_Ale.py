import logging
from unit_tests.utils_main_import_scripts import *

# dev_logger = logging.getLogger()
# user_logger = logging.getLogger()
dev_logger = logging.getLogger("dev")
user_logger = logging.getLogger("user")
user_logger.setLevel(logging.INFO)
dev_logger.setLevel(logging.INFO)
dev_handler = logging.FileHandler('dev_log.log', mode='w')
user_formatter = logging.Formatter('%(message)s')
dev_formatter = logging.Formatter(
    '%(name)s: %(asctime)s - %(levelname)s - %(filename)s (function: %(funcName)s, line: %(lineno)d) - %(message)s')
dev_handler.setFormatter(dev_formatter)
dev_logger.addHandler(dev_handler)

# Make folder
SimulationCommonMethods.make_simulation_folder(default_path_folder_simulation)

user_handler = logging.FileHandler(
    os.path.join(default_path_folder_simulation, name_gh_components_logs_folder, "zob.log"), mode='w')
user_handler.setFormatter(user_formatter)
user_logger.addHandler(user_handler)

# Create urban_canopy
urban_canopy_object = SimulationCommonMethods.create_or_load_urban_canopy_object(
    path_folder_simulation=default_path_folder_simulation)

# Load Buildings from json
path_folder_json = None
path_file_json = None
path_folder_json = "C:\\Users\\elie-medioni\\OneDrive\\OneDrive - Technion\\BUA\\Elie\\Samples\\hb_model"

# path_file_json = "C:\Users\elie-medioni\OneDrive\OneDrive - Technion\BUA\Hilany\Samples\model_with_shades_small_win_corr.hbjson"
# path_file_json = "C:\\Users\\alejandro.s\\Technion\\Elie Medioni - BUA\\Samples\\Elie\\hb_model\\complex_hb_model.hbjson"
# path_file_json = "C:\\Users\\alejandro.s\\Documents\\sample_simple_hb_model.hbjson"

SimulationLoadBuildingOrGeometry.add_buildings_from_hbjson_to_urban_canopy(
    urban_canopy_object=urban_canopy_object,
    path_folder_hbjson=path_folder_json,
    path_file_hbjson=path_file_json,
    are_buildings_targets=True)
# Move building to origin
SimulationBuildingManipulationFunctions.move_buildings_to_origin(urban_canopy_object=urban_canopy_object)

# make envelop
SimulationPostProcessingAndPlots.generate_hb_model_contains_all_building_envelopes_to_plot_Grasshopper(
    urban_canopy_object=urban_canopy_object,
    path_folder_simulation=default_path_folder_simulation)

# Export urban_canopy to pickle
SimulationCommonMethods.save_urban_canopy_object_to_pickle(urban_canopy_object=urban_canopy_object,
                                                           path_folder_simulation=default_path_folder_simulation)
