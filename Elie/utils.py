import os
from urban_canopy.urban_canopy import UrbanCanopy
import logging
import numpy as np

from time import time
from math import sqrt, atan, pi, log

import pyvista as pv

from copy import deepcopy

from ladybug_geometry.geometry3d import Vector3D, Point3D, Face3D

from honeybee.model import Model
from honeybee.face import Face
from honeybee.shade import Shade
from ladybug_geometry.bounding import bounding_domain_x, bounding_domain_y, bounding_rectangle_extents, _orient_geometry
# from building_ubem._footprin_and_envelop_manipulation import extrude_lb_face_to_hb_room


# Inputs
path_folder_test_simulation = "C:\\Users\\elie-medioni\\OneDrive\\OneDrive - Technion\\BUA\\Elie\\Simulation_test"
path_folder_hbjson = "C:\\Users\\elie-medioni\\OneDrive\\OneDrive - Technion\\BUA\\Elie\\Samples\\HB_model"

# Inputs
# path_folder_simulation = "C:\\Users\\elie-medioni\\OneDrive\\OneDrive - Technion\\BUA\\Elie\\Simulation_test"

local_appdata = os.environ['LOCALAPPDATA']
path_folder_simulation = os.path.join(local_appdata, "Building_urban_analysis","Simulation_temp")
path_urban_canopy_pkl = os.path.join(path_folder_simulation, "urban_canopy.pkl")