"""Perform the second pass of context selection. The first pass needs to be performed before running the second pass.
Note that it does not add the shades directly to the Honeybee Model of the buildings, they are stored separately,
but they are used in all the following steps of the simulation implying the shades.
    Inputs:
        path_simulation_folder_: Path to the simulation folder. Default = Appdata\Local\Building_urban_analysis\Simulation_temp
        building_id_list_: list of buildings we want to run the simulation on. If set to None, it will be run
        on the target buildings.
        _number_of_rays_: int: Number of rays to be used for the ray tracing, can be either 1,3 or 9. Default = 3,
        _consider_windows_: Set to True if the windows should be considered as potential shades.
        If so it will consider the reflexivity of the window material. Note that it can increase significantly the number of context surfaces and thus slow down the simulation.
        If set to false, only the facades, with their associated reflexivity will be considered. (Default = False)
        _no_ray_tracing_: Set to True if the ray tracing should not be performed for the context selection, it will just
        add all the surfaces of the selected context buildings as shades.
        _keep_discarded_surfaces_: Set to True if the discarded surfaces should be stored to be displayed later on.
        It can potentially slow down the simulation and increase significantly the size of the result files.
        _overwrite_: Set to True if the context selection should be run again for buildings for which
        it was already performed, otherwise the existing selection will remain. Mandatory if new buildings were added.
        _run: Plug in a button to run the component
    Output:
        report: logs
        path_simulation_folder_: Path to the folder."""

__author__ = "elie-medioni"
__version__ = "2024.05.07"


ghenv.Component.Name = "BUA Perform Second Pass Context Selection"
ghenv.Component.NickName = 'PerformSecondPassContextSelection'
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

# Check if number of rays is correct
if _number_of_rays_ not in [None,1, 3, 9]:
    raise ValueError("The number of rays should be either 1, 3 or 9")

if _run :

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
    argument = argument + "--make_simulation_folder 1 " + "--create_or_load_urban_canopy_object 1 " + "--save_urban_canopy_object_to_pickle 1 " + "--save_urban_canopy_object_to_json 1 " + "--run_second_pass_context_filtering 1 "
    # OPtionnal argument of the bat file/Python script
    if path_simulation_folder_ is not None:
        argument = argument + ' -f "{}"'.format(path_simulation_folder_)
    if building_id_list_ is not None and building_id_list_ != []:
        argument = argument + ' --building_id_list "{}"'.format(building_id_list_)
    # if _on_building_to_simulate_ is not None:  # This option can be added in the future, but it might confuse the user
    #     argument = argument + " --on_building_to_simulate {}".format(int(_on_building_to_simulate_))
    if _number_of_rays_ is not None:
        argument = argument + " --number_of_rays {}".format(int(_number_of_rays_))
    if _consider_windows_ is not None:
        argument = argument + " --consider_windows {}".format(int(_consider_windows_))
    # if _keep_shades_from_user_ is not None:  # This option can be added in the future, but it might confuse the user so the choice of deleting the shades forced by the user will be done when loading the buildings.
    #     argument = argument + " --keep_shades_from_user {}".format(int(_keep_shades_from_user_))
    if _no_ray_tracing_ is not None:
        argument = argument + " --no_ray_tracing {}".format(int(_no_ray_tracing_))
    if _keep_discarded_surfaces_ is not None:
        argument = argument + " --keep_discarded_faces {}".format(int(_keep_discarded_surfaces_))
    if _overwrite_ is not None:
        argument = argument + " --overwrite {}".format(int(_overwrite_))

    # Add the name of the component to the argument
    argument = argument + " -c {}".format(ghenv.Component.NickName)
    # Run the bat file
    output = os.system(command + argument)


# Read the log file
report = read_logs(path_simulation_folder_)
