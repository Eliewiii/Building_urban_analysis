"""Read the results of the KPI Simulation.
    Inputs:
        path_simulation_folder_: Path to the folder. By default, the code will be run in
                                Appdata\Local\Building_urban_analysis\Simulation_temp
        _bipv_simulation_identifier_: Identifier of the BIPV simulation. If not provided, the code will read
            the results of the last simulation.
        _run : Plug a boolean toggle to True to run the code and display the results.
    Output:
        kpis_label : list of the eend energy use categories shown in the results
        kpis_bipv_roof : list of the kpis for the roof BIPV.
        kpis_bipv_facades : list of the kpis for the facades BIPV.
        kpis_bipv_total : list of the kpis for the total BIPV.
"""

__author__ = "Elie"
__version__ = "2024.04.07"

ghenv.Component.Name = "BUA Read Kpis Results"
ghenv.Component.NickName = 'ReadUKPIsResults'
ghenv.Component.Category = 'BUA'
ghenv.Component.SubCategory = '6 :: Solar Radiation and BIPV'

import json
import os


def clean_path(path):
    path = path.replace("\\", "/")
    return (path)


labels = ["eroi", "primary energy payback time [year]", "ghg emissions intensity [kgCo2eq/kWh]",
          "ghg emissions payback time [year]", "net energy compensation", "net economical benefit [$]",
          "economical payback time [year]"]

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

    print(urban_canopy_dict["bipv_scenarios"][_bipv_simulation_identifier_]["kpis_results_dict"])
    # Check that the UBES was run
    if not urban_canopy_dict["bipv_scenarios"][_bipv_simulation_identifier_]["kpis_results_dict"]["has_run"]:
        raise ValueError("The KPI computation was not run. Run the simulation first.")

    result_dict = urban_canopy_dict["bipv_scenarios"][_bipv_simulation_identifier_]["kpis_results_dict"]["kpis"]
    # Init
    end_uses_energy_consumption = []

    # Get results
    kpis_labels = labels
    kpis_bipv_roof = []
    kpis_bipv_facades = []
    kpis_bipv_total = []

    for label in kpis_labels:
        kpis_bipv_roof.append(result_dict[label]["roof"])
        kpis_bipv_facades.append(result_dict[label]["facades"])
        kpis_bipv_total.append(result_dict[label]["total"])

    # Take care of KPIs with densities
    labels.append("zone harvested energy density [Kwh/m2]")
    kpis_bipv_roof.append(result_dict["harvested energy density [Kwh/m2]"]["zone"]["roof"])
    kpis_bipv_facades.append(result_dict["harvested energy density [Kwh/m2]"]["zone"]["facades"])
    kpis_bipv_total.append(result_dict["harvested energy density [Kwh/m2]"]["zone"]["total"])
    labels.append("conditioned apartment harvested energy density [Kwh/m2]")
    kpis_bipv_roof.append(result_dict["harvested energy density [Kwh/m2]"]["conditioned_apartment"]["roof"])
    kpis_bipv_facades.append(result_dict["harvested energy density [Kwh/m2]"]["conditioned_apartment"][
            "facades"])
    kpis_bipv_total.append(result_dict["harvested energy density [Kwh/m2]"]["conditioned_apartment"]["total"])
    labels.append("zone net economical benefit density [$/m2]]")
    kpis_bipv_roof.append(result_dict["net economical benefit density [$/m2]"]["zone"]["roof"])
    kpis_bipv_facades.append(result_dict["net economical benefit density [$/m2]"]["zone"]["facades"])
    kpis_bipv_total.append(result_dict["net economical benefit density [$/m2]"]["zone"]["total"])
    labels.append("conditioned apartment net economical benefit density [$/m2]")
    kpis_bipv_roof.append(result_dict["net economical benefit density [$/m2]"]["conditioned_apartment"][
                              "roof"])
    kpis_bipv_facades.append(result_dict["net economical benefit density [$/m2]"]["conditioned_apartment"][
                                 "facades"])
    kpis_bipv_total.append(result_dict["net economical benefit density [$/m2]"]["conditioned_apartment"][
                               "total"])
