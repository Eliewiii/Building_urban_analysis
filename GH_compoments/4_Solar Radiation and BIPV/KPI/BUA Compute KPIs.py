""" Compute the KPIs of the simulated buildings.
    Inputs:
        path_simulation_folder_: Path to the folder. Default = Appdata\Local\Building_urban_analysis\Simulation_temp
        building_id_list_: list of buildings we want to run the simulation on. If set to None, it will be run on the
        buildings to simulate.
        _bipv_simulation_identifier_: Identifier of the simulation that should be simulated. The results of each
            simulation saved in a separate folder. (Default = "new_uc_scenario")
        _grid_parameters
        _run: Plug in a button to run the component
    Output:
        report: logs
        path_simulation_folder_: Path to the folder.
        path_idf_list: list of paths to the idf files of the simulated buildings
        path_sql_list: list of paths to the sql results files of the simulated buildings
        """


__author__ = "elie-medioni"
__version__ = "2024.31.03"

ghenv.Component.Name = "BUA Run UBES with Openstudio"
ghenv.Component.NickName = 'RunUBESwithOpenstudio'
ghenv.Component.Message = '0.0.0'
ghenv.Component.Category = 'BUA'
ghenv.Component.SubCategory = '5 :: Energy Simulation'
ghenv.Component.AdditionalHelpFromDocStrings = "1"


import os
import json

from honeybee_energy.simulation.parameter import SimulationParameter

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


# Check path_simulation_folder_
if path_simulation_folder_ is not None and os.path.isdir(path_simulation_folder_) is False:
    raise ValueError("The simulation folder does not exist, enter a valid path")

# Get Appdata\local folder
local_appdata = os.environ['LOCALAPPDATA']
path_tool = os.path.join(local_appdata, "Building_urban_analysis")
name_temporary_files_folder = "temporary_files"
path_bat_file = os.path.join(path_tool, "Scripts", "mains_tool", "run_BUA.bat")


# Check _bipv_parameters
if _bipv_parameters is not None:
    try:  # try to load the json
        bipv_parameters_dict = json.loads(_bipv_parameters)



if _run:
    # Convert the simulation parameters to hbjson if it is not already
    if isinstance(_hb_simulation_parameters, SimulationParameter):
        _hb_simulation_parameters.to_dict(path_hbjson_simulation_parameter_file)
    # Write the command
    command = path_bat_file
    # Steps to execute
    argument = " "
    argument = argument + "--make_simulation_folder 1 " + "--create_or_load_urban_canopy_object 1 " + "--save_urban_canopy_object_to_pickle 1 " + "--save_urban_canopy_object_to_json 1 " + "--run_ubes_with_openstudio 1 "
    # OPtionnal argument of the bat file/Python script
    if path_simulation_folder_ is not None:
        argument = argument + ' -f "{}"'.format(path_simulation_folder_)
    if building_id_list_ is not None and building_id_list_ != []:
        argument = argument + ' --building_id_list "{}"'.format(building_id_list_)
    if _path_weather_file is not None:
        argument = argument + ' --path_weather_file "{}"'.format(_path_weather_file)
    if path_ddy_file_ is not None:
        argument = argument + ' --ddy_file "{}"'.format(ddy_file_)
    if _hb_simulation_parameters is not None:
        argument = argument + ' --path_hbjson_simulation_parameters "{}"'.format(path_hbjson_simulation_parameter_file)
    if _cop_cooling_ is not None:
        argument = argument + " --cop_cooling {}".format(float(_cop_cooling_))
    if _cop_heating_ is not None:
        argument = argument + " --cop_heating {}".format(float(_cop_heating_))
    if _overwrite_ is not None:
        argument = argument + " --overwrite {}".format(int(_overwrite_))
    else:
        argument = argument + " --overwrite 1"
    if run_in_parallel_ is not None:
        argument = argument + " --run_in_parallel {}".format(int(_run_in_parallel_))

    # Add the name of the component to the argument
    argument = argument + " -c {}".format(ghenv.Component.NickName)
    # Run the bat file
    output = os.system(command + argument)

# set default value for the simulation folder if not provided
if path_simulation_folder_ is None:
    path_simulation_folder_ = os.path.join(path_tool, "Simulation_temp")

# Read the log file
report = read_logs(path_simulation_folder_)