"""Read the annual solar irradiance results from the json file of the urban canopy
    Inputs:
        path_simulation_folder_: Path to the folder
        building_id_list_: list of ints: list of buildings we want to read the results
        kept_panel_only_ : bool: True if we want to read the results for the kept panels only.
            This option is only available after the bipv simulation.
        _run: Plug in a boolean toggle to run the component and read the results
    Output:
        report: report
        roof_annual_irrandiance_tree: Tree of the annual irradiance for the roof
        facades_annual_irrandiance_tree: Tree of the annual irradiance for the facades"""

__author__ = "Eliewiii"
__version__ = "2023.08.21"

ghenv.Component.Name = "BUA Read Annual Solar Irrandiance Results"
ghenv.Component.NickName = 'ReadAnnualSolarIrrandianceResults'
ghenv.Component.Message = '0.0.0'
ghenv.Component.Category = 'BUA'
ghenv.Component.SubCategory = '5 :: Solar Radiation and BIPV'
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

if kept_panel_only_ is None:
    kept_panel_only_ = False

path_json = os.path.join(path_simulation_folder_, "urban_canopy.json")

if _run and os.path.isfile(path_json):

    # Init
    roof_annual_solar_irr_list = []
    facades_annual_solar_irr_list = []
    with open(path_json, 'r') as json_file:
        urban_canopy_dict = json.load(json_file)
    for id in list(urban_canopy_dict["buildings"].keys()):
        if (building_id_list_ == [] or building_id_list_ == ["all"]) or str(id) in building_id_list_:
            # Roof
            if urban_canopy_dict["buildings"][id]["solar_radiation_and_bipv"][
                "roof_annual_panel_irradiance_list"] is not None:
                annual_solar_irr = urban_canopy_dict["buildings"][id]["solar_radiation_and_bipv"][
                    "roof_annual_panel_irradiance_list"]
                if kept_panel_only_ and urban_canopy_dict["buildings"][id]["solar_radiation_and_bipv"][
                    "roof_panel_mesh_index_list"] is not None:
                    annual_solar_irr = [
                        annual_solar_irr[i] if i in urban_canopy_dict["buildings"][id]["solar_radiation_and_bipv"][
                            "roof_panel_mesh_index_list"] else 0 for i, _ in enumerate(annual_solar_irr)]
                roof_annual_solar_irr_list.append(annual_solar_irr)
            # Facade
            if urban_canopy_dict["buildings"][id]["solar_radiation_and_bipv"][
                "facades_annual_panel_irradiance_list"] is not None:
                annual_solar_irr = urban_canopy_dict["buildings"][id]["solar_radiation_and_bipv"][
                    "facades_annual_panel_irradiance_list"]
                if kept_panel_only_ and urban_canopy_dict["buildings"][id]["solar_radiation_and_bipv"][
                    "facades_panel_mesh_index_list"] is not None:
                    annual_solar_irr = [
                        annual_solar_irr[i] if i in urban_canopy_dict["buildings"][id]["solar_radiation_and_bipv"][
                            "facades_panel_mesh_index_list"] else 0 for i, _ in enumerate(annual_solar_irr)]
                facades_annual_solar_irr_list.append(annual_solar_irr)

    roof_annual_irrandiance_tree = th.list_to_tree(roof_annual_solar_irr_list)
    facades_annual_irrandiance_tree = th.list_to_tree(facades_annual_solar_irr_list)

if not os.path.isfile(path_json):
    print("the json file of the urban canopy does not exist")
