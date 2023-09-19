"""Run the BIPV simulation for the selected buildings.
    Inputs:
        path_simulation_folder_: Path to the simulation folder.
            (Default = user\appdata\Local\Building_urban_analysis\Simulation_temp)
        building_id_list_: list of the identifier of the buildings that should be simulated. The buildings
            need to be target buildings to be simulated (Default = "all")
        _bipv_simulation_identifier: Identifier of the simulation that should be simulated. The results of each
            simulation saved in a separate folder. (Default = "new_uc_scenario")
        _bipv_parameters : Parameters of the BIPV simulation. to be defined from the BIPVParameters component.
        _replacement_scenario_parameters: Parameters of the replacement scenario. to be defined from the
            ReplacementScenarioParameters component.
        _start_year: Year from which the simulation should start. (Default: current year)
        _end_year: Year from which the simulation should end. (Default: current year+50)
        _run: Plug in a button to run the component
    Output:
        report: report
        path_simulation_folder_: Path to the folder."""

__author__ = "Eliewiii"
__version__ = "2023.08.21"

ghenv.Component.Name = "BUA Run BIPV Simulation"
ghenv.Component.NickName = 'RunBIPVSimulation'
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

# if _run and (_roof_bipv or _facades_bipv):
#
#     # Write the command
#     command = path_bat_file
#     # Steps to execute
#     argument = " "
#     argument = argument + "--make_simulation_folder 1 " + "--create_or_load_urban_canopy_object 1 " + "--save_urban_canopy_object_to_pickle 1 " + "--save_urban_canopy_object_to_json 1 " + "--generate_sensorgrid 1 "
#     # OPtionnal argument of the bat file/Python script
#     if path_simulation_folder_ is not None:
#         argument = argument + ' -f "{}"'.format(path_simulation_folder_)
#     if building_id_list_ is not None and building_id_list_ != []:
#         argument = argument + ' --building_id_list "{}"'.format(building_id_list_)
#     if _roof_bipv:
#         argument = argument + " --on_roof 1 "
#     if _facades_bipv:
#         argument = argument + " --on_facades 1 "
#     if _roof_grid_size_x_ is not None:
#         argument = argument + " --roof_grid_size_x {}".format(_roof_grid_size_x_)
#     if _roof_grid_size_y_ is not None:
#         argument = argument + " --roof_grid_size_y {}".format(_roof_grid_size_y_)
#     if _facades_grid_size_x_ is not None:
#         argument = argument + " --facades_grid_size_x {}".format(_facades_grid_size_x_)
#     if _facades_grid_size_y_ is not None:
#         argument = argument + " --facades_grid_size_y {}".format(_facades_grid_size_y_)
#     if _offset_dist_ is not None:
#         argument = argument + " --offset_dist {}".format(_offset_dist_)
#     if merge_building_faces_:
#         argument = argument + " --make_merged_faces_hb_model 1"
#
#     # Add the name of the component to the argument
#     argument = argument + " -c {}".format(ghenv.Component.NickName)
#     # Run the bat file
#     output = os.system(command + argument)

# set default value for the simulation folder if not provided
if path_simulation_folder_ is None:
    path_simulation_folder_ = os.path.join(path_tool, "Simulation_temp")

report = read_logs(path_simulation_folder_)
