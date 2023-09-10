"""Get the values of the radiation simulation for a specific building.
    Inputs:
        path_folder_simulation_: Path to the folder. By default, the code will be run in
                                Appdata\Roaming\Building_urban_analysis\Simulation_temp
        _building_id : id of the building we are interrested in
        plot_on_roof_ : True if we want to plot the heat map on the roof, else False (Default = True)
        plot_on_facades_ : True if we want to plot the heat map on the facades, else False (Default = True)
        _run : True if we want to run the code
    Output:
        building_envelop : envelop of the HB model, to plot on GH
        values_roof : list of the annual values on the roof in kWh/m2
        mesh_roof : rhino mesh of the roof
        values_facades : list of the annual values on the facades in kWh/m2
        mesh_facades : rhino mesh of the facades"""

__author__ = "hilany"
__version__ = "2023.05.03"

import subprocess
import json
import os
from honeybee_radiance.sensorgrid import SensorGrid
from ladybug_rhino.fromgeometry import from_mesh3d

if path_folder_simulation_ is None:
    path_folder_simulation = "C:\\Users\\User\AppData\Local\Building_urban_analysis\Simulation_temp"
if plot_on_roof_ is None:
    plot_on_roof_ = True
if plot_on_facades_ is None:
    plot_on_facades_ = True

def clean_path(path):
    path = path.replace("\\", "/")
    return (path)

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


if _run:

    if _building_id:
        path_json = os.path.join(path_folder_simulation_, "urban_canopy.json")
        with open(path_json, "r") as f:
            urban_canopy_dict = json.load(f)

        path_building = os.path.join(path_folder_simulation_, _building_id)
        building_envelop_dict = urban_canopy_dict["buildings"][_building_id]["HB_model_envelop"]
        building_envelop = building_envelop_dict.from_dict()

        if plot_on_roof_ and plot_on_facades_:
            # for the roof
            path_values_roof = urban_canopy_dict["buildings"][_building_id]["path_values_roof"]
            values_roof = get_values_in_list(path_values_roof)
            sensor_grid_dict_roof = urban_canopy_dict["buildings"][_building_id]["SensorGrid_dict"]["roof"]
            mesh_roof = get_rhino_mesh_from_sensor_grid(sensor_grid_dict_roof)

            # for the facades
            path_values_facades = urban_canopy_dict["buildings"][_building_id]["path_values_facades"]
            values_facades = get_values_in_list(path_values_facades)
            sensor_grid_dict_facades = urban_canopy_dict["buildings"][_building_id]["SensorGrid_dict"]["facades"]
            mesh_facades = get_rhino_mesh_from_sensor_grid(sensor_grid_dict_roof)

        if plot_on_roof_ and not plot_on_facades_:
            path_values_roof = urban_canopy_dict["buildings"][_building_id]["path_values_roof"]
            values_roof = get_values_in_list(path_values_roof)
            sensor_grid_dict_roof = urban_canopy_dict["buildings"][_building_id]["SensorGrid_dict"]["roof"]
            mesh_roof = get_rhino_mesh_from_sensor_grid(sensor_grid_dict_roof)

        if plot_on_facades_ and not plot_on_roof_:
            path_values_facades = urban_canopy_dict["buildings"][_building_id]["path_values_facades"]
            values_facades = get_values_in_list(path_values_facades)
            sensor_grid_dict_facades = urban_canopy_dict["buildings"][_building_id]["SensorGrid_dict"]["facades"]
            mesh_facades = get_rhino_mesh_from_sensor_grid(sensor_grid_dict_roof)
