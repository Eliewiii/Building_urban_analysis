"""Plot the buildings inside the Urban Canopy.
    Inputs:
        path_simulation_folder_: Path to the folder. By default, the code will be run in
                                Appdata\Local\Building_urban_analysis\Simulation_temp
        building_id_list_: List of building ids to display. If empty, all the buildings will be displayed.
        _run : True if we want to run the code
    Output:
        target_building_modeled_envelopes : Brep of the envelopes of the target BuildingModeled
        non_target_building_modeled_envelopes : Brep of the envelopes of the non-target BuildingModeled
        building_basic_envelopes : Brep of the envelopes of the BuildingBasic
        building_hb_rooms : list of the HB rooms of representing the envelopes of buildings, can be used
            to display the ids of the buildings
"""

__author__ = "Elie"
__version__ = "2024.05.05"

ghenv.Component.Name = "BUA Load Building Envelopes"
ghenv.Component.NickName = 'LoadBuildingEnvelopes'
ghenv.Component.Message = '1.1.0'
ghenv.Component.Category = 'BUA'
ghenv.Component.SubCategory = '2 :: Information'

import json
import os

from honeybee.room import Room

from ladybug_rhino.fromgeometry import from_polyface3d


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

    with open(path_json, "r") as f:
        urban_canopy_dict = json.load(f)

    # Get the list of the building ids to display
    if building_id_list_ == [] or building_id_list_ is None:
        building_id_list_ = list(urban_canopy_dict["buildings"].keys())
    else:  # Check if the building ids are in the json file
        for building_id in building_id_list_:
            try:
                urban_canopy_dict["buildings"][building_id]
            except KeyError:
                raise KeyError("Building with ID '{}' not found in the dictionary.".format(building_id))

    # Initialize the lists
    target_building_modeled_id_list = []
    non_target_building_modeled_id_list = []
    building_basic_id_list = []

    # Get the list of the target, simulated and context buildings
    for building_id in building_id_list_:
        if urban_canopy_dict["buildings"][building_id]["type"] == "BuildingModeled":
            if urban_canopy_dict["buildings"][building_id]["is_target_building"] == True:
                target_building_modeled_id_list.append(building_id)
            else :
                non_target_building_modeled_id_list.append(building_id)
        else:
            building_basic_id_list.append(building_id)

    target_building_modeled_envelopes = []
    non_target_building_modeled_envelopes = []
    building_basic_envelopes = []

    building_hb_rooms = [Room.from_dict(urban_canopy_dict["buildings"][building_id]["hb_room_envelope"]) for
                         building_id in building_id_list_]

    for building_id in target_building_modeled_id_list:
        building_hb_room_envelopes = Room.from_dict(
            urban_canopy_dict["buildings"][building_id]["hb_room_envelope"])
        target_building_modeled_envelopes.append(from_polyface3d(building_hb_room_envelopes.geometry))
    for building_id in non_target_building_modeled_id_list:
        building_hb_room_envelopes = Room.from_dict(
            urban_canopy_dict["buildings"][building_id]["hb_room_envelope"])
        non_target_building_modeled_envelopes.append(from_polyface3d(building_hb_room_envelopes.geometry))
    for building_id in building_basic_id_list:
        building_hb_room_envelopes = Room.from_dict(
            urban_canopy_dict["buildings"][building_id]["hb_room_envelope"])
        building_basic_envelopes.append(from_polyface3d(building_hb_room_envelopes.geometry))

if not os.path.isfile(path_json):
    print("the json file of the urban canopy does not exist")
