"""

"""

import os

from utils.utils_configuration import path_tool, path_simulation_temp_folder, path_libraries_tool_folder

# Default path to the simulation folder
default_path_folder_simulation = path_simulation_temp_folder

# Ladybug, Honeybee and Dragonfly
lb_hb_df_tolerance_value = 0.01

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

# Default values for the simulations - Context filter
default_mvfc_context_shading_selection = 0.01
default_mvfc_context_lwr_selection = 0.001
default_shading_number_of_rays_context_filter_second_pass = 3

# Default values for the simulations - Solar radiation calculation
default_name_radiation_simulation_folder = 'Radiation Simulation'
default_grid_size = 1.5  # todo check it !
default_offset_dist = 0.1
default_on_roof = True
default_on_facades = True

# Default values for panel simulation

default_path_pv_tech_dictionary = os.path.join(path_tool, "Libraries", "Solar_panels", "pv_technologies.json")  # todo @Elie to delete
default_id_pv_tech_roof = "mitrex_roof c-Si"
default_id_pv_tech_facades = "metsolar_facades c-Si"
default_minimum_ratio_energy_harvested_on_primary_energy = 1.2
default_performance_ratio = 0.75
default_study_duration_years = 50
default_replacement_scenario = "yearly"
default_evey_X_years = 5
default_country_ghe_cost = 0.57874
