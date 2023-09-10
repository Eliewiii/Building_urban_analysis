"""Generate mesh on buildings for BIPV simulation
    Inputs:
        path_simulation_folder_: Path to the folder. Default = Appdata\Local\Building_urban_analysis\Simulation_temp
        building_id_list_: list of ints: list of buildings we want to run the simulation on
        _roof_bipv: bool : True if we want to run the simulation on the roof
        _facade_bipv: bool : True if we want to run the simulation on the facade
        _roof_grid_size_x_: float : Number for the distance to move points from the surfaces of the geometry of the model.
                    Default = 1.5
        _roof_grid_size_y_: float : Number for the distance to move points from the surfaces of the geometry of the model.
                    Default = 1.5
        _facade_grid_size_x_: float : Number for the distance to move points from the surfaces of the geometry of the model.
                    Default = 1.5
        _facade_grid_size_y_: float : Number for the distance to move points from the surfaces of the geometry of the model.
                    Default = 1.5
        _offset_dist_: float:  Number for the distance to move points from the surfaces of the geometry of the model.
                    Typically, this should be a small positive number to ensure points are not blocked by the mesh.
                    Default = 0.1
        merge_building_faces_: bool: True if the mesh should be generated on a geometry with merged faces,
                    especially to ignore the subdivisions of floors and apartment.
                    Default = False
        _run: Plug in a button to run the component
    Output:
        report: report
        path_simulation_folder_: Path to the folder."""

__author__ = "Eliewiii"
__version__ = "2023.08.21"

ghenv.Component.Name = "BUA Generate Mesh For BIPV"
ghenv.Component.NickName = 'GenerateMeshForBIPV'
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

if _run and (_roof_bipv or _facade_bipv):

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
    if _facade_bipv:
        argument = argument + " --on_facade 1 "
    if _roof_grid_size_x_ is not None:
        argument = argument + " --roof_grid_size_x {}".format(_roof_grid_size_x_)
    if _roof_grid_size_y_ is not None:
        argument = argument + " --roof_grid_size_y {}".format(_roof_grid_size_y_)
    if _facade_grid_size_x_ is not None:
        argument = argument + " --facade_grid_size_x {}".format(_facade_grid_size_x_)
    if _facade_grid_size_y_ is not None:
        argument = argument + " --facade_grid_size_y {}".format(_facade_grid_size_y_)
    if _offset_dist_ is not None:
        argument = argument + " --offset_dist {}".format(_offset_dist_)
    if merge_building_faces_:
        argument = argument + " --make_merged_faces_hb_model 1"

    # Add the name of the component to the argument
    argument = argument + " -c {}".format(ghenv.Component.NickName)
    # Run the bat file
    output = os.system(command + argument)

# set default value for the simulation folder if not provided
if path_simulation_folder_ is None:
    path_simulation_folder_ = os.path.join(path_tool, "Simulation_temp")

report = read_logs(path_simulation_folder_)

