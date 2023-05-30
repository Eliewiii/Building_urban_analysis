
from mains_tool.utils_general import *

from honeybee.model import Model
from honeybee.room import Room

from building.building_basic import BuildingBasic
from building.building_modeled import BuildingModeled

from libraries_addons.extract_gis_files import extract_gis

from typology.typology import Typology

# Default values
default_minimum_vf_criterion_for_shadow_calculation = 0.01  # minimum view factor between surfaces to be considered
# as context surfaces in the first pass of the algorithm for shading computation