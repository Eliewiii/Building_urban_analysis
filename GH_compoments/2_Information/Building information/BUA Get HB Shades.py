"""Get the HB Shading faces of the buildings.
    Inputs:
        path_simulation_folder_: Path to the simulation folder
        _building_id_list_ : List of the building id to get teh HB models. If empty, get all the HB models.
        _run : Plug a boolean toggle. Put it to true if we want to run the code.
    Output:
        user_hb_shade_tree: Tree of the HB shades set by the user for the buildings
        selected_context_filter_hb_shade_tree: Tree of the HB shades selected by the context filter for the buildings
        """

__author__ = "elie-medioni"
__version__ = "2024.05.05"

ghenv.Component.Name = "BUA Get HB Shades"
ghenv.Component.NickName = 'GetHBShades'
ghenv.Component.Category = 'BUA'
ghenv.Component.SubCategory = '2 :: Information'
ghenv.Component.AdditionalHelpFromDocStrings = "1"

import ghpythonlib.treehelpers as th

import json
import os

from honeybee.shade import Shade

# Get Appdata\local folder
local_appdata = os.environ['LOCALAPPDATA']
path_tool = os.path.join(local_appdata, "Building_urban_analysis")

# set default value for the simulation folder if not provided
if path_simulation_folder_ is None:
    path_simulation_folder_ = os.path.join(path_tool, "Simulation_temp")

path_json = os.path.join(path_simulation_folder_, "urban_canopy.json")

if _run and os.path.isfile(path_json):

    path_json = os.path.join(path_simulation_folder_, "urban_canopy.json")
    with open(path_json, "r") as f:
        urban_canopy_dict = json.load(f)
    # Get the list of the building ids to display
    if _building_id_list_ == [] or _building_id_list_ is None:
        _building_id_list_ = []
        # add the id of the target building
        for building_id in list(urban_canopy_dict["buildings"].keys()):
            if urban_canopy_dict["buildings"][building_id]["type"] == "BuildingModeled":
                _building_id_list_.append(building_id)
    else:  # Check if the building ids are in the json file
        for building_id in _building_id_list_:
            try:
                urban_canopy_dict["buildings"][building_id]
            except KeyError:
                raise KeyError("Building with ID '{}' not found in the dictionary.".format(building_id))
            else:
                if not urban_canopy_dict["buildings"][building_id]["type"] == "BuildingModeled":
                    raise ValueError(
                        "Building with ID {} does not have a HB model and thus not shades".format(
                            building_id))

    user_hb_shade_tree = []
    selected_context_filter_hb_shade_tree = []

    for building_id in _building_id_list_:
        user_hb_shade_tree.append([Shade.from_dict(shade) for shade in urban_canopy_dict["buildings"][building_id]["context_surfaces"][
                                      "forced_hb_shades_from_user_list"]])
        selected_context_filter_hb_shade_tree.append([Shade.from_dict(shade) for shade in
            urban_canopy_dict["buildings"][building_id]["context_surfaces"]["context_shading_hb_shade_list"]])
        # Convert to tree
    user_hb_shade_tree = th.list_to_tree(user_hb_shade_tree)
    selected_context_filter_hb_shade_tree = th.list_to_tree(selected_context_filter_hb_shade_tree)

if not os.path.isfile(path_json):
    print("the json file of the urban canopy does not exist")
