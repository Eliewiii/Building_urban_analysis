"""Get the building ids of the urban canopy
    Inputs:
        path_simulation_folder_: Path to the folder. By default, the code will be run in
                                Appdata\Local\Building_urban_analysis\Simulation_temp
        _run : True if we want to run the code
    Output:
        target_building_id_list : Brep of the envelopes of the target building
        simulation_building_id_list : Brep of the envelopes of the simulation building
        context_building_id_list : Brep of the envelopes of the context building
"""

__author__ = "Elie"
__version__ = "2023.08.21"

ghenv.Component.Name = "BUA Get Building Ids"
ghenv.Component.NickName = 'GetBuildingIds'
ghenv.Component.Message = '1.0.0'
ghenv.Component.Category = "BUA"
ghenv.Component.SubCategory = "2 :: Information"



import json
import os

def clean_path(path):
    path = path.replace("\\", "/")
    return (path)

# Get Appdata\local folder
local_appdata = os.environ['LOCALAPPDATA']
path_tool = os.path.join(local_appdata, "Building_urban_analysis")

# set default value for the simulation folder if not provided
if path_simulation_folder_ is None:
    path_simulation_folder_ = os.path.join(path_tool, "Simulation_temp")

path_json = os.path.join(path_simulation_folder_, "urban_canopy.json")

if _run and os.path.isfile(path_json):

    path_json = os.path.join(path_simulation_folder_, "urban_canopy.json")
    with open(path_json, "r") as f:
        urban_canopy_dict = json.load(f)

    target_building_id_list = []
    simulated_building_id_list = []
    context_building_id_list = []
    # Get the list of the target, simulated and context buildings
    for building_id in list(urban_canopy_dict["buildings"].keys()):
    # Get the list of the target, simulated and context buildings
        if urban_canopy_dict["buildings"][building_id]["type"] == "BuildingModeled":
            if urban_canopy_dict["buildings"][building_id]["is_target_building"] == True:
                target_building_id_list.append(building_id)
            elif urban_canopy_dict["buildings"][building_id]["is_building_to_simulate"] == True:
                simulated_building_id_list.append(building_id)
            else:
                context_building_id_list.append(building_id)
        else:
            context_building_id_list.append(building_id)


if not os.path.isfile(path_json):
    print("the json file of the urban canopy does not exist")
