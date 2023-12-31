""" Load Polyface3D json file into the urban canopy object
    Inputs:
        path_simulation_folder_: Path to the folder. Default = Appdata\Local\Building_urban_analysis\Simulation_temp
        _path_polyface3d_json_file: Path to the json file containing the polyface3d object
        _typology_: Typology of the building. Default = None
        _run: Plug in a button to run the component
    Output:
        report: logs
        path_simulation_folder_: Path to the folder."""

__author__ = "Eliewiii"
__version__ = "2023.12.27"

ghenv.Component.Name = "BUA Load Polyface3D json"
ghenv.Component.NickName = 'LoadPolyface3Djson'
ghenv.Component.Message = '0.0.0'
ghenv.Component.Category = 'BUA'
ghenv.Component.SubCategory = '1 :: Load geometry'

import os


def clean_path(path):
    path = path.replace("\\", "/")
    return (path)


def read_logs(path_simulation_folder):
    path_log_file = os.path.join(path_simulation_folder, "gh_components_logs",
                                 ghenv.Component.NickName + ".log")
    if os.path.isfile(path_log_file):
        with open(path_log_file, 'r') as log_file:
            log_data = log_file.read()
        return (log_data)
    else:
        return ("No log file found")


# Check path_simulation_folder_
if path_simulation_folder_ is not None and os.path.isdir(clean_path(path_simulation_folder_)) is False:
    raise ValueError("The simulation folder does not exist, enter a valid path")

# Get Appdata\local folder
local_appdata = os.environ['LOCALAPPDATA']
path_tool = os.path.join(local_appdata, "Building_urban_analysis")
path_bat_file = os.path.join(path_tool, "Scripts", "mains_tool", "run_BUA.bat")

# Possible values for typology, for now not operational
typology_possible_values_list = ["VALUES WILL BE PUT WHEN THE FUNCTION WILL BE OPERATIONAL"]

if _run:
    if not os.path.isfile(clean_path(_path_polyface3d_json_file)):
        raise ValueError("The polyface3d json file does not exist, enter a valid path")
    # Write the command
    command = path_bat_file
    # Steps to execute
    argument = " "
    argument = argument + "--make_simulation_folder 1 " + "--create_or_load_urban_canopy_object 1 " + "--save_urban_canopy_object_to_pickle 1 " + "--save_urban_canopy_object_to_json 1 " + "--extract_buildings_from_polyface3d_json 1 "
    # OPtionnal argument of the bat file/Python script
    if path_simulation_folder_ is not None:
        argument = argument + ' -f "{}"'.format(clean_path(path_simulation_folder_))
    if os.path.isfile(clean_path(_path_polyface3d_json_file)):
        argument = argument + ' --path_file "{}"'.format(clean_path(_path_polyface3d_json_file))
    if _typology_ is not None or _typology_ in typology_possible_values_list:
        argument = argument + ' --typology "{}"'.format(_typology_)

    # Add the name of the component to the argument
    argument = argument + " -c {}".format(ghenv.Component.NickName)
    # Run the bat file
    output = os.system(command + argument)

# set default value for the simulation folder if not provided
if path_simulation_folder_ is None:
    path_simulation_folder_ = os.path.join(path_tool, "Simulation_temp")

# Read the log file
report = read_logs(path_simulation_folder_)
