from ladybug_geometry.geometry3d import Vector3D, Polyface3D
from honeybee.room import Room
import logging
from shapely.geometry import Polygon
from math import pi
import dragonfly
from ladybug_geometry.geometry3d.pointvector import Point3D, Vector3D
from ladybug_geometry.geometry3d.face import Face3D
from ladybug_geometry.geometry3d.polyface import Polyface3D
from ladybug_geometry.bounding import bounding_domain_x, bounding_domain_y, bounding_rectangle_extents, _orient_geometry
from honeybee.boundarycondition import Outdoors
from dragonfly.building import Building
from honeybee_energy.lib.constructionsets import construction_set_by_identifier
from honeybee_energy.lib.programtypes import program_type_by_identifier