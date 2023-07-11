"""Add HB Models from hbjson to the urban canopy building collection
    Inputs:
        _path_hbjson_file_: Path to a hbjson file containing a HB Model to load in the Urban canopy
        _path_folder_with_hbjson_: Path to a directory containing hbjson files, containing HB Models to load in the Urban canopy
        _are_targets_ : Boolean, True if the buildings to add are target buildings that we want to simulate
        path_folder_simulation_: Path to the simulation folder. By default, the code will be run in Appdata\Roaming\Building_urban_analysis\Simulation_temp
        _run: Plug in a button to run the component
    Output:
        a: The a output variable"""

ghenv.Component.Name = "BUA Load hbjson to urban Canopy"
ghenv.Component.NickName = 'LoadHBjson'
ghenv.Component.Message = '0.0.0'
ghenv.Component.Category = 'BUA'
ghenv.Component.SubCategory = '1 :: Load Buildings'
ghenv.Component.AdditionalHelpFromDocStrings = "1"

import os
import shutil
from honeybee.model import Model


def clean_path(path):
    path = path.replace("\\", "/")
    return (path)


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
name_hbjson_directory = "hbjsons_to_add"  # name of the folder that will contain the hbjsons to add

if _run and ((_path_hbjson_file_ is not None and os.path.isfile(_path_hbjson_file_)) or (
        _path_folder_with_hbjson_ is not None and os.path.isdir(_path_folder_with_hbjson_))):

    # Write the command
    command = path_bat_file
    argument = " "  # Initialize the argument
    # Steps to execute
    argument = argument + "--make_simulation_folder 1 " + "--create_or_load_urban_canopy_object 1 " + "--extract_buildings_from_hbjson_models 1 " + "--save_urban_canopy_object_to_pickle 1 " + "--generate_model_with_building_envelop 1 " + " --save_urban_canopy_object_to_json 1"

    # Optional argument of the bat file/Python script
    if path_folder_simulation_ is not None:
        argument = argument + ' -f "{}"'.format(path_folder_simulation_)
    if type(_are_targets_) is bool:
        argument = argument + ' -t "{}"'.format(int(_are_targets_))
    if _path_hbjson_file_ is not None and os.path.isfile(clean_path(_path_hbjson_file_)):
        argument = argument + ' --path_file "{}"'.format(clean_path(_path_hbjson_file_))
    if _path_folder_with_hbjson_ is not None and os.path.isdir(clean_path(_path_folder_with_hbjson_)):
        argument = argument + ' --path_folder "{}"'.format(clean_path(_path_folder_with_hbjson_))

    output = os.system(command + argument)
    print(command + argument)

# set default value for the simulation folder if not provided
if path_folder_simulation_ is None:
    path_folder_simulation_ = os.path.join(path_tool, "Simulation_temp")
# Clean the path and make sure it exist
else:
    path_folder_simulation_ = clean_path(path_folder_simulation_)
    # todo, add the chech to see if the pass exist

# path to th elog file to plot in the report
path_log_file = os.path.join(path_folder_simulation_, "out.txt")

# Extract the log if they exist
if os.path.isfile(path_log_file):
    out = clean_log_for_out(path_log_file)
    for line in out:
        print(line)


