"""
Extract the GIS file and convert it into a hb model that can be read and plotted by Grasshopper.
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
default_path_gis = os.path.join(path_tool, "Libraries", "GIS", "gis_typo_id_extra_small")
default_folder_gis_extraction = os.path.join(path_tool, "Simulation_temp")
default_unit = "m"
default_additional_gis_attribute_key_dict = None
default_move_buildings_to_origin = False
default_run_by_the_tool = False

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-g", "--gis", help="path to gis file", nargs='?', default=default_path_gis)
    parser.add_argument("-f", "--folder", help="path to the simulation folder", nargs='?',
                        default=default_folder_gis_extraction)
    parser.add_argument("-u", "--unit", help="unit of the GIS", nargs='?', default=default_unit)
    parser.add_argument("-d", "--dic", help="path to the additional key dictionary", nargs='?',
                        default=default_additional_gis_attribute_key_dict)
    parser.add_argument("-m", "--mov", help="Boolean telling if building should be moved to the origin", nargs='?',
                        default=default_move_buildings_to_origin)
    parser.add_argument("-t", "--tool",
                        help="Boolean telling if the code is run from an editor or externally by the batch file",
                        nargs='?',
                        default=default_run_by_the_tool)

    args = parser.parse_args()

    # Input parameter that will be given by Grasshopper
    path_gis = args.gis
    unit = args.unit
    path_folder_gis_extraction = args.folder
    path_additional_gis_attribute_key_dict = args.dic
    move_buildings_to_origin = bool(args.mov)
    run_by_the_tool = bool(args.tool)

    # Create the folder if it does not exist
    os.makedirs(path_folder_gis_extraction, exist_ok=True)
    # Configurate and make the logfile
    path_logger = os.path.join(path_folder_gis_extraction, "log_report.log")

    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s",
                        handlers=[logging.FileHandler(path_logger), logging.StreamHandler(sys.stdout)])

    # logging.getLogger('name of the package').setLevel(logging.CRITICAL) todo for later

    # Add the path of scripts in the tool to sys so that the lib can be used
    if run_by_the_tool:
        sys.path.append(os.path.join(path_tool, "Scripts"))
        # # Import libraries from the tool
    # Import libraries from the tool (after as we don't know it's run from the tool or PyCharm)
    from urban_canopy.urban_canopy import UrbanCanopy

    # Create or load the urban canopy object
    path_urban_canopy_pkl = os.path.join(path_folder_gis_extraction, "urban_canopy.pkl")
    if os.path.isfile(path_urban_canopy_pkl):
        urban_canopy = UrbanCanopy.make_urban_canopy_from_pkl(path_urban_canopy_pkl)
        logging.info(f"An urban canopy already exist in the simulation folder, the input GIS will be added to it")
    else:
        urban_canopy = UrbanCanopy()
        logging.info(f"New urban canopy object was created")

    # Get the building_id_key_gis if it is given in the additional_gis_attribute_key_dict
    building_id_key_gis = "idbinyan"  # default value, todo: take it as an argument as well
    additional_gis_attribute_key_dict = None
    # check if given in the additional_gis_attribute_key_dict
    if default_additional_gis_attribute_key_dict and os.path.isfile(path_additional_gis_attribute_key_dict):
        with open(path_additional_gis_attribute_key_dict, "r") as f:
            additional_gis_attribute_key_dict = json.load(f)
            if "building_id_key_gis" in additional_gis_attribute_key_dict:
                building_id_key_gis = additional_gis_attribute_key_dict["building_id_key_gis"]

    # Add the 2D GIS to the urban canopy
    urban_canopy.add_buildings_from_2D_GIS_to_dict(path_gis, building_id_key_gis, unit, additional_gis_attribute_key_dict)
    logging.info(f"Builing geometries extracted from the GIS file successfully")
    # Move the buildings to the origin if asked
    if move_buildings_to_origin or urban_canopy.moving_vector_to_origin is not None:
        urban_canopy.move_buildings_to_origin()
    # generate the hb model that contains all the building envelopes to plot in Grasshopper
    urban_canopy.make_HB_model_envelops_from_buildings(path_folder=path_folder_gis_extraction)
    logging.info(f"HB model for the building envelop created successfully")
    # save the urban canopy object in a pickle file in the temp folder
    urban_canopy.export_urban_canopy_to_pkl(path_folder=path_folder_gis_extraction)
    logging.info(f"Urban canopy object saved successfully")
