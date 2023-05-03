"""Get the values of the radiation simulation for a specific building.
    Inputs:
        path_folder_simulation_: Path to the folder. By default, the code will be run in
                                Appdata\Roaming\Building_urban_analysis\Simulation_temp
        _building_id : id of the building we are interrested in
        on_roof_ : True if the post-processing is to be done on the roof, else False (Default = True)
        on_facades_ : True ifthe post-processing is to be done on the facades, else False (Default = True)
    Output:
        values_roof : list of the annual values on the roof
        values_facades : list of the annual values on the facades"""

__author__ = "hilany"
__version__ = "2023.05.03"

import subprocess
import json
import os
from honeybee_radiance.sensorgrid import SensorGrid

if path_folder_simulation_ is None:
    path_folder_simulation = "C:\\Users\\User\AppData\Local\Building_urban_analysis\Simulation_temp"
if on_roof_ is None:
    on_roof_ = True
if on_facades_ is None:
    on_facades_ = True

path_building = os.path.join(path_folder_simulation_, _building_id)

if _building_id:
    path_json = os.path.join(path_folder_simulation_, "urban_canopy.json")
    file = open(path_json, "r")

    # Load the data
    urban_canopy_dict = json.load(file)

    if on_roof_ and on_facades_:
        path_values_roof = urban_canopy_dict["buildings"][_building_id]["path_values_roof"]
        file = open(path_values_roof, "r")
        # reading the file
        values = file.read()
        values_strings = values.split(",")
        values_roof = list(map(float, values_strings))

        sensor_grid_dict_roof = urban_canopy_dict["buildings"][_building_id]["SensorGrid_dict"]["Roof"]
        sensor_grid_roof = SensorGrid.from_dict(sensor_grid_dict_roof)
        mesh_roof = sensor_grid_roof._mesh

        path_values_facades = urban_canopy_dict["buildings"][_building_id]["path_values_facades"]
        file = open(path_values_facades, "r")
        # reading the file
        values = file.read()
        values_strings = values.split(",")
        values_facades = list(map(float, values_strings))

        sensor_grid_dict_facades = urban_canopy_dict["buildings"][_building_id]["SensorGrid_dict"]["Facades"]
        sensor_grid_facades = SensorGrid.from_dict(sensor_grid_dict_facades)
        mesh_facades = sensor_grid_facades._mesh

    if on_roof_ and not on_facades_:
        path_values_roof = urban_canopy_dict["buildings"][_building_id]["path_values_roof"]
        file = open(path_values_roof, "r")
        # reading the file
        values = file.read()
        values_strings = values.split(",")
        values_roof = list(map(float, values_strings))

        sensor_grid_dict_roof = urban_canopy_dict["buildings"][_building_id]["SensorGrid_dict"]["Roof"]
        sensor_grid_roof = SensorGrid.from_dict(sensor_grid_dict_roof)
        mesh_roof = sensor_grid_roof._mesh

    if on_facades_ and not on_roof_:
        path_values_facades = urban_canopy_dict["buildings"][_building_id]["path_values_facades"]
        file = open(path_values_facades, "r")
        # reading the file
        values = file.read()
        values_strings = values.split(",")
        values_facades = list(map(float, values_strings))

        sensor_grid_dict_facades = urban_canopy_dict["buildings"][_building_id]["SensorGrid_dict"]["Facades"]
        sensor_grid_facades = SensorGrid.from_dict(sensor_grid_dict_facades)
        mesh_facades = sensor_grid_facades._mesh