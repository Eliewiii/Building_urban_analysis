"""Run a solar radiation simulation for all the buildings in the urban canopy that are targeted
    Inputs:
        _path_folder: Path to the folder. By default, the code will be run in Appdata\Roaming\Building_urban_analysis\Simulation_temp
        _name: Name of the simulation folder. By default, it will be "Radiation Simulation"
        _path_weather_file : Path to the weather file.
        _grid_size_ : Number for the distance to move points from the surfaces of the geometry of the model
        _offset_dist_ :  Number for the distance to move points from the surfaces of the geometry of the model.
        Typically, this should be a small positive number to ensure points are not blocked by the mesh.
        _run: Plug in a button to run the component
    Output:
        a: The a output variable"""





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

path_run_solar_radiation_bat = os.path.join(path_tool, "Scripts", "components_gh", "compute_solar_radiation",
                                            "run_solar_radiation.bat")

if _run:
    # Write the command
    command = path_run_solar_radiation_bat
    # argument =" -t 1"
    argument = " "
    # Optionnal argument of the bat file/Python script
    if path_folder_simulation_ is not None:
        argument = argument + ' -f "{}"'.format(path_folder_simulation_)
    if path_weather_file_ is not None:
        argument = argument + ' -d "{}"'.format(path_weather_file_)
    # Execute the command
    output = os.system(command + argument)
    print(command + argument)


# set default value for the simulation folder if not provided
if path_folder_simulation_ is None:
    path_folder_simulation_ = os.path.join(path_tool, "Simulation_temp")

# path to the log file to plot in the report
path_log_file = os.path.join(path_folder_simulation_, "out.txt")

# Extract the log if they exist
if os.path.isfile(path_log_file):
    out = clean_log_for_out(path_log_file)
    for line in out:
        print(line)

# output the path to the hbjson_envelops
path_hb_model_envelop_json = os.path.join(path_folder_simulation_, "buildings_envelops.hbjson")