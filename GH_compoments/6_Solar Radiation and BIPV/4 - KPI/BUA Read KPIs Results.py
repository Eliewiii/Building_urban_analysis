"""Read the results of the KPI Simulation.
    Inputs:
        path_simulation_folder_: Path to the folder. By default, the code will be run in
                                Appdata\Local\Building_urban_analysis\Simulation_temp
        _bipv_simulation_identifier_: Identifier of the BIPV simulation. If not provided, the code will read
            the results of the last simulation.
        _run : Plug a boolean toggle to True to run the code and display the results.
    Output:
        kpis_labels : list of the eend energy use categories shown in the results
        kpis_bipv_roof : list of the kpis for the roof BIPV.
        kpis_bipv_facades : list of the kpis for the facades BIPV.
        kpis_bipv_total : list of the kpis for the total BIPV.
"""

__author__ = "Elie"
__version__ = "2024.06.04"

ghenv.Component.Name = "BUA Read Kpis Results"
ghenv.Component.NickName = 'ReadUKPIsResults'
ghenv.Component.Message = '1.1.2'
ghenv.Component.Category = 'BUA'
ghenv.Component.SubCategory = '6 :: Solar Radiation and BIPV'

import json
import os


def clean_path(path):
    path = path.replace("\\", "/")
    return (path)

def flatten_kpi_dict(d, parent_key='', sep=' '):
    """
    Flatten the KPI dictionary to convert it to CSV.
    :param d: dict, the KPI dictionary
    """
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, dict) and isinstance(list(v.values())[0], dict):
            items.extend(flatten_kpi_dict(v, parent_key=new_key, sep=sep).items())
        else:
            items.append((new_key, [value for value in v.values()]))
    return dict(items)


labels = ["eroi", "ghg emissions intensity [kgCo2eq/kWh]",
           "net energy compensation","economical roi", "net economical benefit [$]",]

# Get Appdata\local folder
local_appdata = os.environ['LOCALAPPDATA']
path_tool = os.path.join(local_appdata, "Building_urban_analysis")
path_bat_file = os.path.join(path_tool, "Scripts", "mains_tool", "run_BUA.bat")


# Check path_simulation_folder_
if path_simulation_folder_ is None:
    path_simulation_folder_ = os.path.join(path_tool, "Simulation_temp")
elif os.path.isdir(path_simulation_folder_) is False:
    raise ValueError("The simulation folder does not exist, enter a valid path")

# Path to the urban canopy json file
path_json = os.path.join(path_simulation_folder_, "urban_canopy.json")

# Check if the _bipv_simulation_identifier_ is exist in the urban canopy json file if not None
if _bipv_simulation_identifier_ is not None:
    if not os.path.isfile(path_json):
        raise ValueError("The urban canopy json file does not exist, buildings need to be loaded before running the context selection.")
    with open(path_json, 'r') as json_file:
        urban_canopy_dict = json.load(json_file)
    if _bipv_simulation_identifier_ not in urban_canopy_dict["bipv_scenarios"].keys():
        raise ValueError(
            "The simulation identifier is not valid, please check the identifier of the bipv simulation"
            "that were run with the adequate component")

# Run the code if the _run input is set to True
if _run:
    # Check if the json file exists
    if not os.path.isfile(path_json):
        raise ValueError(
            "The json file of the urban canopy does not exist, it means that the simulation was not run.")

    # Read the json file
    with open(path_json, 'r') as json_file:
        urban_canopy_dict = json.load(json_file)

    # check if the BIPV simulation identifier is valid
    if urban_canopy_dict["bipv_scenarios"] == {}:
        raise ValueError("No BIPV simulation was run. Run a BIPV simulation first.")
    elif _bipv_simulation_identifier_ is not None:
        if _bipv_simulation_identifier_ not in urban_canopy_dict["bipv_scenarios"]:
            raise ValueError("The BIPV simulation identifier is not valid.")
    else:
        if "new_uc_scenario" in urban_canopy_dict["bipv_scenarios"].keys():
            _bipv_simulation_identifier_ = "new_uc_scenario"
        else:
            raise ValueError("Please provide a BIPV simulation identifier if you did not use the default one.")

    # Check that the UBES was run
    if not urban_canopy_dict["bipv_scenarios"][_bipv_simulation_identifier_]["kpis_results_dict"]["has_run"]:
        raise ValueError("The KPI computation was not run. Run the simulation first.")

    # Load KPI result dictionary
    result_dict = urban_canopy_dict["bipv_scenarios"][_bipv_simulation_identifier_]["kpis_results_dict"]["kpis"]
    # Flatten the dictionary
    flatten_result_dict = flatten_kpi_dict(result_dict)  # index roof=0, facades=1, total=2


    kpi_labels_oredered = [
        "eroi",
        "primary energy payback time [year] profitability_threshold",
        "primary energy payback time [year] lifetime_investment",
        "ghg emissions intensity [kgCo2eq/kWh]",
        "ghg emissions payback time [year] profitability_threshold",
        "ghg emissions payback time [year] lifetime_investment",
        "harvested energy density [Kwh/m2] zone",
        "harvested energy density [Kwh/m2] conditioned_apartment",
        "net energy compensation",
        "economical roi",
        "economical payback time [year] profitability_threshold",
        "economical payback time [year] lifetime_investment",
        "net economical benefit [$]",
        "net economical benefit density [$/m2] zone",
        "net economical benefit density [$/m2] conditioned_apartment",
    ]

    # Get results
    results_kpis_labels = flatten_result_dict.keys()
    kpis_labels = []
    kpis_bipv_roof = []
    kpis_bipv_facades = []
    kpis_bipv_total = []

    for label in kpi_labels_oredered:
        if label in results_kpis_labels:
            kpis_labels.append(label)
            kpis_bipv_roof.append(flatten_result_dict[label][0])
            kpis_bipv_facades.append(flatten_result_dict[label][1])
            kpis_bipv_total.append(flatten_result_dict[label][2])
