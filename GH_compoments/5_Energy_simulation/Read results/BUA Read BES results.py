"""Read the results of the Building Energy Simulation (BES) for the buildings individually.
    Inputs:
        path_simulation_folder_: Path to the folder. By default, the code will be run in
                                Appdata\Local\Building_urban_analysis\Simulation_temp
        building_id_list_: List of building ids to read. If empty, the result will be read for all target buildings.
        _run : Plug a boolean toggle to True to run the code and display the results.
    Output:
        read_building_id_list : List of the ids of the buildings that were read
        end_uses_energy_label : list of the eend energy use categories shown in the results
        end_uses_energy_consumption_tree : Tree of the list of the yearly energy consumption for each read building.
"""

__author__ = "Elie"
__version__ = "2023.08.21"

ghenv.Component.Name = "BUA Read BES Results"
ghenv.Component.NickName = 'ReadBESResults'
ghenv.Component.Message = '0.0.0'
ghenv.Component.Category = 'BUA'
ghenv.Component.SubCategory = '5 :: Energy Simulation'
ghenv.Component.AdditionalHelpFromDocStrings = "1"

import json
import os

import ghpythonlib.treehelpers as th
from ladybug_rhino.fromgeometry import from_face3d
from ladybug_geometry.geometry3d.face import Face3D

from honeybee.shade import Shade


def clean_path(path):
    path = path.replace("\\", "/")
    return (path)


def extract_sorted_bes_keys(dictionary):
    # Specific order of keys
    order = ["heating", "cooling", "lighting", "equipment", "ventilation", "total"]

    # Initialize a list to hold the keys in the desired order
    ordered_keys = []

    # Iterate through the specific order and add the keys if they exist in the dictionary
    for key in order:
        if key in dictionary:
            ordered_keys.append(key)

    # Add any additional keys that are not in the specific order
    for key in dictionary:
        if key not in ordered_keys:
            ordered_keys.append(key)

    return ordered_keys


# Get Appdata\local folder
local_appdata = os.environ['LOCALAPPDATA']
path_tool = os.path.join(local_appdata, "Building_urban_analysis")

# set default value for the simulation folder if not provided
if path_simulation_folder_ is None:
    path_simulation_folder_ = os.path.join(path_tool, "Simulation_temp")

path_json = os.path.join(path_simulation_folder_, "urban_canopy.json")

# Run the code if the _run input is set to True
if _run:
    # Check if the json file exists
    if not os.path.isfile(path_json):
        raise ValueError("The json file of the urban canopy does not exist, it means that the simulation was not run.")

    # Read the json file
    with open(path_json, 'r') as json_file:
        urban_canopy_dict = json.load(json_file)

    # Get the list of the building ids to display
    if building_id_list_ == [] or building_id_list_ is None:
        # add the id of the buildings that have been run if no list is provided
        building_id_list_ = [building_id for building_id in urban_canopy_dict["buildings"].keys() if
                             (urban_canopy_dict["buildings"][building_id]["type"] == "BuildingModeled" and
                              urban_canopy_dict["buildings"][building_id]["bes"]["has_run"])]

    else:  # Check if the building ids are in the json file
        for building_id in building_id_list_:
            try:
                urban_canopy_dict["buildings"][building_id]
            except KeyError:
                raise KeyError("Building with ID '{}' not found in the dictionary.".format(building_id))
            else:
                if not urban_canopy_dict["buildings"][building_id]["type"] == "BuildingModeled":
                    raise ValueError(
                        "Building with ID {} does not have a HB model, a BES cannot be performed on it".format(
                            building_id))
                elif not urban_canopy_dict["buildings"][building_id]["bes"]["has_run"]:
                    raise ValueError("BES for building ID {} was not performed".format(building_id))

    # Init
    end_uses_energy_consumption_tree = []
    read_building_id_list = building_id_list_

    # Collect the labels of the end uses
    end_uses_energy_label = extract_sorted_bes_keys(
        urban_canopy_dict["buildings"][building_id_list_[0]]["bes"]["bes_results_dict"])

    for building_id in building_id_list_:
        # Collect the energy consumption for each end use
        building_end_uses_energy_consumption = []
        for label in end_uses_energy_label:
            building_end_uses_energy_consumption.append(urban_canopy_dict["buildings"][building_id]["bes"][
                                                            "bes_results_dict"][label]["yearly"])
        end_uses_energy_consumption_tree.append([building_end_uses_energy_consumption])

    # Convert to tree
    end_uses_energy_consumption_tree = th.list_to_tree(end_uses_energy_consumption_tree)

if not os.path.isfile(path_json):
    print("the json file of the urban canopy does not exist")
