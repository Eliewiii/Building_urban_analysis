from mains_tool.utils_general import *

from step_methods.building_manipulation_function_for_main import SimulationBuildingManipulationFunctions
from step_methods.general_function_for_main import SimulationCommonMethods
from step_methods.load_bat_file_arguments import LoadArguments
from step_methods.load_building_or_geometry import SimulationLoadBuildingOrGeometry
from step_methods.post_processing_and_plots import SimulationPostProcessingAndPlots
from step_methods.run_simulations import SolarOrPanelSimulation

# Create urban_canopy
urban_canopy_object = SimulationCommonMethods.create_or_load_urban_canopy_object(
    path_folder_simulation=default_path_folder_simulation)

#add GIS
SimulationLoadBuildingOrGeometry.add_2D_GIS_to_urban_canopy(urban_canopy=urban_canopy_object,
                                                            path_gis=default_path_gis,
                                                            path_additional_gis_attribute_key_dict=
                                                            None,
                                                            unit=default_unit_gis)


# Move building to origin
SimulationBuildingManipulationFunctions.move_buildings_to_origin(urban_canopy_object=urban_canopy_object)

# Load Buildings from json
path_folder_json = None
path_file_json = None
path_folder_json = "C:\\Users\\elie-medioni\\OneDrive\\OneDrive - Technion\\BUA\\Elie\\Samples\\hb_model"
# path_file_json = "C:\Users\elie-medioni\OneDrive\OneDrive - Technion\BUA\Hilany\Samples\model_with_shades_small_win_corr.hbjson"

SimulationLoadBuildingOrGeometry.add_buildings_from_hbjson_to_urban_canopy(urban_canopy_object=urban_canopy_object,
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
