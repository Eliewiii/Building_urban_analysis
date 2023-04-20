import os
import logging
import pickle

from honeybee.model import Model
from honeybee.room import Room


# Default values
default_minimum_vf_criterion_for_shadow_calculation = 0.01  # minimum view factor between surfaces to be considered
# as context surfaces in the first pass of the algorithm for shading computation