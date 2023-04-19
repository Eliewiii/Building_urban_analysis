"""

"""
from utils_main_imports_packages import *

# Get Appdata\local folder
local_appdata = os.environ['LOCALAPPDATA']
path_tool = os.path.join(local_appdata, "Building_urban_analysis")
# Path of the different folders in the tool
path_scripts_tool = os.path.join(path_tool, "Scripts")
path_libraries_tool = os.path.join(path_tool, "Libraries")

# Default values for the simulations - General
default_path_folder_simulation = os.path.join(path_tool, "Simulation_temp")
default_move_buildings_to_origin = False
default_make_hb_model_envelops = False
name_urban_canopy_envelop_hbjson = "urban_canopy_envelop.hbjson"  # todo @Elie: change the name in the rest of the code and GH

# Default values for the simulations - GIS
default_path_gis = os.path.join(path_libraries_tool, "GIS", "gis_typo_id_extra_small")
default_building_id_key_gis = "idbinyan"
default_additional_gis_attribute_key_dict = None
default_unit_gis = "m"
default_move_buildings_to_origin = False

# Default values for the simulations - Building manipulation
default_is_target_building = True
default_is_simulated_building = True  # target building is always simulated


# Default values for the simulations - Building bounding boxes
name_bounding_box_file_hbjson = "bounding_boxes.hbjson"

# Default values for the simulations - Context filter
# todo @Elie: add when coded
# Default values for the simulations - Solar radiation calculation
# todo @Elie: add when coded
# Default values for the simulations - LCA
# todo @Elie: add when coded
# Default values for the simulations - LCA end of life
# todo @Elie: add when coded
# Default values for the simulations - building energy simulation
# todo @Elie: add when coded
