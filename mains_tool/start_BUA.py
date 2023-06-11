from mains_tool.utils_general import *
from mains_tool.utils_main_import_scripts import *


def main():
    # Create the logs todo: @Elie, check with Sharon where to put them
    # currentDirectory = os.getcwd()
    # Logspath = "/logs"
    # isExist = os.path.exists(currentDirectory + Logspath)
    # if not isExist:
    #    os.makedirs(currentDirectory + Logspath)
    #
    # LOG_FILENAME = datetime.now().strftime(currentDirectory + Logspath + '/logfile_%H_%M_%S_%d_%m_%Y.log')
    # logging.basicConfig(filename=LOG_FILENAME, level=logging.INFO)

    # Get the user parameters from the command line
    parser = argparse.ArgumentParser()
    # Parse the arguments and return them in a dictionary
    LoadArguments.add_usermeters_to_parser(parser)
    LoadArguments.add_user_simulation_features_to_parser(parser)
    arguments_dictionary, simulation_step_dictionary = LoadArguments.parse_arguments_and_add_them_to_variable_dict(
        parser)

    # todo @Elie, check if to do it like this, a it creates global variables, or just use the dictionary as it is
    # # Import the variables the arguments in the main script
    # globals().update(arguments_dictionary)

    # Run the simulations steps according to the user parameters

    # Initialization #
    # Make simulation folder
    if simulation_step_dictionary["run_make_simulation_folder"]:
        SimulationCommonMethods.make_simulation_folder(
            path_folder_simulation=arguments_dictionary["path_folder_simulation"])
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
            urban_canopy_object=urban_canopy_object,
            path_folder_hbjson=arguments_dictionary["path_gis"])

    # Building manipulation #
    # Convert BuildingBasic obj tp BuildingModeled
    # todo @Elie
    # Remove Building from Urban canopy
    if simulation_step_dictionary["run_extract_buildings_from_hbjson_models"]:
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

    # Solar radiation analysis #
    # Perform Solar radiation
    if simulation_step_dictionary["run_radiation_simulation"]:
        SolarOrPanelSimulation.solar_radiation_simulation(urban_canopy_object=urban_canopy_object,
                                                          path_folder_simulation=arguments_dictionary[
                                                              "path_folder_simulation"],
                                                          path_weather_file=arguments_dictionary["path_weather_file"],
                                                          list_id=arguments_dictionary["list_id"],
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
                                                study_duration_in_years=arguments_dictionary["study_duration_years"],
                                                replacement_scenario=arguments_dictionary["replacement_scenario"])

        SimulationPostProcessingAndPlots.generate_csv_panels_simulation_results(urban_canopy_object=urban_canopy_object,
                                                                                path_folder_simulation=
                                                                                arguments_dictionary[
                                                                                    "path_folder_simulation"])
    # Microclimate weather files

    # Preprocessing Longwave radiation #

    # Building Energy Simulation #

    # Postprocessing and plots #
    # Generate Urban canopy envelop #todo @Elie delete and replace by add_building_envelops_to_urban_canopy_json
    if simulation_step_dictionary["run_generate_model_with_building_envelop"]:
        SimulationPostProcessingAndPlots.generate_hb_model_contains_all_building_envelopes_to_plot_Grasshopper(
            urban_canopy_object=urban_canopy_object,
            path_folder_simulation=arguments_dictionary["path_folder_simulation"])

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
                                                                                default_path_folder_simulation)

    # Save logs for the components
    if arguments_dictionary["gh_component_name"] is not None:
        SimulationCommonMethods.write_gh_component_user_logs(urban_canopy_object=urban_canopy_object,
                                                             path_folder_simulation=arguments_dictionary[
                                                                 "path_folder_simulation"],
                                                             logs=None)  # add the logs


if __name__ == "__main__":
    main()
