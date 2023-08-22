"""Get the values of the radiation simulation for a specific building.
    Inputs:
        path_folder_simulation_: Path to the folder. By default, the code will be run in
                                Appdata\Roaming\Building_urban_analysis\Simulation_temp
        _building_id : id of the building we are interrested in
        _run : True if we want to run the code
    Output:
        building_envelop : envelop of the HB model, to plot on GH
        values_roof : list of the annual values on the roof in kWh/m2
        mesh_roof : rhino mesh of the roof
        values_facades : list of the annual values on the facades in kWh/m2
        mesh_facades : rhino mesh of the facades"""

__author__ = "Elie"
__version__ = "2023.05.03"

import ghpythonlib.treehelpers as th

import subprocess
import json
import os
from honeybee_radiance.sensorgrid import SensorGrid
from ladybug_rhino.fromgeometry import from_mesh3d
from honeybee.room import Room
from honeybee.model import Model

# Get Appdata\local folder
local_appdata = os.environ['LOCALAPPDATA']
path_tool = os.path.join(local_appdata, "Building_urban_analysis")

# set default value for the simulation folder if not provided
if path_folder_simulation_ is None:
    path_folder_simulation_ = os.path.join(path_tool, "Simulation_temp")


def get_values_in_list(path):
    with open(path, "r") as f:
        data_values = f.read()
        data_values_in_string = data_values.split(",")
        values_in_list = list(map(float, data_values_in_string))
        values_in_list = [i / 1000 for i in values_in_list]
    return values_in_list


def get_rhino_mesh_from_sensor_grid(sensor_grid_dict):
    sensor_grid = SensorGrid.from_dict(sensor_grid_dict)
    mesh = sensor_grid.mesh
    mesh_rhino = from_mesh3d(mesh)
    return mesh_rhino

path_json = os.path.join(path_folder_simulation_, "urban_canopy.json")

if _run and os.path.isfile(path_json):

    path_json = os.path.join(path_folder_simulation_, "urban_canopy.json")
    with open(path_json, "r") as f:
        urban_canopy_dict = json.load(f)
    if _building_id_list == ["all"]:
        _building_id_list = []
        for id in list(urban_canopy_dict["buildings"].keys()):
            if urban_canopy_dict["buildings"][id]["Is_target_building"] == True:
                _building_id_list.append(id)
    print(_building_id_list)

    hb_model_list=[]
    values_roof_list=[]
    mesh_roof_list=[]
    values_facade_list=[]
    mesh_facade_list =[]

    for building_id in _building_id_list:
        path_building = os.path.join(path_folder_simulation_, building_id)
        building_envelop_dict = urban_canopy_dict["buildings"][building_id]["HB_room_envelop"]
        building_envelop = Room.from_dict(building_envelop_dict)

        hb_model_list.append(Model.from_dict(urban_canopy_dict["buildings"][building_id]["HB_model"]))

        # for the roof
        path_values_roof = os.path.join(path_folder_simulation_,"Radiation Simulation",building_id,"Roof", 'annual_radiation_values.txt')
        values_roof_list.append(get_values_in_list(path_values_roof))
        sensor_grid_dict_roof = urban_canopy_dict["buildings"][building_id]["Solar_radiation"]["Sensor_grids_dict"]["Roof"]
        mesh_roof_list.append(get_rhino_mesh_from_sensor_grid(sensor_grid_dict_roof))

        # for the facades
        path_values_facades = os.path.join(path_folder_simulation_,"Radiation Simulation",building_id,"Facades", 'annual_radiation_values.txt')
        values_facade_list.append(get_values_in_list(path_values_facades))
        sensor_grid_dict_facades = urban_canopy_dict["buildings"][building_id]["Solar_radiation"]["Sensor_grids_dict"]["Facades"]
        mesh_facade_list.append(get_rhino_mesh_from_sensor_grid(sensor_grid_dict_facades))

    values_roof_tree= th.list_to_tree(values_roof_list)
    mesh_roof_tree= th.list_to_tree(mesh_roof_list)
    values_facade_tree=th.list_to_tree(values_facade_list)
    mesh_facade_tree =th.list_to_tree(mesh_facade_list)

if not os.path.isfile(path_json):
    print("the json file of the urban canopy does not exist")
