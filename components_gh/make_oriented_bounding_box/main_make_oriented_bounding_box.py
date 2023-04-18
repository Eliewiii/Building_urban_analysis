"""
Extract add buildings to the urban canopy from hbjson files.
"""

import os
import sys
import logging
import argparse

# Get Appdata\local folder
local_appdata = os.environ['LOCALAPPDATA']
path_tool = os.path.join(local_appdata, "Building_urban_analysis")

# Default values
default_path_folder_simulation = os.path.join(path_tool, "Simulation_temp")
default_run_by_the_tool = False

name_bounding_box_hbjson = "bounding_boxes.hbjson"

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--folder", help="path to the simulation folder", nargs='?',
                        default=default_path_folder_simulation)
    parser.add_argument("-t", "--tool",
                        help="Boolean telling if the code is run from an editor or externally by the batch file",
                        nargs='?',
                        default=default_run_by_the_tool)

    args = parser.parse_args()

    # Input parameter that will be given by Grasshopper

    path_folder_simulation = args.folder
    run_by_the_tool = bool(args.tool)

    # Create the folder if it does not exist
    os.makedirs(path_folder_simulation, exist_ok=True)
    # Configurate and make the logfile
    path_logger = os.path.join(path_folder_simulation, "log_report.log")

    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s",
                        handlers=[logging.FileHandler(path_logger), logging.StreamHandler(sys.stdout)])

    # Add the path of scripts in the tool to sys so that the lib can be used
    if run_by_the_tool:
        sys.path.append(os.path.join(path_tool, "Scripts"))
        # # Import libraries from the tool
    # Import libraries from the tool (after as we don't know if it runs from the tool or PyCharm)
    from urban_canopy.urban_canopy_methods import UrbanCanopy

    # Create or load the urban canopy object
    path_urban_canopy_pkl = os.path.join(path_folder_simulation, "urban_canopy.pkl")
    if os.path.isfile(path_urban_canopy_pkl):
        urban_canopy = UrbanCanopy.make_urban_canopy_from_pkl(path_urban_canopy_pkl)
        logging.info(f"An urban canopy already exist in the simulation folder, the input GIS will be added to it")
    else:
        urban_canopy = UrbanCanopy()
        logging.info(f"New urban canopy object was created")

    # Add the buildings in the hbjson files to the urban canopy
    urban_canopy.make_oriented_bounding_boxes_of_buildings(path_folder=path_folder_simulation,
                                                           hbjson_name=name_bounding_box_hbjson)
    logging.info("The bounding boxes of the buildings were created successfully")
    # save the urban canopy object in a pickle file in the temp folder
    urban_canopy.export_urban_canopy_to_pkl(path_folder=path_folder_simulation)
    logging.info("Urban canopy object saved successfully")
    # test
