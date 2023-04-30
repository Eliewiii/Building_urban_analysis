import os
import logging
import pickle
import json

from honeybee.model import Model
from honeybee.room import Room
from building.building_basic import BuildingBasic
from building.building_modeled import BuildingModeled
from Elie.gis.extract_gis import extract_gis
from typology.typology import Typology

# Default values
default_minimum_vf_criterion_context_filter_first_pass_shading = 0.01  # minimum view factor between surfaces to be considered
# as context surfaces in the first pass of the algorithm for shading computation

name_urban_canopy_json_file = "urban_canopy.json"