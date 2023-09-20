"""Get the HB models from the urban canopy json file
    Inputs:
        path_simulation_folder_: Path to the simulation folder
        _building_id_list : list of the building id to get teh HB models. If empty, get all the HB models.
        _run : Plug a boolean toggle. Put it to true if we want to run the code.
    Output:
        hb_model_list: """

__author__ = "Eliewiii"
__version__ = "2023.09.20"

ghenv.Component.Name = "BUA Cet HB Models"
ghenv.Component.NickName = 'GetHBModels'
ghenv.Component.Message = '0.0.0'
ghenv.Component.Category = 'BUA'
ghenv.Component.SubCategory = '6 :: General'
ghenv.Component.AdditionalHelpFromDocStrings = "1"


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
    if _building_id_list == [] or _building_id_list is None:
        _building_id_list = []
        # add the id of the target building
        for id in list(urban_canopy_dict["buildings"].keys()):
            if urban_canopy_dict["buildings"][id]["is_target_building"] == True:
                _building_id_list.append(id)

    hb_model_list = []
    values_roof_list = []
    mesh_roof_list = []
    values_facade_list = []
    mesh_facade_list = []

    for building_id in _building_id_list:
        if urban_canopy_dict["buildings"][building_id]["hb_model"] is not None:
            hb_model_list.append(Model.from_dict(urban_canopy_dict["buildings"][building_id]["hb_model"]))

if not os.path.isfile(path_json):
    print("the json file of the urban canopy does not exist")
