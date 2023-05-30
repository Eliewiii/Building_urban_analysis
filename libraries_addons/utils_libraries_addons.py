import logging
from math import pi,sqrt,atan,log
import numpy as np
import pyvista as pv
from shapely.geometry import Polygon
import geopandas as gpd
# Ladybug
from ladybug_geometry.geometry3d.pointvector import Point3D, Vector3D
from ladybug_geometry.geometry3d.face import Face3D
from ladybug_geometry.geometry3d.polyface import Polyface3D
from ladybug_geometry.bounding import bounding_domain_x, bounding_domain_y, bounding_rectangle_extents, _orient_geometry
# Dragonfly
import dragonfly
from dragonfly.building import Building
# Honeybee
from honeybee.room import Room
from honeybee.boundarycondition import Outdoors
from honeybee_energy.lib.constructionsets import construction_set_by_identifier
from honeybee_energy.lib.programtypes import program_type_by_identifier
# Solar radiation with radiance
from lbt_recipes.recipe import Recipe
from ladybug.futil import write_to_file
from honeybee.config import folders
from honeybee_radiance.postprocess.annualdaylight import _process_input_folder
from pollination_handlers.outputs.helper import read_sensor_grid_result

default_tolerance = 0.01
default_height = 9.
default_elevation=0.
default_tol=0.5