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
    LoadArguments.add_user_parameters_to_parser(parser)
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
            path_folder_simulation=arguments_dictionary["path_folder_simulation_para"])
    # Create or load urban canopy object
    if simulation_step_dictionary["run_create_or_load_urban_canopy_object"]:
        urban_canopy_object = SimulationCommonMethods.create_or_load_urban_canopy_object(
            path_folder_simulation=arguments_dictionary["path_folder_simulation_para"])

    # Load Buildings #
    # Extract GIS data
    if simulation_step_dictionary["run_extract_gis"]:
        SimulationLoadBuildingOrGeometry.add_2D_GIS_to_urban_canopy(urban_canopy=urban_canopy_object,
                                                                    path_gis=arguments_dictionary["path_gis_para"],
                                                                    path_additional_gis_attribute_key_dict=
                                                                    arguments_dictionary[
                                                                        "path_additional_gis_attribute_key_dict_para"],
                                                                    unit=arguments_dictionary["unit_gis_para"])
    # Load Buildings from json
    # todo @Elie

    # Building manipulation #
    # Convert BuildingBasic obj tp BuildingModeled
    # todo @Elie
    # Remove Building from Urban canopy
    # todo @Elie
    #

    # Move building to origin
    # todo @Elie

    # Context filtering #
    # Generate bounding boxes
    # todo @Elie
    # Perform context filtering
    # todo @Elie

    # Solar radiation analysis #
    # Perform Solar radiation

    # LCA and DMFA #
    # perform LCA and DMFA

    # Microclimate weather files

    # Preprocessing Longwave radiation #

    # Building Energy Simulation #

    # Postprocessing and plots #
    # Generate Urban canopy envelop
    if simulation_step_dictionary["run_generate_model_with_building_envelop"]:
        SimulationPostProcessingAndPlots.generate_hb_model_contains_all_building_envelopes_to_plot_Grasshopper(
            urban_canopy_object=urban_canopy_object,
            path_folder_simulation=arguments_dictionary["path_folder_simulation_para"])
    #

    # Exports #
    # Export Urban canopy to pickle
    if simulation_step_dictionary["run_save_urban_canopy_object_to_pickle"]:
        SimulationCommonMethods.save_urban_canopy_object_to_pickle(urban_canopy_object=urban_canopy_object,
                                                                   path_folder_simulation=arguments_dictionary[
                                                                       "path_folder_simulation_para"])
    # Export Urban canopy to json
    if simulation_step_dictionary["run_save_urban_canopy_object_to_json"]:
        SimulationCommonMethods.save_urban_canopy_to_json(urban_canopy_object=urban_canopy_object,
                                                          path_folder_simulation=arguments_dictionary[
                                                              "path_folder_simulation_para"])


if __name__ == "__main__":
    main()
