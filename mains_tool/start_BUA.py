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
    arguments_dictionary = LoadArguments.load_user_parameters(parser)
    simulation_step_dictionnary = LoadArguments.load_user_simulation_features(parser)

    # todo @Elie, check if to do it like this, a it creates global variables, or just use the dictionary as it is
    # # Import the variables the arguments in the main script
    # globals().update(arguments_dictionary)

    # Run the simulations steps according to the user parameters



    # Make simulation folder
    if simulation_step_dictionnary["run_make_simulation_folder"]:
        SimulationCommonMethods.make_simulation_folder(path_folder_simulation=arguments_dictionary["path_folder_simulation_para"])
    # Create or load urban canopy object
    if simulation_step_dictionnary["run_create_or_load_urban_canopy_object"]:
        urban_canopy_object = SimulationCommonMethods.create_or_load_urban_canopy_object(path_folder_simulation=arguments_dictionary["path_folder_simulation_para"])

    # Extract GIS data
    if simulation_step_dictionnary["run_extract_gis"]:
        SimulationLoadBuildingOrGeometry.add_2D_GIS_to_urban_canopy(urban_canopy=urban_canopy_object, path_gis=arguments_dictionary["path_gis_para"], path_additional_gis_attribute_key_dict=arguments_dictionary["path_additional_gis_attribute_key_dict_para"], unit=arguments_dictionary["unit_gis_para"], additional_gis_attribute_key_dict)






if __name__ == "__main__":
     main()

