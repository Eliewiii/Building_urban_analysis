"""
Script to evaluate the performance of the RadiativeSurfaceManager VF computation with Radiance,
using various parameters for parallel computing for large datasets.
"""
import os
import pytest

from pyvista import PolyData

from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

from ..vf_computation_with_radiance import RadiativeSurfaceManager
from ..vf_computation_with_radiance.utils import create_folder
from ..vf_computation_with_radiance.radiative_surface.radiative_surface_manager_class import \
    flatten_table_to_lists
