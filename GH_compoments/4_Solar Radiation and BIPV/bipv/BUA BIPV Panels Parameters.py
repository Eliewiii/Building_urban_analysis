"""Parameters for the BIPV panels.
    Inputs:
        _roof_pv_tech_id: Identifier of the PV technology to use for the roof
        _facades_pv_tech_id: Identifier of the PV technology to use for the facades
        _minimum_panel_eroi_: Minimum EROI of the PV panels to be installed (Default: 1.2)
        _efficiency_computation_method_: Method to compute the efficiency of the panels, either "yearly" or "hourly"
            for now only "yearly" is implemented (Default: "yearly")
        _run :Plug a boolean toggle to run the component and generate the output.
    Output:
        bipv_panel_parameters: Dictionary containing the parameters for the BIPV panels """

__author__ = "elie-medioni"
__version__ = "2023.09.19"

ghenv.Component.Name = "BUA BIPV Panels Parameters"
ghenv.Component.NickName = 'BIPVPanelsParameters'
ghenv.Component.Message = '0.0.0'
ghenv.Component.Category = 'BUA'
ghenv.Component.SubCategory = '4 :: Solar Radiation and BIPV'
ghenv.Component.AdditionalHelpFromDocStrings = "1"

import os
import json


# Get Appdata\local folder
local_appdata = os.environ['LOCALAPPDATA']
path_tool = os.path.join(local_appdata, "Building_urban_analysis")
path_data_libraries = os.path.join(path_tool, "Libraries")
path_pv_technology_folder = os.path.join(path_data_libraries, "BIPV_technologies")

# Initilize the bipv panel parameters dictionary

bipv_panel_parameters_dict = {
        "roof_pv_tech_id": None,
        "facade_pv_tech_id": None,
        "minimum_panel_eroi": None,
        "efficiency_computation_method": None
    }

if _run:
    # Read the pv technologies dictionary to check if the parameters are valid
    pv_technologies_dict = {}
    for json_file in os.listdir(path_pv_technology_folder):  # for every json file in the folder
        if json_file.endswith(".json"):
            path_json_file = os.path.join(path_pv_technology_folder,
                                          json_file)  # get the path to the json file
            with open(path_json_file) as f:  # open and load the json file
                pv_dict_data = json.load(f)
                for identifier_key in pv_dict_data:
                    pv_technologies_dict[identifier_key] = pv_dict_data[identifier_key]

    # Minimum panel eroi
    if _minimum_panel_eroi_ < 1:
        raise ValueError(
            "The minimum panel eroi must be greater than 1, otherwsie the panel is not profitable")
    else:
        bipv_panel_parameters_dict["minimum_panel_eroi"] = _minimum_panel_eroi_

    # Roof BIPV technology
    if _roof_pv_tech_id is not None:
        if _roof_pv_tech_id in pv_technologies_dict:
            bipv_panel_parameters_dict["roof_pv_tech_id"] = _roof_pv_tech_id
        else:
            raise ValueError("The roof pv technology id is not valid")
    # Facade BIPV technology
    if _facades_pv_tech_id is not None:
        if _facades_pv_tech_id in pv_technologies_dict:
            bipv_panel_parameters_dict["facade_pv_tech_id"] = _facades_pv_tech_id
        else:
            raise ValueError("The facade pv technology id is not valid")

    # Efficiency computation method parameters (todo in the future)
    if _efficiency_computation_method_ is None:
        bipv_panel_parameters_dict["efficiency_computation_method"] = "yearly"
    elif _efficiency_computation_method_ == "hourly":
        ValueError("Not implemented yet")
        # todo: implement it and check if the pv_tech has the coefficient for the hourly computation
        # todo add eventually a path to epw file
    elif _efficiency_computation_method_ == "yearly":
        bipv_panel_parameters_dict["efficiency_computation_method"] = _efficiency_computation_method_
    else:
        raise ValueError("The efficiency computation method is not valid, choose between yearly and hourly")

bipv_panel_parameters = json.dumps(bipv_panel_parameters_dict)