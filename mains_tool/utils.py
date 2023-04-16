import os
import sys
import logging
import argparse
from datetime import datetime
import json
# Import libraries from the tool (after as we don't know it's run from the tool or PyCharm)
from urban_canopy import urban_canopy_methods

#urban_canopy = UrbanCanopy()
currentDirectory = os.getcwd()
parser = argparse.ArgumentParser()
args = parser.parse_args()
path_gis = args.gis
unit = args.unit
#urban_canopy = UrbanCanopy()

#Get Appdata\local folder
local_appdata = os.environ['LOCALAPPDATA']
path_tool = os.path.join(local_appdata, "Building_urban_analysis")

# Default values
default_path_gis = os.path.join(path_tool, "Libraries", "GIS", "gis_typo_id_extra_small")
default_folder_gis_extraction = os.path.join(path_tool, "Simulation_temp")
default_unit = "m"
default_additional_gis_attribute_key_dict, additional_gis_attribute_key_dict = None
default_move_buildings_to_origin, default_run_by_the_tool = False
#building_id_key_gis - given in the additional_gis_attribute_key_dict
#todo: take it as an argument as well
#default value
building_id_key_gis = "idbinyan"