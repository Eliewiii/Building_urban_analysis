"""
Script to run for a radiation analysis of a building in a context
"""


# Import Libraries
import os
from honeybee.model import Model
import logging

try:
    from ladybug_geometry.geometry3d.plane import Plane
    from ladybug_geometry.geometry3d.face import Face3D
    from ladybug_geometry.geometry3d.mesh import Mesh3D
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

from honeybee.boundarycondition import Outdoors

try:  # import the core honeybee dependencies
    from honeybee.typing import clean_and_id_rad_string, clean_rad_string
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the honeybee-radiance dependencies
    from honeybee_radiance.sensorgrid import SensorGrid

except ImportError as e:
    raise ImportError('\nFailed to import honeybee_radiance:\n\t{}'.format(e))

from Hilany.component_GH.HB_model_to_HB_SensorGrid_facades import hb_model_to_hb_SensorGrid_facades
from Hilany.component_GH.HB_model_to_HB_SensorGrid_roofs import hb_model_to_hb_SensorGrid_roofs




# Import EPW, context, hb model
#epw_path = ""

# todo write the correct path

path_folder = "C:\\Users\\User\OneDrive - Technion\Documents\\test"
hb_model_facades_hbjson_path = os.path.join("C:\\Users\\User\OneDrive - Technion\Documents\\test","test_model_facades.hbjson")
hb_model_roofs_hbjson_path = os.path.join("C:\\Users\\User\OneDrive - Technion\Documents\\test","test_model_roofs.hbjson")

#context_hbjsom_path = "path"

# Extract hb_model and context
hb_model_facades = Model.from_hbjson(hb_model_facades_hbjson_path)
hb_model_roofs = Model.from_hbjson(hb_model_roofs_hbjson_path)
#context = Model.from_hbjson(context_hbjsom_path)
logging.info("Extraction of context and hb_model complete")

# Since we suppose that we already have a hb_building, we suppose all the shades, faces, roofs are already defined

# PRE PROCESSING
# Roof
model_sensorgrid_roofs=hb_model_to_hb_SensorGrid_roofs("SensorGrid_Roofs",hb_model_roofs,3,0.1,True)
# Facades
model_sensorgrid_facades=hb_model_to_hb_SensorGrid_facades("SensorGrid_Facades",hb_model_facades,3,0.1,True)

logging.info("Pre-processing complete")

# Run simulation

# todo : functions Recipe Settings, HB annual irradiance and HB Annual Cumulative Values
# for Roofs and Facades

#hb_model_cum_radiation = cum_radiation(hb_model_obj_ready)
#context_cum_radiation = cum_radiation(context_ready)