""" Load Polyface3D json file into the urban canopy object as a buildings
    Inputs:
        path_simulation_folder_: Path to the simulation folder. Default = Appdata\Local\Building_urban_analysis\Simulation_temp
        _path_polyface3d_json_file: Path to the json file containing the polyface3d object
        _typology_: Typology of the buildings, from List Of Typology Component. Cannot be used yet in the code.  Default = None
        _run: Plug in a button to run the component
    Output:
        report: logs
        path_simulation_folder_: Path to the simulation folder."""

__author__ = "elie-medioni"
__version__ = "2024.05.05"

ghenv.Component.Name = "BUA Load Polyface3D json"
ghenv.Component.NickName = 'LoadPolyface3Djson'
ghenv.Component.Category = 'BUA'
ghenv.Component.SubCategory = '1 :: Load Buildings'

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


# Get Appdata\local folder
local_appdata = os.environ['LOCALAPPDATA']
path_tool = os.path.join(local_appdata, "Building_urban_analysis")
path_bat_file = os.path.join(path_tool, "Scripts", "mains_tool", "run_BUA.bat")

# Check path_simulation_folder_
if path_simulation_folder_ is None or path_simulation_folder_=="":
    path_simulation_folder_ = os.path.join(path_tool, "Simulation_temp")
elif os.path.isdir(path_simulation_folder_) is False:
    raise ValueError("The simulation folder does not exist, enter a valid path")

# Possible values for typology, for now not operational
typology_possible_values_list = ["VALUES WILL BE PUT WHEN THE FUNCTION WILL BE OPERATIONAL"]

if _path_polyface3d_json_file is not None and not os.path.isfile(clean_path(_path_polyface3d_json_file)):
    raise ValueError("The polyface3d json file does not exist, enter a valid path")

if _run:


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

# Read the log file
report = read_logs(path_simulation_folder_)
