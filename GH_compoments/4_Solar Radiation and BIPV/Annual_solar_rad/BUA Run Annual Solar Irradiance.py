"""Run the annual solar irradiance simulation
    Inputs:
        path_simulation_folder_: Path to the folder. Default = Appdata\Local\Building_urban_analysis\Simulation_temp
        building_id_list_: list of ints: list of buildings we want to run the simulation on. If None, all the target
         buildings will be simulated
        _path_epw_weather_file: Path to the weather file. Default = todo
        _north_: A number between -360 and 360 for the counterclockwise
            difference between the North and the positive Y-axis in degrees.
            90 is West and 270 is East. (Default: 0)
        _overwrite_: bool: True if we want to rerun the simulation for buildings that were simulated before.
                Otherwise they will be skipped and speed up the computation. (Default: False)
    Output:
        report: report
        path_simulation_folder_: Path to the folder."""

__author__ = "Eliewiii"
__version__ = "2023.08.21"

ghenv.Component.Name = "BUA Run Annual Solar Irradiance"
ghenv.Component.NickName = 'RunAnnualSolarIrradiance'
ghenv.Component.Message = '0.0.0'
ghenv.Component.Category = 'BUA'
ghenv.Component.SubCategory = '4 :: BIPV And Solar Radiation'
ghenv.Component.AdditionalHelpFromDocStrings = "1"

import os

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
if path_simulation_folder_ is not None and os.path.isdir(path_simulation_folder_) is False:
    raise ValueError("The simulation folder does not exist, enter a valid path")


if _run :
    # Write the command
    command = path_bat_file
    # Steps to execute
    argument = " "
    argument = argument + "--make_simulation_folder 1 " + "--create_or_load_urban_canopy_object 1 " +  "--save_urban_canopy_object_to_pickle 1 " + "--save_urban_canopy_object_to_json 1 " + "--run_annual_solar_irradiance_simulation 1 "
    # OPtionnal argument of the bat file/Python script
    if path_simulation_folder_ is not None:
        argument = argument + ' -f "{}"'.format(path_simulation_folder_)
    if building_id_list_ is not None and building_id_list_ != []:
        argument = argument + ' --building_id_list "{}"'.format(building_id_list_)
    if _path_epw_weather_file is not None and os.path.isfile(_path_epw_weather_file):
        argument = argument + ' -w "{}"'.format(_path_epw_weather_file)
    if _north_ is not None:
        argument = argument + ' --north_angle "{}"'.format(_north_)
    if _overwrite_ is not None:
        argument = argument + ' --overwrite "{}"'.format(int(_overwrite_))
    # Add the name of the component to the argument
    argument = argument + ' -c "{}"'.format(ghenv.Component.NickName)
    # Run the bat file
    output = os.system(command + argument)

# set default value for the simulation folder if not provided
if path_simulation_folder_ is None:
    path_simulation_folder_ = os.path.join(path_tool, "Simulation_temp")

# Read the log file
report = read_logs(path_simulation_folder_)


