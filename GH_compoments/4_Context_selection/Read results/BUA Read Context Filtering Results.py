"""Read the results of the context filtering. The results are seperated for the first and second pass of the filtering.
Please refer to the documentation for more information about the context filtering method.
Note that the shades are not added the HB model of the Building objects. They are used during all the relevant
simulations, but they can hinder some operations and displays and are thus not added to the HB model.
    Inputs:
        path_simulation_folder_: Path to the folder. By default, the code will be run in
                                Appdata\Local\Building_urban_analysis\Simulation_temp
        _building_id_list_: List of building ids to read. If empty, the result will be read for all target buildings.
        _run : Plug a boolean toggle to True to run the code and display the results.
    Output:
        read_building_id_list : List of the ids of the buildings that were read
        forced_shade_from_user_tree : Tree of the list of forced hb shades for each read building. Forced shades can be
            added with the dedicated component or while loading the HB model in the BUA with the option "keep_context" to True.
        first_pass_selected_building_id_tree : Tree of the list of selected buildings ids for each read building (first pass).
        first_pass_discarded_building_id_tree : Tree of the list of discarded faces for each read building (first pass).
        second_pass_selected_hb_shade_tree : Tree of the list of selected HB shades for each read building (second pass).
            Can be converted to brep for easier display.
        second_pass_discarded_surface_tree : Tree of the list of discarded faces for each read building (second pass).
"""

__author__ = "elie-medioni"
__version__ = "2024.05.07"

ghenv.Component.Name = "BUA Read Context Filtering Results"
ghenv.Component.NickName = 'ReadContextFilteringResults'
ghenv.Component.Message = '1.0.0'
ghenv.Component.Category = 'BUA'
ghenv.Component.SubCategory = '4 :: Context Selection'

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

# Check path_simulation_folder_
if path_simulation_folder_ is None:
    path_simulation_folder_ = os.path.join(path_tool, "Simulation_temp")
elif os.path.isdir(path_simulation_folder_) is False:
    raise ValueError("The simulation folder does not exist, enter a valid path")

# Path to the urban canopy json file
path_json = os.path.join(path_simulation_folder_, "urban_canopy.json")


# Run the code
if _run:
    # Check if the urban canopy json file exists
    if not os.path.isfile(path_json):
        raise ValueError(
            "The urban canopy json file does not exist, buildings need to be loaded before running the context selection.")
    # Read the json file
    with open(path_json, 'r') as json_file:
        urban_canopy_dict = json.load(json_file)

    # Get the list of the building ids to display
    if _building_id_list_ == [] or _building_id_list_ is None:
        # add the id of the buildings that have been run if no list is provided
        _building_id_list_ = [building_id for building_id in urban_canopy_dict["buildings"].keys() if
                             (urban_canopy_dict["buildings"][building_id]["type"] == "BuildingModeled" and
                              urban_canopy_dict["buildings"][building_id]["context_surfaces"]["first_pass_done"])]

    else:  # Check if the building ids are in the json file
        for building_id in _building_id_list_:
            try:
                urban_canopy_dict["buildings"][building_id]
            except KeyError:
                raise KeyError("Building with ID '{}' not found in the dictionary.".format(building_id))
            else:
                if not urban_canopy_dict["buildings"][building_id]["type"] == "BuildingModeled":
                    raise ValueError(
                        "Building with ID {} does not have a HB model, a context filtering cannot be performed on it".format(
                            building_id))
                elif not urban_canopy_dict["buildings"][building_id]["context_surfaces"]["first_pass_done"]:
                    raise ValueError("Context filtering for building ID {} was not performed".format(building_id))

    # Init
    forced_shade_from_user_tree = []
    first_pass_selected_building_id_tree = []
    first_pass_discarded_building_id_tree = []
    second_pass_selected_hb_shade_tree = []
    second_pass_discarded_surface_tree = []
    read_building_id_list = _building_id_list_

    for building_id in _building_id_list_:
        # Check if the building has forced shades and add the list of forced HB Shades
        if urban_canopy_dict["buildings"][building_id]["context_surfaces"]["forced_hb_shades_from_user_list"] is not None:
            forced_shade_from_user_tree.append([Shade.from_dict(shade) for shade in
                                                urban_canopy_dict["buildings"][building_id]["context_surfaces"][
                                                    "forced_hb_shades_from_user_list"]])
        else:
            forced_shade_from_user_tree.append([])
        # Check if the building first pass of the context filtering was done and add the selected building ids
        if urban_canopy_dict["buildings"][building_id]["context_surfaces"]["first_pass_done"]:
            first_pass_selected_building_id_tree.append(
                urban_canopy_dict["buildings"][building_id]["context_surfaces"]["selected_context_building_id_list"])
            # make a list of discarded building ids
            first_pass_discarded_building_id_tree.append(
                [id for id in list(urban_canopy_dict["buildings"].keys()) if
                 (id not in first_pass_selected_building_id_tree[-1] and id != building_id)])
        else:
            first_pass_selected_building_id_tree.append([])
            print(
                "The first pass of the context filtering was not done for the building with id {}".format(building_id))
        # Check if the building second pass of the context filtering was done and add the selected HB shades
        if urban_canopy_dict["buildings"][building_id]["context_surfaces"]["second_pass_done"]:
            second_pass_selected_hb_shade_tree.append([Shade.from_dict(shade) for shade in
                                                       urban_canopy_dict["buildings"][building_id]["context_surfaces"][
                                                           "context_shading_hb_shade_list"]])
            if urban_canopy_dict["buildings"][building_id]["context_surfaces"][
                "discarded_lb_face3d_context_shading_second_pass_list"] is not None:
                second_pass_discarded_surface_tree.append([from_face3d(Face3D.from_dict(face)) for face in
                                                           urban_canopy_dict["buildings"][building_id][
                                                               "context_surfaces"][
                                                               "discarded_lb_face3d_context_shading_second_pass_list"]])
            else:
                second_pass_discarded_surface_tree.append([])
                print(
                    "The the option to keep the discarded surfaces for the second pass of the context filtering was " \
                    "not done for the building with id {}".format(building_id))
        else:
            second_pass_selected_hb_shade_tree.append([])
            print(
                "The second pass of the context filtering was not done for the building with id {}".format(building_id))

    # Convert to tree
    forced_shade_from_user_tree = th.list_to_tree(forced_shade_from_user_tree)
    first_pass_selected_building_id_tree = th.list_to_tree(first_pass_selected_building_id_tree)
    first_pass_discarded_building_id_tree = th.list_to_tree(first_pass_discarded_building_id_tree)
    second_pass_selected_hb_shade_tree = th.list_to_tree(second_pass_selected_hb_shade_tree)
    second_pass_discarded_surface_tree = th.list_to_tree(second_pass_discarded_surface_tree)

if not os.path.isfile(path_json):
    print("the json file of the urban canopy does not exist")
