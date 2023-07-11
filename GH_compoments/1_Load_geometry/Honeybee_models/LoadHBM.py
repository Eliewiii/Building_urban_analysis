"""Add a list of HB Models of buildings to the urban canopy building collecting.
    Inputs:
        _hb_model_list: List of Honeybee Models of buildings
        _are_targets_ : Boolean, True if the buildings to add are target buildings that we want to simulate
        path_folder_simulation_: Path to the simulation folder. By default, the code will be run in Appdata\Roaming\Building_urban_analysis\Simulation_temp
        _run: Plug in a button to run the component
    Output:
        path_folder_simulation: path to th esimulation folder to pass down to the next components"""

ghenv.Component.Name = "BUA Load HB Model to urban Canopy"
ghenv.Component.NickName = 'LoadHBM'
ghenv.Component.Message = '0.0.0'
ghenv.Component.Category = 'BUA'
ghenv.Component.SubCategory = '1 :: Load Buildings'
ghenv.Component.AdditionalHelpFromDocStrings = "1"


import os
import shutil
from honeybee.model import Model


def clean_path(path):
    path = path.replace("\\", "/")
         # todo, add the chech to see if the pass exist


def clean_log_for_out(path_log_file):
    with open(path_log_file, 'r') as log_file:
        log_data = log_file.read()
        log_line_list = log_data.split("\n")
        log_line_list = [line.split("[INFO] ")[-1] for line in log_line_list]
        log_line_list = [line.split("[WARNING] ")[-1] for line in log_line_list]
        log_line_list = [line.split("[CRITICAL] ")[-1] for line in log_line_list]
        log_line_list = [line.split("[ERROR] ")[-1] for line in log_line_list]
    return (log_line_list)


# Get Appdata\local folder
local_appdata = os.environ['LOCALAPPDATA']
path_tool = os.path.join(local_appdata, "Building_urban_analysis")

path_bat_file = os.path.join(path_tool, "Scripts", "mains_tool", "run_BUA.bat")

name_folder_temporary_files = "temporary_files"
name_hbjson_directory = "hbjsons_to_add" # name of the folder that will contain the hbjsons to add

# set default value for the simulation folder if not provided
if path_folder_simulation_ is None:
    path_folder_simulation_ = os.path.join(path_tool, "Simulation_temp")
# Clean the path and make sure it exist
else:
     path_folder_simulation_ = clean_path(path_folder_simulation_)
     # todo, add the chech to see if the pass exist

if _run and _hb_model_list is not None and _hb_model_list != []:
    # Make new folder in the simulation folder to store the honeybee models converted to json
    path_folder_honeybee_json = os.path.join(path_folder_simulation_,name_folder_temporary_files, name_hbjson_directory)
    if not os.path.exists(path_folder_honeybee_json):
        os.makedirs(path_folder_honeybee_json)
    else:
        shutil.rmtree(path_folder_honeybee_json)  # Delete the existing folder
        os.makedirs(path_folder_honeybee_json)  # Create a new folder in its place

    # Convert the honeybee models to json
    for i, hb_model in enumerate(_hb_model_list):
        # Make a name for the json file
        name_hb_model = "model_{}".format(i)
        # Make the path to the json file
        path_hb_model = os.path.join(path_folder_honeybee_json, name_hb_model + ".hbjson")
        # Convert the honeybee model to json
        Model.to_hbjson(hb_model, path_hb_model)

    # Write the command
    command = path_bat_file
    argument = " "  # Initialize the argument
    # Steps to execute
    argument = argument + "--make_simulation_folder 1 " + "--create_or_load_urban_canopy_object 1 " + "--path_folder {} ".format(path_folder_honeybee_json)+"--extract_buildings_from_hbjson_models 1 " + "--save_urban_canopy_object_to_pickle 1 " +"--generate_model_with_building_envelop 1 " + " --save_urban_canopy_object_to_json 1"

    # Optional argument of the bat file/Python script
    if path_folder_simulation_ is not None:
        argument = argument + ' -f "{}"'.format(path_folder_simulation_)
    if type(_are_targets_) is bool:
        argument = argument + ' -t "{}"'.format(int(_are_targets_))
    output = os.system(command + argument)
    print(command + argument)

    # Delete the folder with the honeybee models converted to json
    shutil.rmtree(path_folder_honeybee_json)

# path to th elog file to plot in the report
path_log_file = os.path.join(path_folder_simulation_, "out.txt")

# Extract the log if they exist
if os.path.isfile(path_log_file):
    out = clean_log_for_out(path_log_file)
    for line in out:
        print(line)


