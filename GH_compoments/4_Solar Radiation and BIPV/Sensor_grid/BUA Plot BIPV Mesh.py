"""Plot the meshes on the buildings for the BIPV simulation
    Inputs:
        path_simulation_folder_: Path to the folder. Default = Appdata\Local\Building_urban_analysis\Simulation_temp
        building_id_list_: list of ints: list of buildings we want to run the simulation on
        _run: Plug in a boolean toggle to run the component
    Output:
        report: report
        path_simulation_folder_: Path to the folder.
        roof_hb_sensorgrid_tree: Tree of meshes for the roof
        facades_hb_sensorgrid_tree: Tree of meshes for the facades"""

__author__ = "Eliewiii"
__version__ = "2023.08.21"

ghenv.Component.Name = "BUA Plot BIPV Mesh"
ghenv.Component.NickName = 'PlotBIPVMesh'
ghenv.Component.Message = '0.0.0'
ghenv.Component.Category = 'BUA'
ghenv.Component.SubCategory = '4 :: Solar Radiation and BIPV'
ghenv.Component.AdditionalHelpFromDocStrings = "1"

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

# set default value for the simulation folder if not provided
if path_simulation_folder_ is None:
    path_simulation_folder_ = os.path.join(path_tool, "Simulation_temp")

path_json = os.path.join(path_simulation_folder_, "urban_canopy.json")

if _run and os.path.isfile(path_json):

    # Init
    mesh_roof_list = []
    mesh_facades_list = []
    with open(path_json, 'r') as json_file:
        urban_canopy_dict = json.load(json_file)
    for id in list(urban_canopy_dict["buildings"].keys()):
        if (building_id_list_ == [] or building_id_list_ == ["all"]) or str(id) in building_id_list_:
            # Roof
            if urban_canopy_dict["buildings"][id]["solar_radiation_and_bipv"]["roof_sensorgrid"] is not None:
                sensor_grid_dict_roof = urban_canopy_dict["buildings"][id]["solar_radiation_and_bipv"][
                    "roof_sensorgrid"]
                mesh_roof_list.append(get_rhino_mesh_from_sensor_grid(sensor_grid_dict_roof))
            # Facade
            if urban_canopy_dict["buildings"][id]["solar_radiation_and_bipv"][
                "facades_sensorgrid"] is not None:
                sensor_grid_dict_facades = urban_canopy_dict["buildings"][id]["solar_radiation_and_bipv"][
                    "facades_sensorgrid"]
                mesh_facades_list.append(get_rhino_mesh_from_sensor_grid(sensor_grid_dict_facades))

    roof_hb_sensorgrid_tree = th.list_to_tree(mesh_roof_list)
    facades_hb_sensorgrid_tree = th.list_to_tree(mesh_facades_list)

if not os.path.isfile(path_json):
    print("the json file of the urban canopy does not exist")
