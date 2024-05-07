"""Add HB Models from hbjson to the urban canopy building collection
    Inputs:
        path_simulation_folder_: Path to the simulation folder. By default, the code will be run in Appdata\Roaming\Building_urban_analysis\Simulation_temp
        _path_hbjson_file_: Path to a hbjson file containing a HB Model to load in the Urban canopy. A list of files can inputted, they will be loaded one after another.
        _path_folder_with_hbjson_: Path to a directory containing hbjson files, containing HB Models to load in the Urban canopy
        _are_targets_ : True if the buildings to add are target buildings that we want to simulate
        keep_context_: True if you want to keep the context of the HB Model of the hbjsons. (Default: False)
        _run: Plug in a button to run the component
    Output:
        report: logs
        path_folder_simulation_: path to the simulation folder to pass down to the next components
"""
__author__ = "elie-medioni"
__version__ = "2024.05.05"

ghenv.Component.Name = "BUA Load HBjsons in Urban Canopy"
ghenv.Component.NickName = 'LoadHBjsonsInUrbanCanopy'
ghenv.Component.Category = 'BUA'
ghenv.Component.SubCategory = '1 :: Load Buildings'
ghenv.Component.AdditionalHelpFromDocStrings = "1"

import os
import shutil
from honeybee.model import Model


def clean_path(path):
    path = path.replace("\\", "/")
    return (path)


def read_logs(path_simulation_folder):
    path_log_file = os.path.join(path_simulation_folder_, "gh_components_logs",
                                 ghenv.Component.NickName + ".log")
    if os.path.isfile(path_log_file):
        with open(path_log_file, 'r') as log_file:
            log_data = log_file.read()
        return (log_data)
    else:
        return ("No log file found")



# Get Appdata\local folder
local_appdata = os.environ['LOCALAPPDATA']
path_tool = os.path.join(local_appdata, "Building_urban_analysis")

path_bat_file = os.path.join(path_tool, "Scripts", "mains_tool", "run_BUA.bat")

if _run and ((_path_hbjson_file_ is not None and os.path.isfile(_path_hbjson_file_)) or (
        _path_folder_with_hbjson_ is not None and os.path.isdir(_path_folder_with_hbjson_))):

    # Write the command
    command = path_bat_file
    argument = " "  # Initialize the argument
    # Steps to execute
    argument = argument + "--make_simulation_folder 1 " + "--create_or_load_urban_canopy_object 1 " + "--extract_buildings_from_hbjson_models 1 " + "--save_urban_canopy_object_to_pickle 1 " + " --save_urban_canopy_object_to_json 1"

    # Optional argument of the bat file/Python script
    if path_simulation_folder_ is not None:
        argument = argument + ' -f "{}"'.format(path_simulation_folder_)
    if type(_are_targets_) is bool:
        argument = argument + ' -t "{}"'.format(int(_are_targets_))
    if type(keep_context_) is bool:
        argument = argument + ' --keep_context "{}"'.format(int(keep_context_))
    if _path_hbjson_file_ is not None and os.path.isfile(clean_path(_path_hbjson_file_)):
        argument = argument + ' --path_file "{}"'.format(clean_path(_path_hbjson_file_))
    if _path_folder_with_hbjson_ is not None and os.path.isdir(clean_path(_path_folder_with_hbjson_)):
        argument = argument + ' --path_folder "{}"'.format(clean_path(_path_folder_with_hbjson_))
    # Add the name of the component to the argument
    argument = argument + " -c {}".format(ghenv.Component.NickName)
    # Run the bat file
    output = os.system(command + argument)

# set default value for the simulation folder if not provided
if path_simulation_folder_ is None:
    path_simulation_folder_ = os.path.join(path_tool, "Simulation_temp")
# read the log file
report = read_logs(path_simulation_folder_)

