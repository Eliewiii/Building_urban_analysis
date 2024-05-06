"""Load buildings from GIS in the Urban Canopy
    Inputs:
        path_simulation_folder_: Path to the folder the simulation will run. By default, the code will run in
                                Appdata\Local\Building_urban_analysis\Simulation_temp
        _path_gis : Path to the folder containing the GIS files (shp...) to load
        _unit_gis_ : Unit of the GIS file, meter ("m")  or degree ("deg"). By default set to meter
        _gis_attribute_keys_dict_ : Connect the component Add GIS Attribute Keys, to add labels for heights,
            number of floors etc. that are not considered by default by the code and that are specific to the
            GIS file you are using.
        move_to_origin_ : Center the urban canopy and its buildings on the origin of the coordinate system
        _run : Add and press a button to run the code
    Output:
        report: Logs
        path_simulation_folder_: Path to the simulation folder to pass down to the next components"""

ghenv.Component.Name = "BUA Load GIS in Urban Canopy"
ghenv.Component.NickName = 'LoadGISInUrbanCanopy'
ghenv.Component.Category = 'BUA'
ghenv.Component.SubCategory = '1 :: Load Buildings'
ghenv.Component.AdditionalHelpFromDocStrings = "1"

import os
import json
import shutil


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
name_folder_temporary_files = "temporary_files"

# set default value for the simulation folder if not provided

if path_simulation_folder_ is None:
    path_simulation_folder_ = os.path.join(path_tool, "Simulation_temp")
else:
     clean_path(path_simulation_folder_)

# Check GIS attribute keys dictionary
if _gis_attribute_keys_dict_ is not None:
    try:  # try to load the json
        gis_attribute_keys_dict = json.loads(_gis_attribute_keys_dict_)
    except:
        raise ValueError("The GIS attribute keys dictionary is not a valid JSON dictionnary, please use the output of the Add GIS Attribute Keys component")
    mandatory_keys = ["building_id_key_gis", "name", "age", "typology", "elevation", "height", "number of floor", "group"]
    for key in mandatory_keys:
        if key not in gis_attribute_keys_dict:
            raise ValueError("The GIS attribute keys dictionary is missing the key '{}'".format(key))
else:
    gis_attribute_keys_dict = None


if _run:
    # if there are additionnal keys for GIS attributes, make a json file containing the values
    if gis_attribute_keys_dict is not None:
        # Make the simulation folder as it might not exist yet
        command = path_bat_file + " --make_simulation_folder 1 --create_or_load_urban_canopy_object 1 -f " + path_simulation_folder_
        output = os.system(command)
        # Make the json file in the temporary folder in the simulation folder
        path_gis_attribute_keys_dict = os.path.join(path_simulation_folder_, name_folder_temporary_files, "gis_attribute_keys_dict.json")
        with open(path_gis_attribute_keys_dict, 'w') as json_file:
            json.dump(gis_attribute_keys_dict, json_file)
    else:
        path_gis_attribute_keys_dict = None  # Default value
    # Write the command
    command = path_bat_file
    argument = " "  # Initialize the argument
    # Steps to execute
    argument = argument + "--make_simulation_folder 1 " + "--create_or_load_urban_canopy_object 1 " + "--extract_gis 1 " + "--save_urban_canopy_object_to_pickle 1 " + " --save_urban_canopy_object_to_json 1 "
    # OPtionnal argument of the bat file/Python script
    if _path_gis is not None:
        argument = argument + ' -g "{}"'.format(_path_gis)
    if path_simulation_folder_ is not None:
        argument = argument + ' -f "{}"'.format(path_simulation_folder_)
    if path_gis_attribute_keys_dict is not None:
        argument = argument + ' -d "{}"'.format(path_gis_attribute_keys_dict)
    if _unit_gis_ is not None:
        argument = argument + ' -u "{}"'.format(_unit_gis_)
    if move_to_origin_ is not None:
        argument = argument + ' --move_buildings_to_origin "{}"'.format(int(move_to_origin_))
    # Add the name of the component to the argument
    argument = argument + " -c {}".format(ghenv.Component.NickName)
    # Run the bat file
    output = os.system(command + argument)

    # delete json file with the additionnal GIS attributes
    if path_gis_attribute_keys_dict is not None and os.path.exists(path_gis_attribute_keys_dict):
        os.remove(path_gis_attribute_keys_dict)

report = read_logs(path_simulation_folder_)
