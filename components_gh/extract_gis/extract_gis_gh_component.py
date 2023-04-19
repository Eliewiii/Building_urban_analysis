"""Provides a scripting component.
    Inputs:
        x: The x script variable
        y: The y script variable
    Output:
        a: The a output variable"""

#__author__ = "elie-medioni"
#__version__ = "2023.02.08"


from building.utils_building import *

_run = None
_gis_attribute_keys_dict_ = None
_path_gis = None
unit_gis = None
move_to_origin_ = None

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

def get_sppdata_local_folder():
    global path_gis_extract_bat,path_tool
    local_appdata = os.environ['LOCALAPPDATA']
    path_tool = os.path.join(local_appdata, "Building_urban_analysis")
    path_gis_extract_bat = os.path.join(path_tool, "Scripts", "components_gh", "extract_gis", "extract_gis.bat")
get_sppdata_local_folder()

#TODO who change this value?
if _run:
    # if there are additionnal keys for GIS attributes, make a json file containing the values
    path_gis_attribute_keys_dict = None  # default value
    if _gis_attribute_keys_dict_ is not None:
        None
        # Make a json file that contains the dictionnary
        # todo
        # path_gis_attribute_keys_dict = put path

    # Write the command
    command = path_gis_extract_bat
    # argument =" -t 1"
    argument = " "
    # OPtionnal argument of the bat file/Python script
    if _path_gis is not None:
        argument = argument + ' -g "{}"'.format(_path_gis)
    if path_folder_simulation_ is not None:
        argument = argument + ' -f "{}"'.format(path_folder_simulation_)
    if path_gis_attribute_keys_dict is not None:
        argument = argument + ' -d "{}"'.format(path_gis_attribute_keys_dict)
    if unit_gis is not None:
        argument = argument + ' -u "{}"'.format(unit_gis)
    if move_to_origin_ is not None:
        argument = argument + ' -m "{}"'.format(int(move_to_origin_))
    # Execute the command
    output = os.system(command + argument)
    #print(command + argument)

    # def delete_json_with_additionnal_GIS_attributes()
    # todo

def set_default_value_for_simulation_folder():
    global path_folder_simulation_
    if path_folder_simulation_ is None:
        path_folder_simulation_ = os.path.join(path_tool, "Simulation_temp")
set_default_value_for_simulation_folder()

def save_elog_file():
    path_log_file = os.path.join(path_folder_simulation_, "out.txt")
save_elog_file()

def Extract_log():
    if os.path.isfile(path_log_file):
        out = clean_log_for_out(path_log_file)
        for line in out:
            print(line)
Extract_log()

def update_hbjson_envelops_path():
    path_hb_model_envelop_json = os.path.join(path_folder_simulation_, "buildings_envelops.hbjson")
update_hbjson_envelops_path()