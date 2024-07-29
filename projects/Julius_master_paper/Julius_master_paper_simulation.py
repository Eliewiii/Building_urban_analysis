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

# Paths to the different files
path_ubes_inputs = r"C:\Users\elie-medioni\OneDrive\OneDrive - Technion\Ministry of Energy Research\Papers\CheckContext\Simulations_Elie\Inputs\UBES"  # todo : change to the correct path
name_building_folder_list = ["Residential", "Office"]
name_context_folder = "Context"
name_context_alternative_list = ["context_1", "context_2", "context_3"]
path_ep_simulation_parameter_json_file = default_path_hbjson_simulation_parameter_file

# Initialize json result file
name_result_json_file = "results_context_filter.json"
path_result_folder = r"C:\Users\elie-medioni\OneDrive\OneDrive - Technion\Ministry of Energy Research\Papers\CheckContext\Simulations_Elie\results"
path_json_result_file = os.path.join(path_result_folder, name_result_json_file)

# EPW file
path_epw = r"C:\Users\elie-medioni\AppData\Local\Building_urban_analysis\Libraries\EPW\IS_5280_A_Tel_Aviv.epw"


# Simulation parameters
mvfc_list = [0.99, 0.1,0.05, 0.01]
nb_of_rays = 3
consider_windows = False

cop_heating = 3
cop_cooling = 3

# Definition of Scenarios
rooftech_baseline = None # baseline csi id
envtech_baseline = None # baseline csi id
replacement_baseline = 10 # years

envtech_aesthetic = # baseline beige csi id
rooftech_econ_opt = # csi roof optimistic
envtech_econ_opt = # csi grey env optimistic
rooftech_econ_pess = # csi roof pessimistic
envtech_econ_pess = # csi grey env pessimistic


scenarios_dict = {
    "baseline":{
    "rooftech" : rooftech_baseline,
    "envtech" : envtech_baseline,
    "replacement" = replacement_baseline
    },
    "rep_5" : {
    "rooftech" : rooftech_baseline,
    "envtech" : envtech_baseline,
    "replacement" = 5
    },
    "rep_15": {
    "rooftech" : rooftech_baseline,
    "envtech" : envtech_baseline,
    "replacement" = 15
    },
    "rep_20": {
    "rooftech" : rooftech_baseline,
    "envtech" : envtech_baseline,
    "replacement" = 20
    },
    "rep_25": {
    "rooftech" : rooftech_baseline,
    "envtech" : envtech_baseline,
    "replacement" = 25
    },
    "aesthetic": {
    "rooftech" : rooftech_baseline,
    "envtech" : envtech_aesthetic,
    "replacement" = replacement_baseline
    },
    "econ_opt": {
    "rooftech" : rooftech_econ_opt,
    "envtech" : envtech_econ_opt,
    "replacement" = replacement_baseline
    },
    "econ_pess": {
    "rooftech" : rooftech_econ_pess,
    "envtech" : envtech_econ_pess,
    "replacement" = replacement_baseline
    },
    "cdte": {
    "rooftech" : rooftech_baseline,
    "envtech" : envtech_baseline,
    "replacement" = replacement_baseline
    },
    "cigs": {
    "rooftech" : rooftech_baseline,
    "envtech" : envtech_baseline,
    "replacement" = replacement_baseline
    }
}



# Create the json result file if it does not exist
if not os.path.isfile(path_json_result_file):
    json_result_dict = {}
    with open(path_json_result_file, 'w') as json_file:
        json.dump(json_result_dict, json_file)
else:
    with open(path_json_result_file, 'r') as json_file:
        json_result_dict = json.load(json_file)

# loop over the alternatieves
for name_building_folder in name_building_folder_list:
    path_building_folder = os.path.join(path_ubes_inputs, name_building_folder)
    for name_context_alternative in name_context_alternative_list:
        # Path to the context alternative json file
        path_context_alternative_json_file = os.path.join(path_ubes_inputs, name_context_folder,
                                                          name_context_alternative + ".json")
        # list of files in the building folder
        path_building_context_alternative_folder = os.path.join(path_building_folder,
                                                                name_context_alternative)
        building_hbjson_file_name_list = os.listdir(path_building_context_alternative_folder)
        building_hbjson_file_list = [os.path.join(path_building_context_alternative_folder, file_name) for
                                     file_name in building_hbjson_file_name_list]

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

        # Loop over the buildings
        for building_hbjson_name, building_hbjson_file in zip(building_hbjson_file_name_list,
                                                              building_hbjson_file_list):
            # Delete previous traget building if there is any
            target_building_id = None
            for building_id, building_obj in urban_canopy_object.building_dict.items():
                if isinstance(building_obj, BuildingModeled):
                    target_building_id = building_id  # Get the first building that is a BuildingModeled, there is only one anyway
                    break
            if target_building_id is not None:
                urban_canopy_object.remove_building_from_dict(target_building_id)

            # Clean name
            building_name = building_hbjson_name.split(".")[0]  # Remove the extension
            # Load building from json
            SimulationLoadBuildingOrGeometry.add_buildings_from_hbjson_to_urban_canopy(
                urban_canopy_object=urban_canopy_object,
                path_folder_hbjson=None,
                path_file_hbjson=building_hbjson_file,
                are_buildings_targets=True,
                keep_context_from_hbjson=False)

            # Get the id of the target building
            target_building_id = None
            for building_id, building_obj in urban_canopy_object.building_dict.items():
                if isinstance(building_obj, BuildingModeled):
                    target_building_id = building_id  # Get the first building that is a BuildingModeled, there is only one anyway
                    break

            # Make the merged face of the building (not too sure if necessary)
            SimulationBuildingManipulationFunctions.make_merged_face_of_buildings_in_urban_canopy(
                urban_canopy_object=urban_canopy_object, overwrite=False)
            # Make the oriented bounding boxes of the building (not too sure if necessary)
            SimulationBuildingManipulationFunctions.make_oriented_bounding_boxes_of_buildings_in_urban_canopy(
                urban_canopy_object=urban_canopy_object, overwrite=False)

            # Loop over the simulation parameters
            for mvfc in mvfc_list:
                for no_ray_tracing in [True, False]:

                    # Alternative identifier
                    alternative_identifier = f"{building_name}_mvfc_{mvfc}_NBray_{nb_of_rays}_no_ray_tracing_{no_ray_tracing}"
                    if alternative_identifier in json_result_dict:
                        continue

                    # log
                    dev_logger.warning(
                        f"Building: {building_name}, Context alternative: {name_context_alternative}, MVFC: {mvfc}, No ray tracing: {no_ray_tracing}")

                    # Perform the context filtering
                    SimulationContextFiltering.perform_first_pass_of_context_filtering_on_buildings(
                        urban_canopy_object=urban_canopy_object,
                        min_vf_criterion=mvfc,
                        overwrite=True)
                    SimulationContextFiltering.perform_second_pass_of_context_filtering_on_buildings(
                        urban_canopy_object=urban_canopy_object,
                        number_of_rays=nb_of_rays,
                        consider_windows=consider_windows,
                        no_ray_tracing=no_ray_tracing,
                        keep_shades_from_user=True,
                        overwrite=True)

                    # UBES
                    # Write IDF
                    UrbanBuildingEnergySimulationFunctions.generate_idf_files_for_ubes_with_openstudio_in_urban_canopy(
                        urban_canopy_obj=urban_canopy_object,
                        overwrite=True,
                        silent=True)
                    # Run IDF through EnergyPlus
                    UrbanBuildingEnergySimulationFunctions.run_idf_files_with_energyplus_for_ubes_in_urban_canopy(
                        urban_canopy_obj=urban_canopy_object,
                        overwrite=True,
                        silent=True)
                    # Extract UBES results
                    UrbanBuildingEnergySimulationFunctions.extract_results_from_ep_simulation(
                        urban_canopy_obj=urban_canopy_object,
                        cop_heating=3., cop_cooling=3.)

                    # Extract all the results
                    context_selection_results_dict = urban_canopy_object.building_dict[
                        target_building_id].shading_context_obj.to_dict()
                    bes_results_dict = urban_canopy_object.building_dict[target_building_id].bes_obj.to_dict()

                    alternative_result_dict = {
                        "building_name": building_name,
                        "context_alternative": name_context_alternative,
                        "context_selection": {  # todo: fill the dictionary with the outputs
                            "first_pass": {
                                "mvfc": context_selection_results_dict["min_vf_criterion"],
                                "duration": context_selection_results_dict["first_pass_duration"],
                                "nb_selected_buildings": len(context_selection_results_dict["selected_context_building_id_list"]),
                            },
                            "second_pass": {
                                "number_of_rays": nb_of_rays,
                                "consider_windows": consider_windows,
                                "no_ray_tracing": no_ray_tracing,
                                "duration": context_selection_results_dict["second_pass_duration"],
                                "nb_selected_shades": len(context_selection_results_dict["context_shading_hb_shade_list"]),
                                "nb_user_shades": None,  # Louvers in that case
                            }
                        },
                        "BES":
                            {
                                "cop_heating": bes_results_dict["cop_heating"],
                                "cop_cooling": bes_results_dict["cop_cooling"],
                                "duration": bes_results_dict["sim_duration"],
                                "results": {
                                    "heating": bes_results_dict["bes_results_dict"]["heating"]["yearly"],
                                    "cooling": bes_results_dict["bes_results_dict"]["cooling"]["yearly"],
                                    "lighting": bes_results_dict["bes_results_dict"]["lighting"]["yearly"],
                                    "equipment": bes_results_dict["bes_results_dict"]["equipment"]["yearly"],
                                    "total": bes_results_dict["bes_results_dict"]["total"]["yearly"],
                                    "h+c": bes_results_dict["bes_results_dict"]["heating"]["yearly"] +
                                           bes_results_dict["bes_results_dict"]["cooling"][
                                               "yearly"],
                                    "h+c+l": bes_results_dict["bes_results_dict"]["heating"]["yearly"] +
                                             bes_results_dict["bes_results_dict"]["cooling"][
                                                 "yearly"] + bes_results_dict["bes_results_dict"]["lighting"][
                                                 "yearly"]
                                }
                            }
                    }


                    json_result_dict[alternative_identifier] = alternative_result_dict
                    # Overwrite the json file
                    with open(path_json_result_file, 'w') as json_file:
                        json.dump(json_result_dict, json_file)
