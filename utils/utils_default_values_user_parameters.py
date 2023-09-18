"""

"""

import os
from datetime import datetime

from utils.utils_configuration import path_tool, path_simulation_temp_folder, path_libraries_tool_folder

# Default path to the simulation folder
default_path_simulation_folder = path_simulation_temp_folder

# ???
default_move_buildings_to_origin = False
default_make_hb_model_envelops = False

# GIS
default_path_gis = os.path.join(path_libraries_tool_folder, "GIS", "gis_typo_id_extra_small")
default_building_id_key_gis = "idbinyan"
default_gis_attribute_key_dict = {
    "building_id_key_gis": "none",
    "name": ["name", "full_name_"],
    "age": ["age", "date", "year"],
    "typology": ["typo", "typology", "type", "Typology"],
    "elevation": ["minheight"],
    "height": ["height", "Height", "govasimple"],
    "number of floor": ["number_floor", "nb_floor", "mskomot"],
    "group": ["group"]
}
default_unit_gis = "m"

# EPW weather file
default_path_weather_file = os.path.join(path_tool, "Libraries", "EPW", "IS_5280_A_Haifa.epw")

# Creation of BuildingModeled objects
default_automatic_floor_subdivision_for_new_BuildingModeled = False
default_use_layout_from_typology_for_new_BuildingModeled = False
default_use_properties_from_typology_for_new_BuildingModeled = False
default_make_new_BuildingModeled_simulated = False

# Default values for the simulations - Context filter
default_mvfc_context_shading_selection = 0.01
default_mvfc_context_lwr_selection = 0.001
default_shading_number_of_rays_context_filter_second_pass = 3
default_perform_context_filtering_on_building_to_simulate = True

# Default values for the simulations - Solar radiation calculation
default_name_radiation_simulation_folder = 'Radiation Simulation'
default_grid_size = 1.5  # todo check it !
default_offset_dist = 0.1
default_on_roof = True
default_on_facades = True

# Default value mesh generation
default_roof_grid_size_x = 1.5
default_facades_grid_size_x = 1.5
default_roof_grid_size_y = 1.5
default_facades_grid_size_y = 1.5
default_offset_dist = 0.1

# Default values for panel simulation
default_path_pv_tech_dictionary_folder = os.path.join(path_tool, "Libraries", "Solar_panels")
default_id_pv_tech_roof = "mitrex_roof c-Si"
default_id_pv_tech_facades = "mitrex_facades c-Si"
default_minimum_panel_eroi = 1.2
default_start_year = datetime.now().year
default_end_year = default_start_year + 50
default_efficiency_computation_method = "yearly"
default_replacement_scenario = "replace_failed_panels_every_X_years"
default_replacement_frequency_in_years = 20
default_bipv_scenario_identifier = "new_uc_scenario"
# Default values for panel simulation - LCA
default_country_ghe_cost = 0.57874
