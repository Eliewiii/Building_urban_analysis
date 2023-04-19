from building.utils_building import *

local_appdata = os.environ['LOCALAPPDATA']
path_tool_temp_folder = os.path.join(local_appdata, "Building_urban_analysis","Simulation_temp")


for f in os.listdir(path_tool_temp_folder):
    os.remove(os.path.join(path_tool_temp_folder, f))