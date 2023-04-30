"""Add a list of HB Models of buildings to the urban canopy building collecting.
    Inputs:
        _hb_model_list: List of Honeybee Models of buildings
        path_folder_simulation: Path to the simulation folder. By default, the code will be run in Appdata\Roaming\Building_urban_analysis\Simulation_temp
        _run: Plug in a button to run the component
    Output:
        a: The a output variable"""

import os

def clean_path(path):
    path = path.replace("\\", "/")

name_bounding_box_hbjson = "bounding_boxes.hbjson"

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
path_bat_file = os.path.join(path_tool, "Scripts", "components_gh" , "make_oriented_bounding_box", "make_oriented_bounding_box.bat")


# set default value for the simulation folder if not provided
if path_folder_simulation_ is None:
    path_folder_simulation_ = os.path.join(path_tool, "Simulation_temp")

if _run:
    # Write the command
    command = path_bat_file
    # Run the command
    output = os.system(command)
    print(command)

# path to th elog file to plot in the report
path_log_file = os.path.join(path_folder_simulation_, "out.txt")

# Extract the log if they exist
if os.path.isfile(path_log_file):
    out = clean_log_for_out(path_log_file)
    for line in out:
        print(line)

path_bounding_box_hbjson = os.path.join(path_folder_simulation_, name_bounding_box_hbjson)
