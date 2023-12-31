import os
import argparse
import logging

from step_methods.building_manipulation_function_for_main import SimulationBuildingManipulationFunctions
from step_methods.general_function_for_main import SimulationCommonMethods
from step_methods.load_bat_file_arguments import LoadArguments
from step_methods.load_building_or_geometry import SimulationLoadBuildingOrGeometry
from step_methods.post_processing_and_plots import SimulationPostProcessingAndPlots
from step_methods.context_filtering import SimulationContextFiltering
from step_methods.run_simulations import SolarOrPanelSimulation
from step_methods.solar_radiation_and_bipv import SimFunSolarRadAndBipv

from utils.utils_configuration import name_gh_components_logs_folder, path_scripts_tool_folder

user_logger = logging.getLogger("user")
dev_logger = logging.getLogger("dev")
user_logger.setLevel(logging.INFO)
dev_logger.setLevel(logging.INFO)
dev_handler = logging.FileHandler(os.path.join(path_scripts_tool_folder, "dev_log.log"))
user_formatter = logging.Formatter('%(message)s')
dev_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
dev_handler.setFormatter(dev_formatter)
dev_logger.addHandler(dev_handler)


def main():
    # Get the user parameters from the command line
    parser = argparse.ArgumentParser()
    # Parse the arguments and return them in a dictionary
    LoadArguments.add_user_parameters_to_parser(parser)
    LoadArguments.add_user_simulation_features_to_parser(parser)
    arguments_dictionary, simulation_step_dictionary = LoadArguments.parse_arguments_and_add_them_to_variable_dict(
        parser)

    # Initialization #
    # Make simulation folder
    if simulation_step_dictionary["run_make_simulation_folder"]:
        SimulationCommonMethods.make_simulation_folder(
            path_simulation_folder=arguments_dictionary["path_simulation_folder"])

    # Create the log files for the user
    if arguments_dictionary["gh_component_name"] is not None:
        user_handler = logging.FileHandler(
            os.path.join(arguments_dictionary['path_simulation_folder'], name_gh_components_logs_folder,
                         arguments_dictionary['gh_component_name'] + ".log"), mode="w")
        user_handler.setFormatter(user_formatter)
        user_logger.addHandler(user_handler)

    # Create or load urban canopy object
    if simulation_step_dictionary["run_create_or_load_urban_canopy_object"]:
        urban_canopy_object = SimulationCommonMethods.create_or_load_urban_canopy_object(
            path_simulation_folder=arguments_dictionary["path_simulation_folder"])

    # Load Buildings #
    # Extract GIS data
    if simulation_step_dictionary["run_extract_gis"]:
        SimulationLoadBuildingOrGeometry.add_2D_GIS_to_urban_canopy(urban_canopy=urban_canopy_object,
                                                                    path_gis=arguments_dictionary["path_gis"],
                                                                    path_additional_gis_attribute_key_dict=
                                                                    arguments_dictionary[
                                                                        "path_additional_gis_attribute_key_dict"],
                                                                    unit=arguments_dictionary["unit_gis"])
    # Load Buildings from LB Polyface3D json
    if simulation_step_dictionary["run_extract_buildings_from_polyface3d_json"]:
        SimulationLoadBuildingOrGeometry.add_buildings_from_lb_polyface3d_json_in_urban_canopy(
            urban_canopy_object=urban_canopy_object,
            path_lb_polyface3d_json_file=arguments_dictionary["path_file"],
            typology=arguments_dictionary["typology"])

    # Load Buildings from hbjson
    if simulation_step_dictionary["run_extract_buildings_from_hbjson_models"]:
        SimulationLoadBuildingOrGeometry.add_buildings_from_hbjson_to_urban_canopy(
            urban_canopy_object=urban_canopy_object, path_folder_hbjson=arguments_dictionary["path_folder"],
            path_file_hbjson=arguments_dictionary["path_file"],
            are_buildings_targets=arguments_dictionary["are_buildings_target"],
            keep_context_from_hbjson=arguments_dictionary["keep_context"])

    # Building manipulation #
    # Convert BuildingBasic obj tp BuildingModeled
    # todo @Elie

    # Remove Building from Urban canopy
    if simulation_step_dictionary["run_remove_building_list_from_urban_canopy"]:
        SimulationBuildingManipulationFunctions.remove_building_list_from_urban_canopy(
            urban_canopy_object=urban_canopy_object,
            building_id_list=arguments_dictionary["building_id_list"])

    # Move building to origin
    if (simulation_step_dictionary["run_move_buildings_to_origin"]
            or (urban_canopy_object.moving_vector_to_origin is not None
                and False in [building_obj.moved_to_origin for building_obj in
                              urban_canopy_object.building_dict.values()])):
        # Move to origin if asked or if some buildings, but not all of them (a priori new ones), were moved to origin
        # before
        SimulationBuildingManipulationFunctions.move_buildings_to_origin(
            urban_canopy_object=urban_canopy_object)

    # Merge faces of buildings
    if simulation_step_dictionary["run_make_merged_faces_hb_model"]:
        SimulationBuildingManipulationFunctions.make_merged_face_of_buildings_in_urban_canopy(
            urban_canopy_object=urban_canopy_object,
            building_id_list=arguments_dictionary["building_id_list"],
            orient_roof_mesh_to_according_to_building_orientation=arguments_dictionary[
                "orient_roof_according_to_building_orientation"],
            north_angle=arguments_dictionary["north_angle"])

    # Context filtering #
    # Generate bounding boxes
    if simulation_step_dictionary["run_generate_bounding_boxes"]:
        SimulationBuildingManipulationFunctions.make_oriented_bounding_boxes_of_buildings_in_urban_canopy(
            urban_canopy_object=urban_canopy_object,
            overwrite=arguments_dictionary["overwrite"])

    # Perform first step of context filtering
    if simulation_step_dictionary["run_first_pass_context_filtering"]:
        SimulationContextFiltering.perform_first_pass_of_context_filtering_on_buildings(
            urban_canopy_object=urban_canopy_object,
            building_id_list=arguments_dictionary["building_id_list"],
            on_building_to_simulate=arguments_dictionary["on_building_to_simulate"],
            min_vf_criterion=arguments_dictionary["min_vf_criterion"],
            overwrite=arguments_dictionary["overwrite"])

    # Perform second step of context filtering
    if simulation_step_dictionary["run_second_pass_context_filtering"]:
        SimulationContextFiltering.perform_second_pass_of_context_filtering_on_buildings(
            urban_canopy_object=urban_canopy_object,
            building_id_list=arguments_dictionary["building_id_list"],
            number_of_rays=arguments_dictionary["number_of_rays"],
            on_building_to_simulate=arguments_dictionary["on_building_to_simulate"],
            consider_windows=arguments_dictionary["consider_windows"],
            keep_shades_from_user=arguments_dictionary["keep_shades_from_user"],
            no_ray_tracing=arguments_dictionary["no_ray_tracing"],
            overwrite=arguments_dictionary["overwrite"],
            keep_discarded_faces=arguments_dictionary["keep_discarded_faces"])

    # Perform all steps of context filtering
    # todo @Elie

    # Solar radiations and BIPV simulations
    # Generate sensor grids
    if simulation_step_dictionary["run_generate_sensorgrids_on_buildings"]:
        SimFunSolarRadAndBipv.generate_sensor_grid(urban_canopy_object=urban_canopy_object,
                                                   building_id_list=arguments_dictionary["building_id_list"],
                                                   bipv_on_roof=arguments_dictionary["on_roof"],
                                                   bipv_on_facades=arguments_dictionary["on_facades"],
                                                   roof_grid_size_x=arguments_dictionary["roof_grid_size_x"],
                                                   facades_grid_size_x=arguments_dictionary[
                                                       "facades_grid_size_x"],
                                                   roof_grid_size_y=arguments_dictionary["roof_grid_size_y"],
                                                   facades_grid_size_y=arguments_dictionary[
                                                       "facades_grid_size_y"],
                                                   offset_dist=arguments_dictionary["offset_dist"],
                                                   overwrite=arguments_dictionary["overwrite"])
    # Run solar radiation
    if simulation_step_dictionary["run_annual_solar_irradiance_simulation"]:
        SimFunSolarRadAndBipv.run_annual_solar_irradiance_simulation(
            urban_canopy_object=urban_canopy_object,
            path_simulation_folder=arguments_dictionary["path_simulation_folder"],
            building_id_list=arguments_dictionary["building_id_list"],
            path_weather_file=arguments_dictionary["path_weather_file"],
            overwrite=arguments_dictionary["overwrite"],
            north_angle=arguments_dictionary["north_angle"],
            silent=arguments_dictionary["silent"])

    # Run panel simulation
    if simulation_step_dictionary["run_bipv_harvesting_and_lca_simulation"]:
        SimFunSolarRadAndBipv.run_bipv_harvesting_and_lca_simulation(urban_canopy_object,
                                                                     path_simulation_folder=arguments_dictionary[
                                                                         "path_simulation_folder"],
                                                                     bipv_scenario_identifier=arguments_dictionary[
                                                                         "bipv_scenario_identifier"],
                                                                     building_id_list=arguments_dictionary[
                                                                         "building_id_list"],
                                                                     roof_id_pv_tech=arguments_dictionary[
                                                                         "roof_id_pv_tech"],
                                                                     facades_id_pv_tech=arguments_dictionary[
                                                                         "facades_id_pv_tech"],
                                                                     efficiency_computation_method=arguments_dictionary[
                                                                         "efficiency_computation_method"],
                                                                     minimum_panel_eroi=arguments_dictionary[
                                                                         "minimum_panel_eroi"],
                                                                     start_year=arguments_dictionary["start_year"],
                                                                     end_year=arguments_dictionary["end_year"],
                                                                     replacement_scenario=arguments_dictionary[
                                                                         "replacement_scenario"],
                                                                     continue_simulation=(
                                                                         not arguments_dictionary["overwrite"]),
                                                                     replacement_frequency_in_years=
                                                                     arguments_dictionary[
                                                                         "replacement_frequency_in_years"],
                                                                     update_panel_technology=arguments_dictionary[
                                                                         "update_panel_technology"])

    # Microclimate weather files

    # Preprocessing Longwave radiation #

    # Building Energy Simulation #

    # Exports #
    # Export Urban canopy to pickle
    if simulation_step_dictionary["run_save_urban_canopy_object_to_pickle"]:
        SimulationCommonMethods.save_urban_canopy_object_to_pickle(urban_canopy_object=urban_canopy_object,
                                                                   path_simulation_folder=
                                                                   arguments_dictionary[
                                                                       "path_simulation_folder"])
    # Export Urban canopy to json
    if simulation_step_dictionary["run_save_urban_canopy_object_to_json"]:
        SimulationCommonMethods.save_urban_canopy_to_json(urban_canopy_object=urban_canopy_object,
                                                          path_simulation_folder=arguments_dictionary[
                                                              "path_simulation_folder"])

    # Post-processing panels
    if simulation_step_dictionary["generate_panels_results_in_csv"]:
        SimulationPostProcessingAndPlots.generate_csv_panels_simulation_results(
            urban_canopy_object=urban_canopy_object,
            path_simulation_folder=
            arguments_dictionary[
                "path_simulation_folder"])

    if simulation_step_dictionary["plot_graph_results_building_panel_simulation"]:
        SimulationPostProcessingAndPlots.plot_graphs(urban_canopy_object=urban_canopy_object,
                                                     path_simulation_folder=arguments_dictionary[
                                                         "path_simulation_folder"],
                                                     study_duration_years=arguments_dictionary[
                                                         "study_duration_years"],
                                                     country_ghe_cost=arguments_dictionary[
                                                         "country_ghe_cost"])


if __name__ == "__main__":
    main()
