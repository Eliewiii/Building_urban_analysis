"""Parameters for the BIPV panels.
    Inputs:
        _roof_pv_tech_id: Identifier of the PV technology to use for the roof
        _roof_pv_transport_id: Identifier of the transport to use for the roof
        _roof_pv_inverter: Identifier of the inverter to use for the roof
        _roof_inverter_sizing_ratio: Roof inverter sizing ratio, ratio of the power of the inverter to the peak power of the panels. (Default: 0.9)
        _facades_pv_tech_id: Identifier of the PV technology to use for the facades
        _facades_pv_transport_id: Identifier of the transport to use for the facades
        _facades_pv_inverter: Identifier of the inverter to use for the facades
        _facades_inverter_sizing_ratio: Facades inverter sizing ratio, ratio of the power of the inverter to the peak power of the panels. (Default: 0.9)
        _minimum_panel_eroi_: Minimum EROI of the PV panels to be installed (Default: 1.2)
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
path_bipv_library_folders = [os.path.join(path_data_libraries, "BIPV", "default"),
                             os.path.join(path_data_libraries, "BIPV", "user")]

# Initilize the bipv panel parameters dictionary

bipv_panel_parameters_dict = {
    "roof_pv_tech_id": None,
    "roof_pv_transport_id": None,
    "roof_pv_inverter": None,
    "roof_inverter_sizing_ratio": None,
    "facades_pv_tech_id": None,
    "facades_pv_transport_id": None,
    "facades_pv_inverter": None,
    "facades_inverter_sizing_ratio": None,
    "minimum_panel_eroi": None,
}

if _run:
    # Read the pv technologies dictionary to check if the parameters are valid
    pv_technologies_dict = {}
    for path_pv_technology_folder in path_bipv_library_folders:
        for json_file in os.listdir(path_pv_technology_folder):  # for every json file in the folder
            if json_file.endswith(".json"):
                path_json_file = os.path.join(path_pv_technology_folder,
                                              json_file)  # get the path to the json file
                with open(path_json_file) as f:  # open and load the json file
                    pv_dict_data = json.load(f)
                    for item in pv_dict_data.items():
                        if item["id"] not in pv_technologies_dict:
                            pv_technologies_dict[item["id"]] = item
                        else:
                            raise ValueError("The element " + item[
                                "id"] + " seems to be duplicated in the libraries. Please, check the libraries to make sure that the elements are unique")

    # Minimum panel eroi
    if _minimum_panel_eroi_ < 1:
        raise ValueError(
            "The minimum panel eroi must be greater than 1, otherwise the panel is not profitable")
    else:
        bipv_panel_parameters_dict["minimum_panel_eroi"] = _minimum_panel_eroi_

    # Roof BIPV technology
    if _roof_pv_tech_id is not None:
        if _roof_pv_tech_id in pv_technologies_dict:
            if pv_technologies_dict[_roof_pv_tech_id]["type"] == "pv_technology":
                bipv_panel_parameters_dict["roof_pv_tech_id"] = _roof_pv_tech_id
            else:
                raise ValueError("_roof_pv_tech_id is not a pv technology, please choose a valid one")
        else:
            raise ValueError("The roof pv technology id is not valid")
    # Facade BIPV technology
    if _facades_pv_tech_id is not None:
        if _facades_pv_tech_id in pv_technologies_dict:
            if pv_technologies_dict[_facades_pv_tech_id]["type"] == "pv_technology":
                bipv_panel_parameters_dict["facades_pv_tech_id"] = _facades_pv_tech_id
            else:
                raise ValueError("_roof_pv_tech_id is not a pv technology, please choose a valid one")
        else:
            raise ValueError("The roof pv technology id is not valid")

    # Roof BIPV transport
    if _roof_pv_transport_id is not None:
        if _roof_pv_transport_id in pv_technologies_dict:
            if pv_technologies_dict[_roof_pv_transport_id]["type"] == "transportation":
                bipv_panel_parameters_dict["roof_pv_transport_id"] = _roof_pv_transport_id
            else:
                raise ValueError("_roof_pv_transport_id is not a transport, please choose a valid one")
        else:
            raise ValueError("The roof pv transport id is not valid")
    # Facade BIPV transport
    if _facades_pv_transport_id is not None:
        if _facades_pv_transport_id in pv_technologies_dict:
            if pv_technologies_dict[_facades_pv_transport_id]["type"] == "transportation":
                bipv_panel_parameters_dict["facades_pv_transport_id"] = _facades_pv_transport_id
            else:
                raise ValueError("_facades_pv_transport_id is not a transport, please choose a valid one")
        else:
            raise ValueError("The facades pv transport id is not valid")

    # Roof BIPV inverter
    if _roof_pv_inverter is not None:
        if _roof_pv_inverter in pv_technologies_dict:
            if pv_technologies_dict[_roof_pv_inverter]["type"] == "inverter":
                bipv_panel_parameters_dict["roof_pv_inverter"] = _roof_pv_inverter
            else:
                raise ValueError("_roof_pv_inverter is not an inverter, please choose a valid one")
        else:
            raise ValueError("The roof pv inverter id is not valid")
    # Facade BIPV inverter
    if _facades_pv_inverter is not None:
        if _facades_pv_inverter in pv_technologies_dict:
            if pv_technologies_dict[_facades_pv_inverter]["type"] == "inverter":
                bipv_panel_parameters_dict["facades_pv_inverter"] = _facades_pv_inverter
            else:
                raise ValueError("_facades_pv_inverter is not an inverter, please choose a valid one")
        else:
            raise ValueError("The facades pv inverter id is not valid")

    # Roof inverter sizing ratio
    if _roof_inverter_sizing_ratio is not None:
        if _roof_inverter_sizing_ratio <= 0:
            raise ValueError("The inverter sizing ratio must be greater than 0")
        else:
            bipv_panel_parameters_dict["roof_inverter_sizing_ratio"] = _roof_inverter_sizing_ratio
    # Facade inverter sizing ratio
    if _facades_inverter_sizing_ratio is not None:
        if _facades_inverter_sizing_ratio <= 0:
            raise ValueError("The inverter sizing ratio must be greater than 0")
        else:
            bipv_panel_parameters_dict["facades_inverter_sizing_ratio"] = _facades_inverter_sizing_ratio

bipv_panel_parameters = json.dumps(bipv_panel_parameters_dict)
