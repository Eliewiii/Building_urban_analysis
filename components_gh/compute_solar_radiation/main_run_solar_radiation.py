"""
Run solar radiation on buildings of urban canopy
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
default_path_folder_simulation = os.path.join(path_tool, "Simulation_temp")
default_path_weather_file = os.path.join(path_tool, "Libraries", "EPW", "IS_5280_A_Haifa.epw")
default_grid_size = 1
default_offset_dist = 0.1
default_run_by_the_tool = False

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--folder", help="path to the simulation folder", nargs='?',
                        default=default_path_folder_simulation)
    parser.add_argument("-w", "--epw", help="path to the weather file", nargs='?',
                        default=default_path_weather_file)
    parser.add_argument("-g", "--grid", help="Number for the size of the test grid", nargs='?',
                        default=default_grid_size)
    parser.add_argument("-o", "--off",
                        help="Number for the distance to move points from the surfaces of the geometry of the model",
                        nargs='?',
                        default=default_offset_dist)
    parser.add_argument("-t", "--tool",
                        help="Boolean telling if the code is run from an editor or externally by the batch file",
                        nargs='?',
                        default=default_run_by_the_tool)

    # Input parameter that will be given by Grasshopper
    args = parser.parse_args()

    path_folder_simulation = args.folder
    path_radiation_folder = os.path.join(path_folder_simulation, "Radiation simulation")
    path_weather_file = args.epw
    grid_size = float(args.grid)
    offset_dist = float(args.off)
    run_by_the_tool = bool(args.tool)

    # Create the folder if it does not exist
    os.makedirs(path_folder_simulation, exist_ok=True)

    # Configurate and make the logfile
    path_logger = os.path.join(path_folder_simulation, "log_report.log")

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
    path_urban_canopy_pkl = os.path.join(path_folder_simulation, "urban_canopy.pkl")
    if os.path.isfile(path_urban_canopy_pkl):
        urban_canopy = UrbanCanopy.make_urban_canopy_from_pkl(path_urban_canopy_pkl)
        logging.info(f"An urban canopy already exist in the simulation folder, let us load it")
    else:
        urban_canopy = UrbanCanopy()
        logging.info(f"New urban canopy object was created")

    # Run the annual solar radiation simulation on each building targeted of the urban canopy
    urban_canopy.radiation_simulation_urban_canopy(path_radiation_folder, path_weather_file, ['unnamed_88b30172'], grid_size, offset_dist)
    logging.info(f"Solar radiation simulation run successfully")

    # generate the hb model that contains all the building envelopes to plot in Grasshopper
    urban_canopy.make_HB_model_envelops_from_buildings(path_folder=path_folder_simulation)
    logging.info(f"HB model for the building envelop created successfully")

    urban_canopy.export_urban_canopy_to_pkl_and_json(path_folder=path_folder_simulation)
    logging.info(f"Urban canopy attributes saved successfully")
