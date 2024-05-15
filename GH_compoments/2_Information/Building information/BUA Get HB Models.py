"""Get the HB models from the urban canopy json file
    Inputs:
        path_simulation_folder_: Path to the simulation folder
        _building_id_list_ : List of the building id to get teh HB models. If empty, get all the HB models.
        _run : Plug a boolean toggle. Put it to true if we want to run the code.
    Output:
        hb_model_list: List of the HB models"""

__author__ = "elie-medioni"
__version__ = "2024.05.05"

ghenv.Component.Name = "BUA Get HB Models"
ghenv.Component.NickName = 'GetHBModels'
ghenv.Component.Message = '1.0.0'
ghenv.Component.Category = 'BUA'
ghenv.Component.SubCategory = '2 :: Information'


import json
import os

from honeybee.model import Model

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

    hb_model_list = []
    for building_id in _building_id_list_:
        if urban_canopy_dict["buildings"][building_id]["hb_model"] is not None:
            hb_model_list.append(Model.from_dict(urban_canopy_dict["buildings"][building_id]["hb_model"]))

if not os.path.isfile(path_json):
    print("the json file of the urban canopy does not exist")
