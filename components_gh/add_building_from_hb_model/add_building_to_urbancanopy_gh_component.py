"""Add a list of HB Models of buildings to the urban canopy building collecting.
    Inputs:
        _hb_model_list: List of Honeybee Models of buildings
        path_folder_simulation: Path to the simulation folder. By default, the code will be run in Appdata\Roaming\Building_urban_analysis\Simulation_temp
        _run: Plug in a button to run the component
    Output:
        a: The a output variable"""

import os
import shutil
from honeybee.model import Model


def clean_path(path):
    path = path.replace("\\", "/")


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

# Path to the bat file
path_bat_file = os.path.join(path_tool, "Scripts", "components_gh", "add_building_from_hb_model", "add_hbjson_buildings.bat")
# name of the folder that will contain the hbjsons to add
name_hbjson_directory = "hbjsons_to_add"

# set default value for the simulation folder if not provided
if path_folder_simulation_ is None:
    path_folder_simulation_ = os.path.join(path_tool, "Simulation_temp")

if _run:
    # Make new folder in the simulation folder to store the honeybee models converted to json
    path_folder_honeybee_json = os.path.join(path_folder_simulation_, name_hbjson_directory)
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
    # argument =" -t 1"
    argument = " "
    # Optional argument of the bat file/Python script
    if path_folder_simulation_ is not None:
        argument = argument + ' -f "{}"'.format(path_folder_simulation_)
    if type(_are_targets_) is bool:
        argument = argument + ' -tar "{}"'.format(_are_targets_)
    if make_hb_model_building_envelop_ is not None and type(make_hb_model_building_envelop_) == bool:
        argument = argument + ' -e "{}"'.format(int(make_hb_model_building_envelop_))
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

path_hb_model_envelop_json = os.path.join(path_folder_simulation_, "buildings_envelops.hbjson")
