import os
import sys
import logging
import argparse
from datetime import datetime
import json


#parser = argparse.ArgumentParser()  # todo @Sharon, I don't think we can use this function here, it should be used on the main script, not on the utils script
# args = parser.parse_args() # todo ; to delete
# path_gis = args.gis
# unit = args.unit

#Get Appdata\local folder
local_appdata = os.environ['LOCALAPPDATA']
path_tool = os.path.join(local_appdata, "Building_urban_analysis")

# Default values
default_path_gis = os.path.join(path_tool, "Libraries", "GIS", "gis_typo_id_extra_small")
default_folder_simulation = os.path.join(path_tool, "Simulation_temp")
default_unit = "m"
default_additional_gis_attribute_key_dict, additional_gis_attribute_key_dict = None
default_move_buildings_to_origin = False
#building_id_key_gis - given in the additional_gis_attribute_key_dict
#todo: take it as an argument as well
#default value
building_id_key_gis = "idbinyan"  # todo: change name to default_building_id_key_gis