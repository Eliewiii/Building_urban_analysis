from mains_tool.utils_general import *
from mains_tool.utils_main_import_scripts import *

# Load urban_canopy
urban_canopy_object = SimulationCommonMethods.create_or_load_urban_canopy_object(path_folder_simulation=
                                                                                 default_path_folder_simulation)

# Run radiation simulation on the Urban Canopy
SolarOrPanelSimulation.panel_simulation(urban_canopy_object=urban_canopy_object,
                                        path_folder_simulation=default_path_folder_simulation,
                                        path_pv_tech_dictionary_json=default_path_pv_tech_dictionary,
                                        id_pv_tech_roof=default_id_pv_tech_roof,
                                        id_pv_tech_facades=default_id_pv_tech_facades,
                                        minimum_ratio_energy_produced_on_used=
                                        default_minimum_ratio_energy_produced_on_used,
                                        performance_ratio=default_performance_ratio,
                                        study_duration_in_years=default_study_duration_years,
                                        replacement_scenario=default_replacement_scenario)
#                                         replacement_scenario="every_X_years",
#                                         replacement_year=5)

# Export urban_canopy to pickle
SimulationCommonMethods.save_urban_canopy_object_to_pickle(urban_canopy_object=urban_canopy_object,
                                                           path_folder_simulation=default_path_folder_simulation)
# Export urban_canopy to json
SimulationCommonMethods.save_urban_canopy_to_json(urban_canopy_object=urban_canopy_object,
                                                  path_folder_simulation=default_path_folder_simulation)
