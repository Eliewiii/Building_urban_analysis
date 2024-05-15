"""Read the results of the Urban Building Energy Simulation.
    Inputs:
        path_simulation_folder_: Path to the simulation folder. By default, the code will be run in
                                Appdata\Local\Building_urban_analysis\Simulation_temp
        _run : Plug a boolean toggle to True to run the code and display the results.
    Output:
        end_uses_energy_label : list of the eend energy use categories shown in the results
        end_uses_energy_consumption : List of the yearly energy consumption of the whole urban canopy.
"""

__author__ = "Elie"
__version__ = "2024.04.07"

ghenv.Component.Name = "BUA Read UBES Results"
ghenv.Component.NickName = 'ReadUBESResults'
ghenv.Component.Message = '1.0.0'
ghenv.Component.Category = 'BUA'
ghenv.Component.SubCategory = '5 :: Energy Simulation'

import json
import os

def clean_path(path):
    path = path.replace("\\", "/")
    return (path)


def extract_sorted_bes_keys(dictionary):
    """Extract the keys of the dictionary in a specific order."""
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
        raise ValueError(
            "The json file of the urban canopy does not exist, it means that the simulation was not run.")

    # Read the json file
    with open(path_json, 'r') as json_file:
        urban_canopy_dict = json.load(json_file)

    # Check that the UBES was run
    if not urban_canopy_dict["ubes"]["has_run"]:
        raise ValueError("The UBES simulation was not run. Run the simulation first.")

    # Init
    end_uses_energy_consumption = []

    # Collect the labels of the end uses
    end_uses_energy_label = extract_sorted_bes_keys(
        urban_canopy_dict["ubes"]["ubes_results_dict"])

    for label in end_uses_energy_label:
        end_uses_energy_consumption.append(urban_canopy_dict["ubes"]["ubes_results_dict"][label]["yearly"])
