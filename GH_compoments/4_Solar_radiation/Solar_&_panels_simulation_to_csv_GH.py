"""Run a solar radiation simulation for all the buildings in the urban canopy that are targeted
    Inputs:
        building_id_list : list of buildings we want to run the simulation on
        path_folder_simulation_: Path to the folder. By default, the code will be run in
                                Appdata\Roaming\Building_urban_analysis\Simulation_temp
        _path_weather_file : Path to the weather file.
        _grid_size_ : Number for the distance to move points from the surfaces of the geometry of the model
        _offset_dist_ :  Number for the distance to move points from the surfaces of the geometry of the model.
        Typically, this should be a small positive number to ensure points are not blocked by the mesh.
        on_roof_ : True if the the simulation is to be run on the roof, else False (Default = True)
        on_facades_ : True if the the simulation is to be run on the facades, else False (Default = True)
        _run: Plug in a button to run the component
    Output:
        a: The a output variable"""

import os
import json


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

path_bat_file = os.path.join(path_tool, "Scripts", "mains_tool", "run_BUA.bat")

if _run:

    # Write the command
    command = path_bat_file
    # argument =" -t 1"
    argument = " "
    # Steps to execute
    argument = argument + "--make_simulation_folder 1 " + "--create_or_load_urban_canopy_object 1 " + "--save_urban_canopy_object_to_pickle 1 " + "--save_urban_canopy_object_to_json 1 " + "--generate_model_with_building_envelop 1 " + "--do_radiation_simulation 1 " + "--do_panel_simulation 1 " + "--generate_panels_results_in_csv 1 "
    # OPtionnal argument of the bat file/Python script
    if path_folder_simulation_ is not None:
        argument = argument + ' -f "{}"'.format(path_folder_simulation_)
    if _path_weather_file_ is not None:
        argument = argument + ' -w "{}""'.format(_path_weather_file_)
    if building_id_list_ is not None:
        argument = argument + ' --building_id_list "{}"'.format(building_id_list_)
    if grid_size_ is not None:
        argument = argument + ' --grid_size "{}"'.format(grid_size_)
    if offset_dist_ is not None:
        argument = argument + ' --offset_dist "{}"'.format(offset_dist_)
    if on_roof_ is not None:
        argument = argument + ' --on_roof "{}"'.format(on_roof_)
    if on_facades_ is not None:
        argument = argument + ' --on_facades "{}"'.format(on_facades_)
    if path_pv_tech_dictionary_ is not None:
        argument = argument + ' --path_pv_tech_dictionary "{}"'.format(path_pv_tech_dictionary_)
    if _id_pv_tech_roof_ is not None:
        argument = argument + ' --id_pv_tech_roof "{}"'.format(_id_pv_tech_roof_)
    if _id_pv_tech_facades_ is not None:
        argument = argument + ' --id_pv_tech_facades "{}"'.format(_id_pv_tech_facades_)
    if study_duration_years_ is not None:
        argument = argument + ' --study_duration_years "{}"'.format(study_duration_years_)
    if _replacement_scenario_ is not None:
        argument = argument + ' --replacement_scenario "{}"'.format(_replacement_scenario_)
    if every_X_years_ is not None:
        argument = argument + ' --every_X_years_ "{}"'.format(every_X_years_)

        # Execute the command
    output = os.system(command + argument)
    print(command + argument)

    # delete json file with the additionnal GIS attributes
    # todo

# set default value for the simulation folder if not provided
if path_folder_simulation_ is None:
    path_folder_simulation_ = os.path.join(path_tool, "Simulation_temp")

# path to th elog file to plot in the report
path_log_file = os.path.join(path_folder_simulation_, "out.txt")

# Extract the log if they exist
if os.path.isfile(path_log_file):
    out = clean_log_for_out(path_log_file)
    for line in out:
        print(line)

