"""
Extract add buildings to the urban canopy from hbjson files.
"""

import os
import sys
import logging
import argparse
import json


# Get Appdata\local folder
local_appdata = os.environ['LOCALAPPDATA']
path_tool = os.path.join(local_appdata, "Building_urban_analysis")
parser = argparse.ArgumentParser()

# Default values
default_path_folder_simulation = os.path.join(path_tool, "Simulation_temp")
default_make_hb_model_envelops = False
default_run_by_the_tool = False
default_are_buildings_target = True
name_hbjson_directory = "hbjsons_to_add"



if __name__ == "__main__":
    parser.add_argument("-f", "--folder", help="path to the simulation folder", nargs='?',
                        default=default_path_folder_simulation)
    parser.add_argument("-e", "--hbenv",
                        help="Boolean telling if a HB Model containing the envelop of all buildings should be generated",
                        nargs='?',
                        default=default_make_hb_model_envelops)
    parser.add_argument("-tar", "--target",
                        help="Boolean telling if the buildings to add are target buildings",
                        nargs='?',
                        default=default_are_buildings_target)
    parser.add_argument("-t", "--tool",
                        help="Boolean telling if the code is run from an editor or externally by the batch file",
                        nargs='?',
                        default=default_run_by_the_tool)

    args = parser.parse_args()
    path_folder_simulation = args.folder
    path_folder_hbjson = os.path.join(path_folder_simulation, name_hbjson_directory)
    make_hb_model_envelops = bool(args.hbenv)
    are_buildings_targets = bool(args.target)
    run_by_the_tool = bool(args.tool)

    os.makedirs(path_folder_simulation, exist_ok=True)
    path_logger = os.path.join(path_folder_simulation, "log_report.log")

    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s",
                        handlers=[logging.FileHandler(path_logger), logging.StreamHandler(sys.stdout)])

    #add_path_to_scripts in the tool to sys so that the lib can be used
    def update_script_path_venv():
        if run_by_the_tool:
            sys.path.append(os.path.join(path_tool, "Scripts"))

    update_script_path_venv()

    # Import the urban canopy methods, needs to be after the update_script_path_venv(), otherwise it will not find the lib
    # when executed from Grasshopper
    from urban_canopy.urban_canopy import UrbanCanopy

    # Create or load the urban canopy object
    path_urban_canopy_pkl = os.path.join(path_folder_simulation, "urban_canopy.pkl")
    if os.path.isfile(path_urban_canopy_pkl):
        urban_canopy = UrbanCanopy.make_urban_canopy_from_pkl(path_urban_canopy_pkl)
        logging.info("An urban canopy already exist in the simulation folder, the input GIS will be added to it")
    else:
        urban_canopy = UrbanCanopy()
        logging.info("New urban canopy object was created")



    # Add the buildings in the hbjson files to the urban canopy
    urban_canopy.add_buildings_from_hbjson_to_dict(path_directory_hbjson=path_folder_hbjson, are_buildings_targets=are_buildings_targets)
    logging.info("Building(s) from hbjson added to the urban canopy successfully")
    # generate the hb model that contains all the building envelopes to plot in Grasshopper
    if make_hb_model_envelops:
        urban_canopy.make_HB_model_envelops_from_buildings(path_folder=path_folder_simulation)
        logging.info("HB model for the building envelop created successfully")


    # save the urban canopy object in a pickle file in the temp folder
    urban_canopy.export_urban_canopy_to_pkl(path_folder=path_folder_simulation)
    logging.info("Urban canopy object saved successfully")
    # test