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

ghenv.Component.Name = "BUA Read Context Filtering Results"
ghenv.Component.NickName = 'ReadContextFilteringResults'
ghenv.Component.Message = '0.0.0'
ghenv.Component.Category = 'BUA'
ghenv.Component.SubCategory = '3 :: Context filtering'
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


# Get Appdata\local folder
local_appdata = os.environ['LOCALAPPDATA']
path_tool = os.path.join(local_appdata, "Building_urban_analysis")

# set default value for the simulation folder if not provided
if path_simulation_folder_ is None:
    path_simulation_folder_ = os.path.join(path_tool, "Simulation_temp")

path_json = os.path.join(path_simulation_folder_, "urban_canopy.json")

# Run the code if the _run input is set to True
if _run :
    # Check if the json file exists
    if not os.path.isfile(path_json):
        raise ValueError("The json file of the urban canopy does not exist, it means that the simulation was not run.")

    # Read the json file
    with open(path_json, 'r') as json_file:
        urban_canopy_dict = json.load(json_file)

    # Get the list of the building ids to display
    if _building_id_list == [] or _building_id_list is None:
        # add the id of the buildings that have been run if no list is provided
        _building_id_list = [building_id for building_id in urban_canopy_dict["buildings"].keys() if
                             (urban_canopy_dict["buildings"][building_id]["type"] == "BuildingModeled" and
                              urban_canopy_dict["buildings"][building_id]["bes"]["has_run"])]

    else:  # Check if the building ids are in the json file
        for building_id in _building_id_list:
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
    read_building_id_list = _building_id_list

    # Collect the labels of the end uses
    end_uses_energy_label = list(urban_canopy_dict["buildings"][_building_id_list[0]]["bes"]["bes_results_dict"].keys())


    for building_id in _building_id_list:
        for label in end_uses_energy_label:
            end_uses_energy_consumption_tree.append(urban_canopy_dict["buildings"][building_id]["bes"][
                                                        "bes_results_dict"][label]["yearly"])
        # Check if the building has forced shades and add the list of forced HB Shades
        if urban_canopy_dict["buildings"][building_id]["context_surfaces"][
            "forced_shades_from_user"] is not None:
            end_uses_energy_consumption_tree.append([Shade.from_dict(shade) for shade in
                                                urban_canopy_dict["buildings"][building_id][
                                                    "context_surfaces"][
                                                    "forced_shades_from_user"]])
        else:
            forced_shade_from_user_tree.append([])
        # Check if the building first pass of the context filtering was done and add the selected building ids
        if urban_canopy_dict["buildings"][building_id]["context_surfaces"]["parameters"]["first_pass_done"]:
            first_pass_selected_building_id_tree.append(
                urban_canopy_dict["buildings"][building_id]["context_surfaces"][
                    "first_pass_selected_building_id_list"])
            # make a list of discarded building ids
            first_pass_discarded_building_id_tree.append(
                [id for id in list(urban_canopy_dict["buildings"].keys()) if
                 (id not in first_pass_selected_building_id_tree[-1] and id != building_id)])
        else:
            first_pass_selected_building_id_tree.append([])
            print(
                "The first pass of the context filtering was not done for the building with id {}".format(
                    building_id))
        # Check if the building second pass of the context filtering was done and add the selected HB shades
        if urban_canopy_dict["buildings"][building_id]["context_surfaces"]["parameters"]["second_pass_done"]:
            second_pass_selected_hb_shade_tree.append([Shade.from_dict(shade) for shade in
                                                       urban_canopy_dict["buildings"][building_id][
                                                           "context_surfaces"][
                                                           "second_pass_selected_hb_shade_list"]])
            if urban_canopy_dict["buildings"][building_id]["context_surfaces"][
                "discarded_face3d_second_pass_list"] is not None:
                second_pass_discarded_surface_tree.append([from_face3d(Face3D.from_dict(face)) for face in
                                                           urban_canopy_dict["buildings"][building_id][
                                                               "context_surfaces"][
                                                               "discarded_face3d_second_pass_list"]])
            else:
                second_pass_discarded_surface_tree.append([])
                print(
                    "The the option to keep the discarded surfaces for the second pass of the context filtering was " \
                    "not done for the building with id {}".format(building_id))
        else:
            second_pass_selected_hb_shade_tree.append([])
            print(
                "The second pass of the context filtering was not done for the building with id {}".format(
                    building_id))

    # Convert to tree
    forced_shade_from_user_tree = th.list_to_tree(forced_shade_from_user_tree)
    first_pass_selected_building_id_tree = th.list_to_tree(first_pass_selected_building_id_tree)
    first_pass_discarded_building_id_tree = th.list_to_tree(first_pass_discarded_building_id_tree)
    second_pass_selected_hb_shade_tree = th.list_to_tree(second_pass_selected_hb_shade_tree)
    second_pass_discarded_surface_tree = th.list_to_tree(second_pass_discarded_surface_tree)

if not os.path.isfile(path_json):
    print("the json file of the urban canopy does not exist")
