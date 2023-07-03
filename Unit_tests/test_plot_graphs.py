from mains_tool.utils_general import *
from mains_tool.utils_main_import_scripts import *

# Load urban_canopy
urban_canopy_object = SimulationCommonMethods.create_or_load_urban_canopy_object(path_folder_simulation=
                                                                                 default_path_folder_simulation)

# Export urban_canopy to pickle
SimulationCommonMethods.save_urban_canopy_object_to_pickle(urban_canopy_object=urban_canopy_object,
                                                           path_folder_simulation=default_path_folder_simulation)
# Export urban_canopy to json
SimulationCommonMethods.save_urban_canopy_to_json(urban_canopy_object=urban_canopy_object,
                                                  path_folder_simulation=default_path_folder_simulation)

# Generate csv panels data
SimulationPostProcessingAndPlots.plot_graphs(urban_canopy_object=urban_canopy_object,
                                             path_folder_simulation=default_path_folder_simulation,
                                             study_duration_years=default_study_duration_years,
                                             country_ghe_cost=default_country_ghe_cost)
