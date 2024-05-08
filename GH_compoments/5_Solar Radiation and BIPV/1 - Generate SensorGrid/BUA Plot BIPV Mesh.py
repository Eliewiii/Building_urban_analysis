"""Plot the meshes on the buildings for the BIPV simulation
    Inputs:
        path_simulation_folder_: Path to the simulation folder. Default = Appdata\Local\Building_urban_analysis\Simulation_temp
        building_id_list_: list of buildings identifiers that need to be plotted.
        If no id is inputted, it will display the mesh of all the buildings that have one.
        _run: Plug in a boolean toggle to run the component
    Output:
        report: report
        path_simulation_folder_: Path to the folder.
        roof_hb_sensorgrid_tree: Tree of meshes for the roof
        facades_hb_sensorgrid_tree: Tree of meshes for the facades"""

__author__ = "elie-medioni"
__version__ = "2024.05.07"

ghenv.Component.Name = "BUA Plot BIPV Mesh"
ghenv.Component.NickName = 'PlotBIPVMesh'
ghenv.Component.Category = 'BUA'
ghenv.Component.SubCategory = '5 :: Solar Radiation and BIPV'

import ghpythonlib.treehelpers as th

import json
import os

from honeybee_radiance.sensorgrid import SensorGrid
from ladybug_rhino.fromgeometry import from_mesh3d

def clean_path(path):
    path = path.replace("\\", "/")
    return (path)


def get_rhino_mesh_from_sensor_grid(sensor_grid_dict):
    sensor_grid = SensorGrid.from_dict(sensor_grid_dict)
    mesh = sensor_grid.mesh
    mesh_rhino = from_mesh3d(mesh)
    return mesh_rhino


# Get Appdata\local folder
local_appdata = os.environ['LOCALAPPDATA']
path_tool = os.path.join(local_appdata, "Building_urban_analysis")

# Check path_simulation_folder_
if path_simulation_folder_ is None:
    path_simulation_folder_ = os.path.join(path_tool, "Simulation_temp")
elif os.path.isdir(path_simulation_folder_) is False:
    raise ValueError("The simulation folder does not exist, enter a valid path")

# Path to the urban canopy json file
path_json = os.path.join(path_simulation_folder_, "urban_canopy.json")

if _run:

    # Check if the urban canopy json file exists
    if not os.path.isfile(path_json):
        raise ValueError(
            "The urban canopy json file does not exist, buildings need to be loaded before running the context selection.")
    # Read the json file
    with open(path_json, 'r') as json_file:
        urban_canopy_dict = json.load(json_file)

    # Get the list of the building ids to display
    if building_id_list_ == [] or building_id_list_ is None:
        # add the id of the buildings that have been run if no list is provided
        building_id_list_ = [building_id for building_id in urban_canopy_dict["buildings"].keys() if
                             (urban_canopy_dict["buildings"][building_id]["type"] == "BuildingModeled" and
                              (urban_canopy_dict["buildings"][building_id]["solar_radiation_and_bipv"]["roof_sensorgrid"] is not None
                              or urban_canopy_dict["buildings"][building_id]["solar_radiation_and_bipv"]["facades_sensorgrid"] is not None))]

    else:  # Check if the building ids are in the json file
        for building_id in building_id_list_:
            try:
                urban_canopy_dict["buildings"][building_id]
            except KeyError:
                raise KeyError("Building with ID '{}' not found in the dictionary.".format(building_id))
            else:
                if not urban_canopy_dict["buildings"][building_id]["type"] == "BuildingModeled":
                    raise ValueError(
                        "Building with ID {} does not have a HB model, no mesh could have been performed on it".format(
                            building_id))
                elif (urban_canopy_dict["buildings"][building_id]["solar_radiation_and_bipv"]["roof_sensorgrid"] is None
                              and  urban_canopy_dict["buildings"][building_id]["solar_radiation_and_bipv"]["facades_sensorgrid"] is None):
                    raise ValueError("No mesh was generated for the building id {}".format(building_id))

    # Init
    mesh_roof_list = []
    mesh_facades_list = []

    for building_id in building_id_list_:
        # Roof
        if urban_canopy_dict["buildings"][building_id]["solar_radiation_and_bipv"]["roof_sensorgrid"] is not None:
            sensor_grid_dict_roof = urban_canopy_dict["buildings"][building_id]["solar_radiation_and_bipv"][
                "roof_sensorgrid"]
            mesh_roof_list.append(get_rhino_mesh_from_sensor_grid(sensor_grid_dict_roof))
        else:
            mesh_roof_list.append(None)
        # Facades
        if urban_canopy_dict["buildings"][building_id]["solar_radiation_and_bipv"]["facades_sensorgrid"] is not None:
                sensor_grid_dict_facades = urban_canopy_dict["buildings"][building_id]["solar_radiation_and_bipv"][
                    "facades_sensorgrid"]
                mesh_facades_list.append(get_rhino_mesh_from_sensor_grid(sensor_grid_dict_facades))
        else:
            mesh_facades_list.append(None)


    roof_hb_sensorgrid_tree = th.list_to_tree(mesh_roof_list)
    facades_hb_sensorgrid_tree = th.list_to_tree(mesh_facades_list)

if not os.path.isfile(path_json):
    print("the json file of the urban canopy does not exist")
