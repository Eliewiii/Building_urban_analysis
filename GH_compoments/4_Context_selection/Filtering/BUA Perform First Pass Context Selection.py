"""Perform the first pass of the context selection. Select the building that will be kept for the second step of filtering based on estimation of the supremum of the view factor of between the building faces andcontext bounding boxes.
It will automatically generate the bounding boxes of all the buildings if not done already.
    Inputs:
        path_simulation_folder_: Path to the simulation folder. Default = Appdata\Local\Building_urban_analysis\Simulation_temp
        building_id_list_: List of buildings we want to run the simulation on. If set to None, it will be run
        on the target buildings.
        _min_vf_criterion_: Minimum view factor criterion (in ]1:0[ ) of a surface of a context building boundary box
        to be kept for the second pass (Default = 0.01). If you want all buildings to be selected, just input a very low
        value, like 0.00001. Look at the documentation for more detailed explanation about the filtering process.
        _overwrite_: Set to True if the context filtering should be run again for buildings for which
        it was already performed, otherwise the existing filtering will remain. Mandatory if new buildings were added.
        _run: Plug in a button to run the component
    Output:
        report: logs
        path_simulation_folder_: Path to the folder."""


__author__ = "elie-medioni"
__version__ = "2024.05.27"

from ghpythonlib.componentbase import executingcomponent as component


ghenv.Component.Name = "BUA Perform First Pass Context Selection"
ghenv.Component.NickName = 'PerformFirstPassContextSelection'
ghenv.Component.Message = '1.1.0'
ghenv.Component.Category = 'BUA'
ghenv.Component.SubCategory = '4 :: Context Selection'


import os
import json

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

# Check path_simulation_folder_
if path_simulation_folder_ is None:
    path_simulation_folder_ = os.path.join(path_tool, "Simulation_temp")
elif os.path.isdir(path_simulation_folder_) is False:
    raise ValueError("The simulation folder does not exist, enter a valid path")

# Path to the urban canopy json file
path_json = os.path.join(path_simulation_folder_, "urban_canopy.json")

# Check the _min_vf_criterion_
if _min_vf_criterion_ is not None:
    if not 0<_min_vf_criterion_ <1:
        raise ValueError("The minimum view factor criterion should be in ]0:1[ range.")

if _run:

    # Check if the urban canopy json file exists
    if not os.path.isfile(path_json):
        raise ValueError("The urban canopy json file does not exist, buildings need to be loaded before running the context selection.")

    # Check if the building id list is not empty
    with open(path_json, "r") as f:
        urban_canopy_dict = json.load(f)
    if building_id_list_ == [] or building_id_list_ is None:
        pass
    else:  # Check if the building ids are in the json file
        for building_id in building_id_list_:
            try:
                urban_canopy_dict["buildings"][building_id]
            except KeyError:
                raise KeyError("Building with ID '{}' not found in the dictionary.".format(building_id))

    # Write the command
    command = path_bat_file
    # Steps to execute
    argument = " "
    argument = argument + "--make_simulation_folder 1 " + "--create_or_load_urban_canopy_object 1 " + "--save_urban_canopy_object_to_pickle 1 " + "--save_urban_canopy_object_to_json 1 " + "--run_first_pass_context_filtering 1 "
    # OPtionnal argument of the bat file/Python script
    if path_simulation_folder_ is not None:
        argument = argument + ' -f "{}"'.format(path_simulation_folder_)
    if building_id_list_ is not None and building_id_list_ != []:
        argument = argument + ' --building_id_list "{}"'.format(building_id_list_)
    if _min_vf_criterion_ is not None:
        argument = argument + " --min_vf_criterion {}".format(float(_min_vf_criterion_))
    if _overwrite_ is not None:
        argument = argument + " --overwrite {}".format(int(_overwrite_))

    # Add the name of the component to the argument
    argument = argument + " -c {}".format(ghenv.Component.NickName)
    # Run the bat file
    output = os.system(command + argument)


# Read the log file
report = read_logs(path_simulation_folder_)