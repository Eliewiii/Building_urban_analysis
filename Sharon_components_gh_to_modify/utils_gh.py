import os
import sys
import logging
import argparse
import json

# # Import libraries from the tool
# Import libraries from the tool (after as we don't know if it runs from the tool or PyCharm)
from urban_canopy.urban_canopy_methods import UrbanCanopy


# Get Appdata\local folder
local_appdata = os.environ['LOCALAPPDATA']
path_tool = os.path.join(local_appdata, "Building_urban_analysis")
parser = argparse.ArgumentParser()

# Default values
default_path_folder_simulation = os.path.join(path_tool, "Simulation_temp")
default_make_hb_model_envelops = False
default_run_by_the_tool = False
name_hbjson_directory = "hbjsons_to_add"

default_path_gis = os.path.join(path_tool, "Libraries", "GIS", "gis_typo_id_extra_small")
default_folder_gis_extraction = os.path.join(path_tool, "Simulation_temp")
default_unit = "m"
default_additional_gis_attribute_key_dict = None
default_move_buildings_to_origin = False
default_run_by_the_tool = False

name_bounding_box_hbjson = "bounding_boxes.hbjson"