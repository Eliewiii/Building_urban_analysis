""" Run the Energy simulation with Openstudio and EnergyPlus at the urban scale.
    Inputs:
        path_simulation_folder_: Path to the folder. Default = Appdata\Local\Building_urban_analysis\Simulation_temp
        building_id_list_: list of buildings we want to run the simulation on. If set to None, it will be run on the
        buildings to simulate.
        _path_weather_file: Path to the epw or wea (not sure wea compatible) weather file. Default =
        path_ddy_file_: Path to the ddy file. If no file is provided the design days will be set automatically by Honeybee
         Default = None
        _hb_simulation_parameters : Honeybee simulation parameter object from the Honeybee parameter or a path to
        a Honeybee parameter hbjson file.
        _cop_cooling_: float: Coefficient of performance of the cooling system. Default = 3.
        _cop_heating_: float: Coefficient of performance of the heating system. Default = 3.
        _overwrite_: Set to True if the existing simulation should be overwritten. (Default: True)
        run_in_parallel_: bool: True if the simulations should be run in parallel. (not implemented yet) (Default: False)
        _run: Plug in a button to run the component
    Output:
        report: logs
"""


__author__ = "elie-medioni"
__version__ = "2024.05.28"

ghenv.Component.Name = "BUA Run UBES with Openstudio"
ghenv.Component.NickName = 'RunUBESwithOpenstudio'
ghenv.Component.Message = '1.2.0'
ghenv.Component.Category = 'BUA'
ghenv.Component.SubCategory = '5 :: Energy Simulation'

import rhinoscriptsyntax as rs
def get_rhino_version():
    return rs.ExeVersion()
rhino_version = get_rhino_version()
if rhino_version > 7:
    import ghpythonlib as ghlib
    c = ghlib.component._get_active_component()
    c.ToggleObsolete(False)

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
path_bat_file = os.path.join(path_tool, "Scripts","bua", "mains_tool", "run_BUA.bat")

# Check the Honeybee simulation parameters
if _hb_simulation_parameters is None:
    # Don't do anything, the default simulation parameters will be used
    pass
elif isinstance(_hb_simulation_parameters,SimulationParameter):
    if path_simulation_folder_ is None:
        path_simulation_folder = os.path.join(path_tool, "Simulation_temp")
    # Save the simulation parameter to a file
    path_hbjson_simulation_parameter_file = os.path.join(path_simulation_folder,name_temporary_files_folder, "simulation_parameters.json")
elif isinstance(_hb_simulation_parameters,str) :
    # Check if the file exists
    if not os.path.isfile(_hb_simulation_parameters):
        raise FileNotFoundError("The simulation parameter file inputed does not exist.")
    # Check if the file contains a valid Honeybee simulation parameters object
    try:
        with open(_hb_simulation_parameters, 'r') as f:
            json_dic = json.load(f)
        SimulationParameter.from_dict(json_dic)
    except:
        raise ValueError("The simulation parameter file is not valid, it cannot be loaded.")

    path_hbjson_simulation_parameter_file = _hb_simulation_parameters
else:
    raise ValueError("The simulation parameter is not valid. Please input the path to a Honeybee simulation parameter file or a Honeybee simulation parameter object")

# Check if the weather file exists
if _path_weather_file is not None and not os.path.isfile(_path_weather_file):
    raise FileNotFoundError("The weather file does not exist, enter a valid path")
# Check if the ddy file exists
if path_ddy_file_ is not None and not os.path.isfile(path_ddy_file_):
    raise FileNotFoundError("The ddy file does not exist, enter a valid path")

# Check the COPs
if (_cop_cooling_ is not None and _cop_cooling_ <= 0) or (_cop_heating_ is not None and _cop_heating_ <= 0):
    raise ValueError("The COP should be greater than 0")

# Set _overwrite_ to True if it is not provided
if _overwrite_ is None:
    _overwrite_ = True

if _run:
    # Convert the simulation parameters to hbjson if it is not already
    print(type(_hb_simulation_parameters))
    if isinstance(_hb_simulation_parameters, SimulationParameter):
        hb_simulation_parameters_dict = _hb_simulation_parameters.to_dict()
        with open(path_hbjson_simulation_parameter_file,"w") as json_file:
            json.dump(hb_simulation_parameters_dict,json_file)
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
        argument = argument + ' --path_hbjson_simulation_parameters_file "{}"'.format(path_hbjson_simulation_parameter_file)
    if _cop_cooling_ is not None:
        argument = argument + " --cop_cooling {}".format(float(_cop_cooling_))
    if _cop_heating_ is not None:
        argument = argument + " --cop_heating {}".format(float(_cop_heating_))
    if _overwrite_ is not None:
        argument = argument + " --overwrite {}".format(int(_overwrite_))
    # if run_in_parallel_ is not None:
    #     argument = argument + " --run_in_parallel {}".format(int(run_in_parallel_))

    # Add the name of the component to the argument
    argument = argument + " -c {}".format(ghenv.Component.NickName)
    # Run the bat file
    output = os.system(command + argument)

# set default value for the simulation folder if not provided
if path_simulation_folder_ is None:
    path_simulation_folder_ = os.path.join(path_tool, "Simulation_temp")

# Read the log file
report = read_logs(path_simulation_folder_)