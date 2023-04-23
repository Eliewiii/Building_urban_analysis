import os
import sys
import shutil
import logging
import argparse
import json
import shapely
import geopandas as gpd
from math import sqrt, isnan

import dragonfly
from honeybee.model import Model
from ladybug_geometry.geometry3d import Point3D, Face3D, Vector3D

from libraries_addons.hb_model_addons import elevation_and_height_from_HB_model, make_LB_face_footprint_from_HB_model
from libraries_addons.lb_face_addons import make_LB_polyface3D_oriented_bounding_box_from_LB_face3D_footprint, \
    LB_face_footprint_to_lB_polyface3D_extruded_footprint
from libraries_addons.hb_rooms_addons import LB_face_footprint_to_elevated_HB_room_envelop
from libraries_addons.context_filter_algorithm.context_filter_first_pass import is_bounding_box_context_using_mvfc_criterion

default_gis_attribute_key_dict = {
    "building_id_key_gis": [],
    "name": ["name", "full_name_"],
    "age": ["age", "date"],
    "typology": ["typo", "typology", "type", "Typology"],
    "elevation": ["minheight"],
    "height": ["height", "Height", "govasimple"],
    "number of floor": ["number_floor", "nb_floor", "mskomot"],
    "group": ["group"]
}
