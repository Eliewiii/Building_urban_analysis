"""
Script to run for a radiation analysis of a building in a context
"""


# Import Libraries
from honeybee.model import Model
import logging

# Import EPW, context, hb model
epw_path = ""
hb_model_hbjson_path = "path"
context_hbjsom_path = "path"
# todo write the correct path


# Extract hb_model and context
hb_model_obj = Model.from_hbjson(hb_model_hbjson_path)
context = Model.from_hbjson(context_hbjsom_path)
logging.info("Extraction of context and hb_model complete")

# Since we suppose that we already have a hb_building, we suppose all the shades, faces, roofs are already defined

# PRE PROCESSING

# todo : write a function to generate points, vertices and a mesh a mesh from hb_model
#  And then returns it as a HB_sensor_grid

# todo : write a function to assign to a HB model a sensor grid and views to prepare it for the radiation simulation

# Roof
sensor_grids_obj = sensor_grids(hb_model_obj)
hb_model_obj_ready = assign_grids_views(hb_model_obj, sensor_grids_obj, views_obj)

# Facades
sensor_grids_context = sensor_grids(context)
context_ready = assign_grids_views(context, sensor_grids_context, views_context)

logging.info("Pre-processing complete")


# Run simulation

# todo : functions Recipe Settings, HB annual irradiance and HB Annual Cumulative Values
# for Roofs and Facades

hb_model_cum_radiation = cum_radiation(hb_model_obj_ready)
context_cum_radiation = cum_radiation(context_ready)