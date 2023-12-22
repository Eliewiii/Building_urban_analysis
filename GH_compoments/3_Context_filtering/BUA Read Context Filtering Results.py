"""Read the results of the context filtering. The results are seperated for the first and second pass of the filtering.
Please refer to the documentation for more information about the context filtering method.
Note that the shades are not added the HB model of the Building objects. They are used during all the relevant
simulations, but they can hinder some operations and displays and are thus not added to the HB model.
    Inputs:
        path_simulation_folder_: Path to the folder. By default, the code will be run in
                                Appdata\Local\Building_urban_analysis\Simulation_temp
        building_id_list_: List of building ids to read. If empty, the result will be read for all target buildings.
        _run : Plug a boolean toggle to True to run the code and display the results.
    Output:
        read_building_id_list : List of the ids of the buildings that were read
        forced_shade_from_user_tree : Tree of the list of forced hb shades for each read building. Forced shades can be
            added with the dedicated component or while loading the HB model in the BUA with the option "keep_context" to True.
        first_pass_selected_building_id_tree : Tree of the list of selected buildings ids for each read building (first pass).
        second_pass_selected_hb_shade_tree : Tree of the list of selected HB shades for each read building (second pass).
            Can be converted to brep for easier display.
"""

__author__ = "Elie"
__version__ = "2023.08.21"

ghenv.Component.Name = "BUA Load Building Envelopes"
ghenv.Component.NickName = 'LoadBuildingEnvelopes'
ghenv.Component.Message = '0.0.0'
ghenv.Component.Category = 'BUA'
ghenv.Component.SubCategory = '2 :: Building Manipulation'
ghenv.Component.AdditionalHelpFromDocStrings = "1"

import json
import os

import ghpythonlib.treehelpers as th

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
if _run and os.path.isfile(path_json):

    # Read the json file
    with open(path_json, 'r') as json_file:
        urban_canopy_dict = json.load(json_file)

    # Get the list of the building ids to display
    if _building_id_list == [] or _building_id_list is None:
        # add the id of the target building
        _building_id_list = [building_key for building_key in urban_canopy_dict["buildings"].keys() if
                             urban_canopy_dict["buildings"][building_key]["is_target_building"] == True]
    elif _building_id_list == "target_and_simulated":
        _building_id_list = [building_key for building_key in urban_canopy_dict["buildings"].keys() if
                             urban_canopy_dict["buildings"][building_key]["is_target_building"] or
                             urban_canopy_dict["buildings"][building_key]["is_building_to_simulate"]]
    else:  # Check if the building ids are in the json file
        for building_id in _building_id_list:
            try:
                urban_canopy_dict["buildings"][building_id]
            except KeyError:
                raise KeyError(f"Building with ID '{building_id}' not found in the dictionary.")
            else:
                if not urban_canopy_dict["buildings"][building_id]["is_target_building"] and not \
                        urban_canopy_dict["buildings"][building_id]["is_building_to_simulate"]:
                    raise ValueError("Building with ID {} is not a target building. It does not".format(building_id))

    # Init
    forced_shade_from_user_tree = []
    first_pass_selected_building_id_tree = []
    second_pass_selected_hb_shade_tree = []
    read_building_id_list = _building_id_list

    for building_id in _building_id_list:
        # Check if the building has forced shades and add the list of forced HB Shades
        if urban_canopy_dict["buildings"][building_id]["context_surfaces"]["forced_shades_from_user"] is not None:
            forced_shade_from_user_tree.append([Shade.from_dict(shade) for shade in
                                                urban_canopy_dict["buildings"][building_id]["context_surfaces"][
                                                    "forced_shades_from_user"]])
        else:
            forced_shade_from_user_tree.append([])
        # Check if the building first pass of the context filtering was done and add the selected building ids
        if urban_canopy_dict["buildings"][building_id]["context_surfaces"]["first_pass_done"]:
            first_pass_selected_building_id_tree.append(
                urban_canopy_dict["buildings"][building_id]["context_surfaces"]["first_pass_selected_building_id_list"])
        else:
            first_pass_selected_building_id_tree.append([])
            print(
                "The first pass of the context filtering was not done for the building with id {}".format(building_id))
        # Check if the building second pass of the context filtering was done and add the selected HB shades
        if urban_canopy_dict["buildings"][building_id]["context_surfaces"]["second_pass_done"]:
            second_pass_selected_hb_shade_tree.append([Shade.from_dict(shade) for shade in
                                                       urban_canopy_dict["buildings"][building_id]["context_surfaces"][
                                                           "second_pass_selected_hb_shade_list"]])
        else:
            second_pass_selected_hb_shade_tree.append([])
            print(
                "The second pass of the context filtering was not done for the building with id {}".format(building_id))


    # Convert to tree
    forced_shade_from_user_tree = th.list_to_tree(forced_shade_from_user_tree)
    first_pass_selected_building_id_tree = th.list_to_tree(first_pass_selected_building_id_tree)
    second_pass_selected_hb_shade_tree = th.list_to_tree(second_pass_selected_hb_shade_tree)

if not os.path.isfile(path_json):
    print("the json file of the urban canopy does not exist")
