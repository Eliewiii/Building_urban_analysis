"""Generate a version of the HB model of the building with merged faces. It is useful to ignore the subdivisions
of floors and apartment. It can be used for the context selection and generate the mesh for the solar radiation simulation.
Only BuildingModelled objects (with a Honeybee Model) can generate a merged face HB Model.
    Inputs:
        path_simulation_folder_: Path to the folder. Default = Appdata\Local\Building_urban_analysis\Simulation_temp
        building_id_list_: list of buildings we want to run the simulation on. If set to None, it will be run on
        all the buildings.
        _merge_face_parameters_: Dictionary of parameters to merge the faces. You can plug the dedicated BUA Merge Face
        component. If empty, the default parameters will be used.
        _run: Plug in a button to run the component
    Output:
        report: logs
        path_simulation_folder_: Path to the folder."""

__author__ = "elie-medioni"
__version__ = "2024.05.07"

ghenv.Component.Name = "BUA Merge Building Faces"
ghenv.Component.NickName = 'MergeBuildingFaces'
ghenv.Component.Message = '1.0.0'
ghenv.Component.Category = 'BUA'
ghenv.Component.SubCategory = '3 :: Building manipulation'

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

# Check _bipv_parameters
if _merge_face_parameters_ is not None:
    try:  # try to load the json
        merge_face_parameters_dict = json.loads(_merge_face_parameters_)
    except:
        raise ValueError("The _merge_face_parameters_ is not valid, use the BUA Merge Face component as input")
    if not (isinstance(merge_face_parameters_dict, dict)
            or "orient_roof_according_to_building_orientation" not in merge_face_parameters_dict.keys()
            or "north_angle" not in merge_face_parameters_dict.keys()
            or "overwrite" not in merge_face_parameters_dict.keys()):
        raise ValueError("The _merge_face_parameters_ is not valid, use the BUA Merge Face component as input")
    else:
        orient_roof_according_to_building_orientation = merge_face_parameters_dict[
            "orient_roof_according_to_building_orientation"]
        north_angle = merge_face_parameters_dict["north_angle"]
        overwrite = merge_face_parameters_dict["overwrite"]
else:
    orient_roof_according_to_building_orientation = None
    north_angle = None
    overwrite = None

if _run:
    # Write the command
    command = path_bat_file
    # Steps to execute
    argument = " "
    argument = argument + "--make_simulation_folder 1 " + "--create_or_load_urban_canopy_object 1 " + "--save_urban_canopy_object_to_pickle 1 " + "--save_urban_canopy_object_to_json 1 " + "--make_merged_faces_hb_model 1 "
    # OPtionnal argument of the bat file/Python script
    if path_simulation_folder_ is not None:
        argument = argument + ' -f "{}"'.format(path_simulation_folder_)
    if building_id_list_ is not None and building_id_list_ != []:
        argument = argument + ' --building_id_list "{}"'.format(building_id_list_)
    if orient_roof_according_to_building_orientation is not None:
        argument = argument + " --orient_roof_according_to_building_orientation {}".format(
            int(orient_roof_according_to_building_orientation))
    if north_angle is not None:
        argument = argument + " --north_angle {}".format(float(north_angle))
    if overwrite is not None:
        argument = argument + " --overwrite {}".format(int(overwrite))

    # Add the name of the component to the argument
    argument = argument + " -c {}".format(ghenv.Component.NickName)
    # Run the bat file
    output = os.system(command + argument)

# set default value for the simulation folder if not provided
if path_simulation_folder_ is None:
    path_simulation_folder_ = os.path.join(path_tool, "Simulation_temp")

# Read the log file
report = read_logs(path_simulation_folder_)
