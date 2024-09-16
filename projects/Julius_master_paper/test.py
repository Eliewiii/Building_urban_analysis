"""
Script for the context selection paper UBES simulation.
"""
import json
import logging

from bua.utils.utils_import_simulation_steps_and_config_var import *

from bua.building.building_modeled import BuildingModeled

# Initialize logger
dev_logger = logging.getLogger("dev")
dev_logger.setLevel(logging.WARNING)
dev_handler = logging.FileHandler('dev_log.log', mode='w')
dev_formatter = logging.Formatter(
    '% %(asctime)s - %(message)s')
dev_handler.setFormatter(dev_formatter)
dev_logger.addHandler(dev_handler)

# Initialize json result file
name_result_json_file = "results_context_filter.json"
path_result_folder = r"C:\Users\julius.jandl\OneDrive - Technion\Julius PhD\Paper\results"
path_json_result_file = os.path.join(path_result_folder, name_result_json_file)

# Buildings folder
path_buildings = r"C:\Users\julius.jandl\OneDrive - Technion\Elie_Julius\Paper_Julius\Geometry\hbjson_target_buildings"

# EPW file
path_epw = r"C:\Users\julius.jandl\AppData\Local\Building_urban_analysis\Libraries\EPW\IS_5280_A_Tel_Aviv.epw"

cop_heating = 3
cop_cooling = 3

# Definition of Scenarios
rooftech_baseline = "mitrex_roof c-Si M390-A1F"  # baseline csi id
envtech_baseline = "mitrex_facades c-Si Solar Siding 350W - Dove Grey china"  # baseline csi id
replacement_frequency_baseline = 10  # years

envtech_aesthetic = "mitrex_facades c-Si Solar Siding 216W - beige china"  # baseline beige csi id
rooftech_econ_opt = "mitrex_roof c-Si M390-A1F optimistic"  # csi roof optimistic
envtech_econ_opt = "mitrex_facades c-Si Solar Siding 350W - Dove Grey china optimistic"  # csi grey env optimistic
rooftech_econ_pess = "mitrex_roof c-Si M390-A1F pessimistic"  # csi roof pessimistic
envtech_econ_pess = "mitrex_facades c-Si Solar Siding 350W - Dove Grey china pessimistic"  # csi grey env pessimistic
rooftech_cdte = "cdte firstsolar FS-6445 roof"
envtech_cdte = "cdte firstsolar FS-6445 facade"
rooftech_cigs = "cigs eterbright CIGS-3650A1 roof"
envtech_cigs = "cigs eterbright CIGS-3650A1 facade"

scenarios_dict = {
    "baseline": {
        "rooftech": rooftech_baseline,
        "envtech": envtech_baseline,
        "replacement": replacement_frequency_baseline
    },
    "rep_5": {
        "rooftech": rooftech_baseline,
        "envtech": envtech_baseline,
        "replacement": 5
    },
    "rep_15": {
        "rooftech": rooftech_baseline,
        "envtech": envtech_baseline,
        "replacement": 15
    },
    "rep_20": {
        "rooftech": rooftech_baseline,
        "envtech": envtech_baseline,
        "replacement": 20
    },
    "rep_25": {
        "rooftech": rooftech_baseline,
        "envtech": envtech_baseline,
        "replacement": 25
    },
    "aesthetic": {
        "rooftech": rooftech_baseline,
        "envtech": envtech_aesthetic,
        "replacement": replacement_frequency_baseline
    },
    "econ_opt": {
        "rooftech": rooftech_econ_opt,
        "envtech": envtech_econ_opt,
        "replacement": replacement_frequency_baseline
    },
    "econ_pess": {
        "rooftech": rooftech_econ_pess,
        "envtech": envtech_econ_pess,
        "replacement": replacement_frequency_baseline
    }
}

scenarios_tech_dict = {
    "cdte": {
        "rooftech": rooftech_cdte,
        "envtech": envtech_cdte,
        "replacement": replacement_frequency_baseline
    },
    "cigs": {
        "rooftech": rooftech_cigs,
        "envtech": envtech_cigs,
        "replacement": replacement_frequency_baseline
    }
}
scenarios_list = list(scenarios_dict.keys())

# -------------------------------------------------------------------------------------------
# Init json results file
# -------------------------------------------------------------------------------------------
json_result_dict = {}
with open(path_json_result_file, 'w') as json_file:
    json.dump(json_result_dict, json_file)

# -------------------------------------------------------------------------------------------
# Preprocessing for all scenarios
# -------------------------------------------------------------------------------------------
# Clear simulation temp folder at when simulating for another building
SimulationCommonMethods.clear_simulation_temp_folder()
# Create simulation folder
SimulationCommonMethods.make_simulation_folder()
# Make an original urban canopy object that will be copied for each simulation
urban_canopy_object = SimulationCommonMethods.create_or_load_urban_canopy_object()
# Load context from json
SimulationLoadBuildingOrGeometry.add_buildings_from_lb_polyface3d_json_in_urban_canopy(
    urban_canopy_object=urban_canopy_object,
    path_lb_polyface3d_json_file=r"C:\Users\julius.jandl\OneDrive - Technion\Elie_Julius\Paper_Julius\Geometry\Ramat_gan_lb_pf3d_julius_paper.json")
# Make the merged face of the context buildings
SimulationBuildingManipulationFunctions.make_merged_face_of_buildings_in_urban_canopy(
    urban_canopy_object=urban_canopy_object, overwrite=True)
SimulationBuildingManipulationFunctions.make_oriented_bounding_boxes_of_buildings_in_urban_canopy(
    urban_canopy_object=urban_canopy_object, overwrite=True)

# Load epw and simulation parameters
UrbanBuildingEnergySimulationFunctions.load_epw_and_hb_simulation_parameters_for_ubes_in_urban_canopy(
    urban_canopy_obj=urban_canopy_object,
    path_weather_file=path_epw,
    overwrite=True)

# Load building from json
SimulationLoadBuildingOrGeometry.add_buildings_from_hbjson_to_urban_canopy(
    urban_canopy_object=urban_canopy_object,
    path_folder_hbjson=path_buildings,
    path_file_hbjson=None,
    are_buildings_targets=True,
    keep_context_from_hbjson=False)

# Make the merged face of the building (not too sure if necessary)
SimulationBuildingManipulationFunctions.make_merged_face_of_buildings_in_urban_canopy(
    urban_canopy_object=urban_canopy_object, overwrite=False)
# Make the oriented bounding boxes of the building (not too sure if necessary)
SimulationBuildingManipulationFunctions.make_oriented_bounding_boxes_of_buildings_in_urban_canopy(
    urban_canopy_object=urban_canopy_object, overwrite=False)

mvfc = 0.01
nb_of_rays = 3
consider_windows = True

# Perform the context filtering
SimulationContextFiltering.perform_first_pass_of_context_filtering_on_buildings(
    urban_canopy_object=urban_canopy_object,
    min_vf_criterion=mvfc,
    overwrite=True)
SimulationContextFiltering.perform_second_pass_of_context_filtering_on_buildings(
    urban_canopy_object=urban_canopy_object,
    number_of_rays=nb_of_rays,
    consider_windows=consider_windows,
    overwrite=True)


# -------------------------------------------------------------------------------------------
# Loop over scenarios for BIPV assessment
# -------------------------------------------------------------------------------------------

# BIPV
# Merge the face of the buildings to reduce the number of faces and the
#SimulationBuildingManipulationFunctions.make_merged_face_of_buildings_in_urban_canopy(
#    urban_canopy_object=urban_canopy_object)
# Generate the sensor grid
SimFunSolarRadAndBipv.generate_sensor_grid(urban_canopy_object=urban_canopy_object
                                           )
SimFunSolarRadAndBipv.run_annual_solar_irradiance_simulation(urban_canopy_object=urban_canopy_object)



# Export urban_canopy to pickle
SimulationCommonMethods.save_urban_canopy_object_to_pickle(urban_canopy_object=urban_canopy_object,
                                                           path_simulation_folder=default_path_simulation_folder)
# Export urban_canopy to json
SimulationCommonMethods.save_urban_canopy_to_json(urban_canopy_object=urban_canopy_object,
                                                  path_simulation_folder=default_path_simulation_folder)
