"""
Functions used in the second pass of the context filter algorithm for shading, using ray tracing to detect obstruction.
"""
import numpy as np
import pyvista as pv

from math import sqrt, atan, log, pi

from honeybee.face import Face
from ladybug_geometry.geometry3d import Face3D





