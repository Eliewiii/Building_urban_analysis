"""Generate mesh on buildings for BIPV simulation.
    Inputs:
        path_simulation_folder_: Path to the simulation folder. Default = Appdata\Local\Building_urban_analysis\Simulation_temp
        building_id_list_: list of buildings we want to run the simulation on
        _roof_bipv: bool : True if we want to run the simulation on the roof
        _facades_bipv: bool : True if we want to run the simulation on the facades
        _roof_grid_size_x_: float : Size of the grid on the x axis on the roof.
                    Default = 1.5
        _roof_grid_size_y_: float : Size of the grid on the y axis on the roof.
                    Default = 1.5
        _facades_grid_size_x_: float : Size of the grid on the x axis on the facades.
                    Default = 1.5
        _facades_grid_size_y_: float : Size of the grid on the x axis on the facades.
                    Default = 1.5
        _offset_dist_: float:  Distance between the edges of surfaces and the mesh .
                    Typically, this should be a small positive number to ensure points are not blocked by the mesh.
                    Default = 0.1
        merge_building_faces_: Set to True if a on a geometry with merged faces should be generated to ignore
            the artificial subdivisions of floors and apartment when generating the mesh. To adjust the parameters
            of the merged faces, use the component "BUA Merge Building Faces" before generating the mesh.
            Default = False
        overwrite_: bool: True if the new mesh should overwrite the previous one if it exists.
        _run: Plug in a button to run the component
    Output:
        report: logs
        path_simulation_folder_: Path to the folder."""

__author__ = "elie-medioni"
__version__ = "2024.05.07"

ghenv.Component.Name = "BUA Generate Mesh For BIPV"
ghenv.Component.NickName = 'GenerateMeshForBIPV'
ghenv.Component.Category = 'BUA'
ghenv.Component.SubCategory = '6 :: Solar Radiation and BIPV'


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

# Check path_simulation_folder_
if path_simulation_folder_ is not None and os.path.isdir(path_simulation_folder_) is False:
    raise ValueError("The simulation folder does not exist, enter a valid path")



# todo: make grid parameter and merge_building_faces_ components
# todo : check the values of the other parameters


# Get Appdata\local folder
local_appdata = os.environ['LOCALAPPDATA']
path_tool = os.path.join(local_appdata, "Building_urban_analysis")
path_bat_file = os.path.join(path_tool, "Scripts", "mains_tool", "run_BUA.bat")

if _run and (_roof_bipv or _facades_bipv):

    # Check _roof_bipv and _facades_bipv
    if (_roof_bipv is None or not _roof_bipv) and (_facades_bipv is None or not _facades_bipv):
        raise ValueError("Please select if you want to run the simulation on the roof and/or the facades")

    # Write the command
    command = path_bat_file
    # Steps to execute
    argument = " "
    argument = argument + "--make_simulation_folder 1 " + "--create_or_load_urban_canopy_object 1 " +  "--save_urban_canopy_object_to_pickle 1 " + "--save_urban_canopy_object_to_json 1 " + "--generate_sensorgrid 1 "
    # OPtionnal argument of the bat file/Python script
    if path_simulation_folder_ is not None:
        argument = argument + ' -f "{}"'.format(path_simulation_folder_)
    if building_id_list_ is not None and building_id_list_ != []:
        argument = argument + ' --building_id_list "{}"'.format(building_id_list_)
    if _roof_bipv:
        argument = argument + " --on_roof 1 "
    if _facades_bipv:
        argument = argument + " --on_facades 1 "
    if _roof_grid_size_x_ is not None:
        argument = argument + " --roof_grid_size_x {}".format(_roof_grid_size_x_)
    if _roof_grid_size_y_ is not None:
        argument = argument + " --roof_grid_size_y {}".format(_roof_grid_size_y_)
    if _facades_grid_size_x_ is not None:
        argument = argument + " --facades_grid_size_x {}".format(_facades_grid_size_x_)
    if _facades_grid_size_y_ is not None:
        argument = argument + " --facades_grid_size_y {}".format(_facades_grid_size_y_)
    if _offset_dist_ is not None:
        argument = argument + " --offset_dist {}".format(_offset_dist_)
    if merge_building_faces_ is not None:
        argument = argument + " --make_merged_faces_hb_model {}".format(int(merge_building_faces_))
    if overwrite_ is not None:
        argument = argument + " --overwrite {}".format(int(overwrite_))

    # Add the name of the component to the argument
    argument = argument + " -c {}".format(ghenv.Component.NickName)
    # Run the bat file
    output = os.system(command + argument)

# set default value for the simulation folder if not provided
if path_simulation_folder_ is None:
    path_simulation_folder_ = os.path.join(path_tool, "Simulation_temp")

# Read the log file
report = read_logs(path_simulation_folder_)

