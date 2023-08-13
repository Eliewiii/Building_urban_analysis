import os
import argparse
import logging

from step_methods.building_manipulation_function_for_main import SimulationBuildingManipulationFunctions
from step_methods.general_function_for_main import SimulationCommonMethods
from step_methods.load_bat_file_arguments import LoadArguments
from step_methods.load_building_or_geometry import SimulationLoadBuildingOrGeometry
from step_methods.post_processing_and_plots import SimulationPostProcessingAndPlots
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
            path_folder_simulation=arguments_dictionary["path_folder_simulation"])

    # # Create the log files for the user
    # user_handler = logging.FileHandler(os.path.join(arguments_dictionary['path_folder_simulation'],name_gh_components_logs_folder, arguments_dictionary['gh_component_name']+".log"))
    # user_handler.setFormatter(user_formatter)
    # user_logger.addHandler(user_handler)

    # Create or load urban canopy object
    if simulation_step_dictionary["run_create_or_load_urban_canopy_object"]:
        urban_canopy_object = SimulationCommonMethods.create_or_load_urban_canopy_object(
            path_folder_simulation=arguments_dictionary["path_folder_simulation"])

    # Load Buildings #
    # Extract GIS data
    if simulation_step_dictionary["run_extract_gis"]:
        SimulationLoadBuildingOrGeometry.add_2D_GIS_to_urban_canopy(urban_canopy=urban_canopy_object,
                                                                    path_gis=arguments_dictionary["path_gis"],
                                                                    path_additional_gis_attribute_key_dict=
                                                                    arguments_dictionary[
                                                                        "path_additional_gis_attribute_key_dict"],
                                                                    unit=arguments_dictionary["unit_gis"])
    # Load Buildings from json
    if simulation_step_dictionary["run_extract_buildings_from_hbjson_models"]:
        SimulationLoadBuildingOrGeometry.add_buildings_from_hbjson_to_urban_canopy(
            urban_canopy_object=urban_canopy_object, path_folder_hbjson=arguments_dictionary["path_folder"],
            path_file_hbjson=arguments_dictionary["path_file"],
            are_buildings_targets=arguments_dictionary["are_buildings_target"])

    # Building manipulation #
    # Convert BuildingBasic obj tp BuildingModeled
    # todo @Elie
    # Remove Building from Urban canopy
    if simulation_step_dictionary["run_remove_building_list_from_urban_canopy"]:
        SimulationBuildingManipulationFunctions.remove_building_list_from_urban_canopy(
            urban_canopy_object=urban_canopy_object,
            building_id_list=arguments_dictionary["building_id_list"])

    # Move building to origin
    if simulation_step_dictionary["run_move_buildings_to_origin"] or (
            urban_canopy_object.moving_vector_to_origin is not None and False in [building_obj.moved_to_origin for
                                                                                  building_obj in
                                                                                  urban_canopy_object.building_dict.values()]):
        # Move to origin if asked or if some buildings, but not all of them (a priori new ones), were moved to origin before
        SimulationBuildingManipulationFunctions.move_buildings_to_origin(urban_canopy_object=urban_canopy_object)

    # Context filtering #
    # Generate bounding boxes
    # todo @Elie
    # Perform context filtering
    # todo @Elie

    # Solar radiations and BIPV simulations
    # Generate sensor grids
    if simulation_step_dictionary["run_generate_sensorgrids_on_buildings"]:
        SimFunSolarRadAndBipv.genrate_sensor_grid(urban_canopy_object=urban_canopy_object,
                                                  building_id_list=arguments_dictionary["building_id_list"],
                                                  do_simulation_on_roof=arguments_dictionary["on_roof"],
                                                  do_simulation_on_facade=arguments_dictionary["on_facades"],
                                                  roof_grid_size_x=arguments_dictionary["roof_grid_size_x"],
                                                  facade_grid_size_x=arguments_dictionary["facade_grid_size_x"],
                                                  roof_grid_size_y=arguments_dictionary["roof_grid_size_y"],
                                                  facade_grid_size_y=arguments_dictionary["facade_grid_size_y"],
                                                  offset_dist=arguments_dictionary["offset_dist"])
    # Run solar radiation
    if simulation_step_dictionary["run_solar_radiation_simulation"]:
        SimFunSolarRadAndBipv.run_annual_solar_irradiance_simulation(
            urban_canopy_object=urban_canopy_object,
            path_folder_simulation=arguments_dictionary["path_folder_simulation"],
            building_id_list=arguments_dictionary["building_id_list"],
            path_weather_file=arguments_dictionary["path_weather_file"],
            overwrite=arguments_dictionary["overwrite"],
            north_angle=arguments_dictionary["north_angle"],
            silent=arguments_dictionary["silent"])

    # Solar radiation analysis #  todo @Elie : old version to delete
    # Perform Solar radiation
    if simulation_step_dictionary["run_radiation_simulation"]:
        SolarOrPanelSimulation.solar_radiation_simulation(urban_canopy_object=urban_canopy_object,
                                                          path_folder_simulation=arguments_dictionary[
                                                              "path_folder_simulation"],
                                                          path_weather_file=arguments_dictionary["path_weather_file"],
                                                          list_id=arguments_dictionary["building_id_list"],
                                                          grid_size=arguments_dictionary["grid_size"],
                                                          offset_dist=arguments_dictionary["offset_dist"],
                                                          on_roof=arguments_dictionary["on_roof"],
                                                          on_facades=arguments_dictionary["on_facades"])

    # LCA and DMFA #
    # perform LCA and DMFA
    if simulation_step_dictionary["run_panel_simulation"]:
        SolarOrPanelSimulation.panel_simulation(urban_canopy_object=urban_canopy_object,
                                                path_folder_simulation=arguments_dictionary["path_folder_simulation"],
                                                path_pv_tech_dictionary_json=arguments_dictionary[
                                                    "path_pv_tech_dictionary"],
                                                id_pv_tech_roof=arguments_dictionary["id_pv_tech_roof"],
                                                id_pv_tech_facades=arguments_dictionary["id_pv_tech_facades"],
                                                minimum_ratio_energy_harvested_on_primary_energy=arguments_dictionary[
                                                    "minimum_ratio_energy_harvested_on_primary_energy"],
                                                performance_ratio=arguments_dictionary["performance_ratio"],
                                                study_duration_in_years=arguments_dictionary["study_duration_years"],
                                                replacement_scenario=arguments_dictionary["replacement_scenario"],
                                                replacement_year=arguments_dictionary["every_X_years"])

    # Microclimate weather files

    # Preprocessing Longwave radiation #

    # Building Energy Simulation #

    # Postprocessing and plots #
    if simulation_step_dictionary["run_generate_model_with_building_envelop"]:
        SimulationPostProcessingAndPlots.add_building_envelops_to_urban_canopy_json(
            urban_canopy_object=urban_canopy_object)

    # Exports #
    # Export Urban canopy to pickle
    if simulation_step_dictionary["run_save_urban_canopy_object_to_pickle"]:
        SimulationCommonMethods.save_urban_canopy_object_to_pickle(urban_canopy_object=urban_canopy_object,
                                                                   path_folder_simulation=arguments_dictionary[
                                                                       "path_folder_simulation"])
    # Export Urban canopy to json
    if simulation_step_dictionary["run_save_urban_canopy_object_to_json"]:
        SimulationCommonMethods.save_urban_canopy_to_json(urban_canopy_object=urban_canopy_object,
                                                          path_folder_simulation=arguments_dictionary[
                                                              "path_folder_simulation"])

    # Post-processing panels
    if simulation_step_dictionary["generate_panels_results_in_csv"]:
        SimulationPostProcessingAndPlots.generate_csv_panels_simulation_results(urban_canopy_object=urban_canopy_object,
                                                                                path_folder_simulation=
                                                                                arguments_dictionary[
                                                                                    "path_folder_simulation"])

    if simulation_step_dictionary["plot_graph_results_building_panel_simulation"]:
        SimulationPostProcessingAndPlots.plot_graphs(urban_canopy_object=urban_canopy_object,
                                                     path_folder_simulation=arguments_dictionary[
                                                         "path_folder_simulation"],
                                                     study_duration_years=arguments_dictionary[
                                                         "study_duration_years"],
                                                     country_ghe_cost=arguments_dictionary[
                                                         "country_ghe_cost"])

    # Save logs for the components
    if arguments_dictionary["gh_component_name"] is not None:
        SimulationCommonMethods.write_gh_component_user_logs(urban_canopy_object=urban_canopy_object,
                                                             path_folder_simulation=arguments_dictionary[
                                                                 "path_folder_simulation"],
                                                             logs=None)  # add the logs


if __name__ == "__main__":
    main()
