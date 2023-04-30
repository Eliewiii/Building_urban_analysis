"""Get the list of the buildings' ids
    Inputs:
        path_folder_ : Path to the folder. By default, the code will be run in Appdata\Roaming\Building_urban_analysis\Simulation_temp
    Output:
        a: list of ids"""

import os


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


# Get Appdata\local folder
local_appdata = os.environ['LOCALAPPDATA']
path_tool = os.path.join(local_appdata, "Building_urban_analysis")

path_get_id_buildings_bat = os.path.join(path_tool, "Scripts", "components_gh", "get_id_buildings",
                                         "get_id_buildings.bat")

if _run:
    # Write the command
    command = path_get_id_buildings_bat
    # argument =" -t 1"
    argument = " "
    # Optionnal argument of the bat file/Python script
    if path_folder_ is not None:
        argument = argument + ' -f "{}"'.format(path_folder_)
    # Execute the command
    output = os.system(command + argument)
    print(command + argument)

# set default value for the simulation folder if not provided
if path_folder_ is None:
    path_folder_simulation_ = os.path.join(path_tool, "Simulation_temp")

# path to the log file to plot in the report
path_log_file = os.path.join(path_folder_, "out.txt")

# Extract the log if they exist
if os.path.isfile(path_log_file):
    out = clean_log_for_out(path_log_file)
    for line in out:
        print(line)


