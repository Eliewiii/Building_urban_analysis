"""Get the values of the radiation simulation for a specific building.
    Inputs:
        path_simulation_folder_: Path to the folder. By default, the code will be run in
                                Appdata\Local\Building_urban_analysis\Simulation_temp
        _run : True if we want to run the code
    Output:
        target_building_envelopes : Brep of the envelopee of the target building
        simulation_building_envelopes : Brep of the envelopee of the simulation building
        context_building_envelopes : Brep of the envelopee of the context building
        building_hb_rooms : list of the HB rooms of representing the envelopes of buildings, can be used
            to display the ids of the buildings
"""

__author__ = "Elie"
__version__ = "2023.05.03"

import ghpythonlib.treehelpers as th

import subprocess
import json
import os

from honeybee.room import Room
from honeybee.model import Model

from ladybug_rhino.fromgeometry import from_polyface3d

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

    for id in list(urban_canopy_dict["buildings"].keys()):
        if urban_canopy_dict["buildings"][id]["is_target_building"] == True:
            target_building_id_list.append(id)
        elif urban_canopy_dict["buildings"][id]["is_building_to_simulate"] == True:
            simulated_building_id_list.append(id)
        else:
            context_building_id_list.append(id)

    target_building_envelopes = []
    simulation_building_envelopes = []
    context_building_envelopes = []
    # todo : fast way, to check if it works
    # target_building_envelopes = [from_polyface3d(
    #     Room.from_dict(urban_canopy_dict["building"][building_id]["hb_room_envelope"]).geometry) for
    #                              building_id in
    #                              urban_canopy_dict["list_of_building_ids"] if
    #                              urban_canopy_dict["building"][building_id]["is_target_building"]]
    # simulation_building_envelopes = [from_polyface3d(
    #     Room.from_dict(urban_canopy_dict["building"][building_id]["hb_room_envelope"]).geometry) for
    #                                  building_id in
    #                                  urban_canopy_dict["list_of_building_ids"] if
    #                                  urban_canopy_dict["building"][building_id][
    #                                      "is_building_to_simulate"] and not
    #                                  urban_canopy_dict["building"][building_id]["is_target_building"]]
    # context_building_envelopes = [from_polyface3d(
    #     Room.from_dict(urban_canopy_dict["building"][building_id]["hb_room_envelope"]).geometry) for
    #                               building_id in
    #                               urban_canopy_dict["list_of_building_ids"] if
    #                               not urban_canopy_dict["building"][building_id]["is_target_building"] and not
    #                               urban_canopy_dict["building"][building_id]["is_building_to_simulate"]]

    building_hb_rooms = [Room.from_dict(urban_canopy_dict["building"][building_id]["hb_room_envelope"]) for
                         building_id in
                         urban_canopy_dict["list_of_building_ids"]]

    for building_id in target_building_id_list:
        building_hb_room_envelop = Room.from_dict(
            urban_canopy_dict["buildings"][building_id]["hb_room_envelope"])
        target_building_envelopes.append(from_polyface3d(building_hb_room_envelop.geometry))
    for building_id in simulated_building_id_list:
        building_hb_room_envelop = Room.from_dict(
            urban_canopy_dict["buildings"][building_id]["hb_room_envelope"])
        simulation_building_envelopes.append(from_polyface3d(building_hb_room_envelop.geometry))
    for building_id in context_building_id_list:
        building_hb_room_envelop = Room.from_dict(
            urban_canopy_dict["buildings"][building_id]["hb_room_envelope"])
        context_building_envelopes.append(from_polyface3d(building_hb_room_envelop.geometry))

if not os.path.isfile(path_json):
    print("the json file of the urban canopy does not exist")
