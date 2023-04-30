"""
Get list of the buildings' ids
"""

import os
import sys
import logging
import argparse
import json

# Get Appdata\local folder
local_appdata = os.environ['LOCALAPPDATA']
path_tool = os.path.join(local_appdata, "Building_urban_analysis")

# Default values
default_path_folder = os.path.join(path_tool, "Simulation_temp")
default_run_by_the_tool = False

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--folder", help="path to the folder", nargs='?',
                        default=default_path_folder)
    parser.add_argument("-t", "--tool",
                        help="Boolean telling if the code is run from an editor or externally by the batch file",
                        nargs='?',
                        default=default_run_by_the_tool)

    # Input parameter that will be given by Grasshopper
    args = parser.parse_args()

    path_folder = args.folder
    run_by_the_tool = bool(args.tool)

    # Create the folder if it does not exist
    os.makedirs(path_folder, exist_ok=True)

    # Configurate and make the logfile
    path_logger = os.path.join(path_folder, "log_report.log")

    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s",
                        handlers=[logging.FileHandler(path_logger), logging.StreamHandler(sys.stdout)])

    # logging.getLogger('name of the package').setLevel(logging.CRITICAL) todo for later

    # Add the path of scripts in the tool to sys so that the lib can be used
    if run_by_the_tool:
        sys.path.append(os.path.join(path_tool, "Scripts"))

    # # Import libraries from the tool
    # Import libraries from the tool (after as we don't know it's run from the tool or PyCharm)
    from urban_canopy.urban_canopy_methods import UrbanCanopy
    from building.building_modeled import BuildingModeled

    # Create or load the urban canopy object
    path_urban_canopy_pkl = os.path.join(path_folder, "urban_canopy.pkl")
    if os.path.isfile(path_urban_canopy_pkl):
        urban_canopy = UrbanCanopy.make_urban_canopy_from_pkl(path_urban_canopy_pkl)
        logging.info(f"An urban canopy already exist in the simulation folder, let us load it")
    else:
        urban_canopy = UrbanCanopy()
        logging.info(f"New urban canopy object was created")

    # Get the list of id of the buildings in the urban canopy
    list_id = urban_canopy.get_list_id_buildings_urban_canopy()
    logging.info(f"List of building ids created")

    # save the urban canopy object in a pickle file in the temp folder
    urban_canopy.export_urban_canopy_to_pkl(path_folder=path_folder)
    logging.info(f"Urban canopy object saved successfully")
