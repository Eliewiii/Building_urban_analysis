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
    # Import the variables the arguments in the main script
    globals().update(arguments_dictionary)




if __name__ == "__main__":
     main()

