"""
Script for the context selection paper UBES simulation.
"""
import os
import json
import logging

from copy import deepcopy

from unit_tests.utils_main_import_scripts import *

# Initialize logger
dev_logger = logging.getLogger("dev")
dev_logger.setLevel(logging.INFO)
dev_handler = logging.FileHandler('../dev_log.log', mode='w')
dev_formatter = logging.Formatter(
    '%(name)s: %(asctime)s - %(levelname)s - %(filename)s (function: %(funcName)s, line: %(lineno)d) - %(message)s')
dev_handler.setFormatter(dev_formatter)
dev_logger.addHandler(dev_handler)

# Paths to the different files
path_ubes_inputs = r"C:\Users\elie-medioni\OneDrive\OneDrive - Technion\Ministry of Energy Research\Papers\CheckContext\Simulations_Elie\Inputs\UBES"
name_building_folder_list = ["Residential", "Office"]
name_context_folder = "Context"
name_context_alternative_list = ["context_1", "context_2", "context_3"]
path_ep_simulation_parameter_json_file = None  # todo

# Initialize json result file
name_result_json_file = "residential.json"
path_result_folder = r"C:\Users\elie-medioni\OneDrive\OneDrive - Technion\Ministry of Energy Research\Papers\CheckContext\Simulations_Elie\results"
path_json_result_file = os.path.join(path_result_folder, name_result_json_file)

# EPW file
path_epw = ""  # todo

# Simulation parameters
mvfc_list = [0.5, 0.5, 0.5]
nb_of_rays = 3
consider_windows = False

cop_heating = 3
cop_cooling = 3

# Create the json result file if it does not exist
if not os.path.isfile(path_json_result_file):
    json_result_dict = {}
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
        urban_canopy_object_initial = SimulationCommonMethods.create_or_load_urban_canopy_object()
        # Load context from json
        SimulationLoadBuildingOrGeometry.add_buildings_from_lb_polyface3d_json_in_urban_canopy(
            urban_canopy_object=urban_canopy_object_initial,
            path_lb_polyface3d_json_file=path_context_alternative_json_file)
        # Make the merged face of the context buildings
        SimulationBuildingManipulationFunctions.make_merged_face_of_buildings_in_urban_canopy(
            urban_canopy_object=urban_canopy_object_initial, overwrite=True)
        SimulationBuildingManipulationFunctions.make_oriented_bounding_boxes_of_buildings_in_urban_canopy(
            urban_canopy_object=urban_canopy_object_initial, overwrite=True)

        # Load epw and simulation parameters
        UrbanBuildingEnergySimulationFunctions.load_epw_and_hb_simulation_parameters_for_ubes_in_urban_canopy(
            urban_canopy_obj=urban_canopy_object,
            path_weather_file=path_epw,
            overwrite=True)

        # Loop over the buildings
        for building_hbjson_name, building_hbjson_file in zip(building_hbjson_file_name_list,
                                                              building_hbjson_file_list):
            # Clean name
            building_name = building_hbjson_name.split(".")[0]  # Remove the extension
            # Copy the urban canopy object
            urban_canopy_object = deepcopy(
                urban_canopy_object_initial)  # If it does not work, can delete the BuildingModel objects
            # Load building from json
            SimulationLoadBuildingOrGeometry.add_buildings_from_hbjson_to_urban_canopy(
                urban_canopy_object=urban_canopy_object,
                path_folder_hbjson=None,
                path_file_hbjson=building_hbjson_file,
                are_buildings_targets=True,
                keep_context_from_hbjson=False)

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

                    # Perform the context filtering
                    SimulationContextFiltering.perform_first_pass_of_context_filtering_on_buildings(
                        urban_canopy_object=urban_canopy_object,
                        min_VF_criterion=mvfc,
                        overwrite=True)
                    SimulationContextFiltering.perform_second_pass_of_context_filtering_on_buildings(
                        urban_canopy_object=urban_canopy_object,
                        nb_of_rays=nb_of_rays,
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

                    bes_duration = None
                    bes_results_dict = {}



                    alternative_result_dict = {
                        "building_name": building_name,
                        "context_alternative": name_context_alternative,
                        "context_selection": {  # todo: fill the dictionary with the outputs
                            "first_pass": {
                                "mvfc": None,
                                "duration": None,
                                "nb_selected_buildings": None,
                            },
                            "second_pass": {
                                "number_of_rays": nb_of_rays,
                                "consider_windows": consider_windows,
                                "duration": None,
                                "nb_selected_shades": None,
                                "nb_user_shades": None,  # Louvers in that case
                            }
                        },
                        "BES":
                            {
                                "cop_heating": None,
                                "cop_cooling": None,
                                "duration": None,
                                "results": {
                                    "heating": bes_results_dict["heating"]["yearly"],
                                    "cooling": bes_results_dict["cooling"]["yearly"],
                                    "lighting": bes_results_dict["lighting"]["yearly"],
                                    "equipment": bes_results_dict["equipment"]["yearly"],
                                    "total": bes_results_dict["total"]["yearly"],
                                    "h+c": bes_results_dict["heating"]["yearly"] + bes_results_dict["cooling"][
                                        "yearly"],
                                    "h+c+l": bes_results_dict["heating"]["yearly"] + bes_results_dict["cooling"][
                                        "yearly"] + bes_results_dict["lighting"]["yearly"]
                                }
                            }
                    }

                # Update the result dictionary
                if building_name not in json_result_dict:
                    json_result_dict[building_name] = {}
                json_result_dict[alternative_identifier] = alternative_result_dict
                # Overwrite the json file
                with open(path_json_result_file, 'w') as json_file:
                    json.dump(json_result_dict, json_file)
