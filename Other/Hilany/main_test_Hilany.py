"""
Script to run for a radiation analysis of a building in a context
"""


# Import Libraries
import os
from honeybee.model import Model
import logging

dev_logger = logging.getLogger("dev")
user_logger = logging.getLogger("user")

try:
    from ladybug_geometry.geometry3d.plane import Plane
    from ladybug_geometry.geometry3d.face import Face3D
    from ladybug_geometry.geometry3d.mesh import Mesh3D
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:  # import the core honeybee dependencies
    from honeybee.typing import clean_and_id_rad_string, clean_rad_string
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the honeybee-radiance dependencies
    from honeybee_radiance.sensorgrid import SensorGrid

except ImportError as e:
    raise ImportError('\nFailed to import honeybee_radiance:\n\t{}'.format(e))

from Other.Hilany.component_GH.HB_model_to_HB_SensorGrid_facades import hb_model_to_hb_SensorGrid_facades
from Other.Hilany.component_GH.HB_model_to_HB_SensorGrid_roofs import hb_model_to_hb_SensorGrid_roofs
from Other.Hilany.component_GH.HB_Annual_Irradiance_Simulation import hb_ann_irr_sim
from libraries_addons.solar_radiations.hb_recipe_settings import hb_recipe_settings
from Other.Hilany.component_GH.HB_Annual_Cumulative_Values import hb_ann_cum_values

# Import EPW, context, hb model


path_folder = "C:\\Users\\User\OneDrive - Technion\Documents\\test"
wea_folder = "C:\\Users\\User\AppData\Local\Building_urban_analysis\Libraries\EPW\IS_5280_A_Haifa.epw"
hb_model_facades_hbjson_path = os.path.join("C:\\Users\\User\OneDrive - Technion\Documents\\test","test_model_facades.hbjson")
hb_model_roofs_hbjson_path = os.path.join("C:\\Users\\User\OneDrive - Technion\Documents\\test","test_model_roofs.hbjson")


# Extract hb_model and context
hb_model_facades = Model.from_hbjson(hb_model_facades_hbjson_path)
hb_model_roofs = Model.from_hbjson(hb_model_roofs_hbjson_path)

# context = Model.from_hbjson(context_hbjsom_path)
user_logger.info("Extraction of context and hb_model complete")
dev_logger.info("Extraction of context and hb_model complete")

# Since we suppose that we already have a hb_building, we suppose all the shades, faces, roofs are already defined

# PRE PROCESSING
# roof
model_sensorgrid_roofs=  hb_model_to_hb_SensorGrid_roofs("SensorGrid_Roofs", hb_model_roofs, 3, 0.1, True)
# facades
model_sensorgrid_facades = hb_model_to_hb_SensorGrid_facades("SensorGrid_Facades", hb_model_facades, 3, 0.1, True)

user_logger.info("Pre-processing complete")
dev_logger.info("Pre-processing complete")

# Run simulation

path_folder_simulation = os.path.join("C:\\Users\\User\OneDrive - Technion\Documents\\test", "Radiation Simulation")
path_folder_simulation_roofs = os.path.join(path_folder_simulation, "Roofs")
path_folder_simulation_facades = os.path.join(path_folder_simulation, "facades")
# Roofs
settings_roofs = hb_recipe_settings(path_folder_simulation_roofs)
hb_annual_irr_roofs = hb_ann_irr_sim(model_sensorgrid_roofs, wea_folder, settings_roofs)
# facades
settings_facades = hb_recipe_settings(path_folder_simulation_facades)
hb_annual_irr_facades = hb_ann_irr_sim(model_sensorgrid_facades, wea_folder, settings_facades)

# HB Annual cumulative value
cum_values_roofs_direct = hb_ann_cum_values([os.path.join(path_folder_simulation_roofs, "annual_irradiance", "results",
                                                          "direct")])
cum_values_roofs_total = hb_ann_cum_values([os.path.join(path_folder_simulation_roofs, "annual_irradiance", "results",
                                                         "total")])

cum_values_facades_direct = hb_ann_cum_values([os.path.join(path_folder_simulation_facades, "annual_irradiance",
                                                            "results", "direct")])
cum_values_facades_total = hb_ann_cum_values([os.path.join(path_folder_simulation_facades, "annual_irradiance",
                                                           "results", "total")])
