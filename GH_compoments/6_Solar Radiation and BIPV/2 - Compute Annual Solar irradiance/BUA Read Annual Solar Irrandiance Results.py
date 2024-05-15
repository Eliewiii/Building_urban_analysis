"""Read the annual solar irradiance results from the json file of the urban canopy.
    Inputs:
        path_simulation_folder_: Path to the folder
        building_id_list_: list of ints: list of buildings we want to read the results
        kept_panel_only_ : Set to True if we want to read the results for the kept panels only.
            This option is only available after the bipv simulation.
        _run: Plug in a boolean toggle to run the component and read the results
    Output:
        report: report
        roof_annual_irradiance_tree: Tree of the annual irradiance for the roof
        facades_annual_irradiance_tree: Tree of the annual irradiance for the facades"""

__author__ = "elie-medioni"
__version__ = "2024.05.07"

ghenv.Component.Name = "BUA Read Annual Solar Irrandiance Results"
ghenv.Component.NickName = 'ReadAnnualSolarIrrandianceResults'
ghenv.Component.Message = '1.0.0'
ghenv.Component.Category = 'BUA'
ghenv.Component.SubCategory = '6 :: Solar Radiation and BIPV'

import ghpythonlib.treehelpers as th

import json
import os


def clean_path(path):
    path = path.replace("\\", "/")
    return (path)


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

if kept_panel_only_ is None:
    kept_panel_only_ = False

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
                              (urban_canopy_dict["buildings"][building_id]["solar_radiation_and_bipv"]["roof_annual_panel_irradiance_list"] is not None
                              or urban_canopy_dict["buildings"][building_id]["solar_radiation_and_bipv"]["facades_annual_panel_irradiance_list"] is not None))]

    else:  # Check if the building ids are in the json file
        for building_id in building_id_list_:
            try:
                urban_canopy_dict["buildings"][building_id]
            except KeyError:
                raise KeyError("Building with ID '{}' not found in the dictionary.".format(building_id))
            else:
                if not urban_canopy_dict["buildings"][building_id]["type"] == "BuildingModeled":
                    raise ValueError(
                        "Building with ID {} does not have a HB model, no radiation simulation could have been performed on it".format(
                            building_id))
                elif (urban_canopy_dict["buildings"][building_id]["solar_radiation_and_bipv"]["roof_annual_panel_irradiance_list"] is None
                              and  urban_canopy_dict["buildings"][building_id]["solar_radiation_and_bipv"]["facades_annual_panel_irradiance_list"] is None):
                    raise ValueError("Radiation simulation for building ID {} was not performed".format(building_id))

    # Init
    roof_annual_solar_irr_list = []
    facades_annual_solar_irr_list = []

    for building_id in building_id_list_:
        # Roof
        if urban_canopy_dict["buildings"][building_id]["solar_radiation_and_bipv"][
            "roof_annual_panel_irradiance_list"] is not None:
            annual_solar_irr = urban_canopy_dict["buildings"][building_id]["solar_radiation_and_bipv"][
                "roof_annual_panel_irradiance_list"]
            if kept_panel_only_ and urban_canopy_dict["buildings"][building_id]["solar_radiation_and_bipv"][
                "roof_panel_mesh_index_list"] is not None:
                annual_solar_irr = [
                    annual_solar_irr[i] if i in urban_canopy_dict["buildings"][building_id]["solar_radiation_and_bipv"][
                        "roof_panel_mesh_index_list"] else 0 for i, _ in enumerate(annual_solar_irr)]
            roof_annual_solar_irr_list.append(annual_solar_irr)
        else:
            roof_annual_solar_irr_list.append([])
        # Facade
        if urban_canopy_dict["buildings"][building_id]["solar_radiation_and_bipv"][
            "facades_annual_panel_irradiance_list"] is not None:
            annual_solar_irr = urban_canopy_dict["buildings"][building_id]["solar_radiation_and_bipv"][
                "facades_annual_panel_irradiance_list"]
            if kept_panel_only_ and urban_canopy_dict["buildings"][building_id]["solar_radiation_and_bipv"][
                "facades_panel_mesh_index_list"] is not None:
                annual_solar_irr = [
                    annual_solar_irr[i] if i in urban_canopy_dict["buildings"][building_id]["solar_radiation_and_bipv"][
                        "facades_panel_mesh_index_list"] else 0 for i, _ in enumerate(annual_solar_irr)]
            facades_annual_solar_irr_list.append(annual_solar_irr)
        else:
            facades_annual_solar_irr_list.append([])

    roof_annual_irradiance_tree = th.list_to_tree(roof_annual_solar_irr_list)
    facades_annual_irradiance_tree = th.list_to_tree(facades_annual_solar_irr_list)

if not os.path.isfile(path_json):
    print("the json file of the urban canopy does not exist")
