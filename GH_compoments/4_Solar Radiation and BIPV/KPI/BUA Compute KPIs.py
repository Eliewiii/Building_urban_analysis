""" Compute the KPIs of the urban canopy scenario based on the results of the UBES and BIPV simulations.
    Inputs:
        path_simulation_folder_: Path to the folder. Default = Appdata\Local\Building_urban_analysis\Simulation_temp
        _bipv_simulation_identifier_: Identifier of the simulation that should be simulated. The results of each
            simulation saved in a separate folder. (Default = "new_uc_scenario")
        _electricity_grid_parameters : Parameters of the electricity grid. to be defined from the ElectricityGridParameters component.
        zone_area_: Area in m2 of the terrain the urban canopy/group of buildings is built on, to compute the KPIs per
            m2 of land use. (Optional)
        _run: Plug in a button to run the component
    Output:
        report: logs
        path_simulation_folder_: Path to the folder.
        """

__author__ = "elie-medioni"
__version__ = "2024.04.01"

ghenv.Component.Name = "BUA Compute KPIs"
ghenv.Component.NickName = 'ComputeKPIs'
ghenv.Component.Message = '0.0.0'
ghenv.Component.Category = 'BUA'
ghenv.Component.SubCategory = '4 :: Solar Radiation and BIPV'
ghenv.Component.AdditionalHelpFromDocStrings = "1"

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


# Check path_simulation_folder_
if path_simulation_folder_ is not None and os.path.isdir(path_simulation_folder_) is False:
    raise ValueError("The simulation folder does not exist, enter a valid path")

# Get Appdata\local folder
local_appdata = os.environ['LOCALAPPDATA']
path_tool = os.path.join(local_appdata, "Building_urban_analysis")
path_bat_file = os.path.join(path_tool, "Scripts", "mains_tool", "run_BUA.bat")

# Check electricity grid parameters
if _electricity_grid_parameters is not None:
    try:  # try to load the json
        electricity_grid_parameters_dict = json.loads(_electricity_grid_parameters)
    except:
        raise ValueError(
            "The _electricity_grid_parameters input is not correct, use the Electricity Grid parameters component as input")
    if isinstance(electricity_grid_parameters_dict,
                  dict) is False or "grid_ghg_intensity" not in electricity_grid_parameters_dict.keys() or "grid_energy_intensity" not in electricity_grid_parameters_dict.keys() or "grid_electricity_sell_price" not in electricity_grid_parameters_dict.keys():
        raise ValueError(
            "The _electricity_grid_parameters input is not correct, use the Electricity Grid parameters component as input")
    else:
        grid_ghg_intensity = electricity_grid_parameters_dict["grid_ghg_intensity"]
        grid_energy_intensity = electricity_grid_parameters_dict["grid_energy_intensity"]
        grid_electricity_sell_price = electricity_grid_parameters_dict["grid_electricity_sell_price"]
else:
    grid_ghg_intensity = None
    grid_energy_intensity = None
    grid_electricity_sell_price = None

# Check the _bipv_simulation_identifier_
if _bipv_simulation_identifier_ is not None:
    # set default value for the simulation folder if not provided
    if path_simulation_folder_ is None:
        path_simulation_folder = os.path.join(path_tool, "Simulation_temp")
    else:
        path_simulation_folder = path_simulation_folder_
    # Path to the urban canopy json file
    path_uc_json = os.path.join(path_simulation_folder, "urban_canopy.json")
    if os.path.isfile(path_uc_json):
        with open(path_uc_json, 'r') as json_file:
            urban_canopy_dict = json.load(json_file)
        if _bipv_simulation_identifier_ not in urban_canopy_dict["bipv_scenarios"].keys():
            raise ValueError(
                "The simulation identifier is not valid, please check the identifier of the bipv simulation"
                "that were run with the adequate component")
    else:
        raise ValueError("The urban canopy json file does not exist, run the previous steps need to be run first")

# Check the zone_area_
if zone_area_ is not None:
    if zone_area_ <= 0:
        raise ValueError("The zone area must be greater than 0")

if _run:
    # Write the command
    command = path_bat_file
    # Steps to execute
    argument = " "
    argument = argument + "--make_simulation_folder 1 " + "--create_or_load_urban_canopy_object 1 " + "--save_urban_canopy_object_to_pickle 1 " + "--save_urban_canopy_object_to_json 1 " + "--run_kpi_simulation 1 "
    # OPtionnal argument of the bat file/Python script
    if path_simulation_folder_ is not None:
        argument = argument + ' -f "{}"'.format(path_simulation_folder_)
    if _bipv_simulation_identifier_ is not None:
        argument = argument + ' -b "{}"'.format(_bipv_simulation_identifier_)
    if grid_ghg_intensity is not None:
        argument = argument + ' --grid_ghg_intensity "{}"'.format(grid_ghg_intensity)
    if grid_energy_intensity is not None:
        argument = argument + ' --grid_energy_intensity "{}"'.format(grid_energy_intensity)
    if grid_electricity_sell_price is not None:
        argument = argument + ' --grid_electricity_sell_price "{}"'.format(grid_electricity_sell_price)
    if zone_area_ is not None:
        argument = argument + ' --zone_area "{}"'.format(zone_area_)
    # Add the name of the component to the argument
    argument = argument + " -c {}".format(ghenv.Component.NickName)
    # Run the bat file
    output = os.system(command + argument)

# set default value for the simulation folder if not provided
if path_simulation_folder_ is None:
    path_simulation_folder_ = os.path.join(path_tool, "Simulation_temp")

# Read the log file
report = read_logs(path_simulation_folder_)
