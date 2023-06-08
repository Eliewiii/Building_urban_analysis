
import numpy

from mains_tool.utils_general import *

from honeybee.model import Model
from honeybee.room import Room

from building.building_basic import BuildingBasic
from building.building_modeled import BuildingModeled

from libraries_addons.extract_gis_files import extract_gis

from typology.typology import Typology

from urban_canopy.urban_canopy_additional_functions import UrbanCanopyAdditionalFunction

from solar_panel.pv_panel import PvPanel
from solar_panel.pv_panel_technology import PvPanelTechnology

from libraries_addons.solar_panels.useful_functions_solar_panel import write_to_csv_arr

# Default values
default_minimum_vf_criterion_for_shadow_calculation = 0.01  # minimum view factor between surfaces to be considered
# as context surfaces in the first pass of the algorithm for shading computation
