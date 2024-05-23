"""

"""

import os
from datetime import datetime

from utils.utils_configuration import path_tool, path_simulation_temp_folder, path_libraries_tool_folder

# Default path to the simulation folder
default_path_simulation_folder = path_simulation_temp_folder

# Default GIS
default_move_buildings_to_origin = False

default_path_gis = os.path.join(path_libraries_tool_folder, "Samples","gis", "gis_example")
default_building_id_key_gis = "idbinyan"
default_unit_gis = "m"

# Default hbjson
default_path_hbjson = os.path.join(path_libraries_tool_folder, "Samples","hb_models", "sample_building.hbjson")

# EPW weather file
default_path_weather_file = os.path.join(path_tool, "Libraries", "EPW", "IS_5280_A_Haifa.epw")

# Building Energy Simulation
default_path_hbjson_simulation_parameter_file = os.path.join(path_libraries_tool_folder, "Simulation_parameters",
                                                        "default_hb_sim_paramters.json")  # todo: check the link and update the file
default_cop_heating = 3.0
default_cop_cooling = 3.0

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

default_on_roof = False
default_on_facades = False

# Default value mesh generation
default_roof_grid_size_x = 1.5
default_facades_grid_size_x = 1.5
default_roof_grid_size_y = 1.5
default_facades_grid_size_y = 1.5
default_offset_dist = 0.1

# Default values for panel simulation
default_id_pv_tech_roof = "mitrex_roof c-Si M390-A1F default"
default_id_pv_tech_facades = "mitrex_facades c-Si Solar Siding 350W - Dove Grey china"
default_roof_transport_id = "China-Israel"
default_facades_transport_id = "China-Israel"
default_roof_inverter_id = "inverter_default"
default_facades_inverter_id = "inverter_default"
default_roof_inverter_sizing_ratio = 0.9
default_facades_inverter_sizing_ratio = 0.9
default_minimum_panel_eroi = 1.2
default_start_year = datetime.now().year
default_end_year = default_start_year + 50
default_efficiency_computation_method = "yearly"
default_replacement_scenario = "replace_failed_panels_every_X_years"
default_replacement_frequency_in_years = 20
default_bipv_scenario_identifier = "new_uc_scenario"

# Default values for panel simulation - LCA
default_country_ghe_cost = 0.57874  # todo: value used on old files


# Default values for KPI computation, values for 2023, taken from Zenebu's excel sheet
default_grid_ghg_intensity = 0.660  # kgCO2/kWh
default_grid_energy_intensity = 2.84      # kWh/kWh
default_grid_electricity_sell_price = 0.14  # $/kWh



