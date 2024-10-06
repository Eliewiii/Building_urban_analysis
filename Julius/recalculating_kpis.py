import json
import logging
from bua.utils.utils_import_simulation_steps_and_config_var import *

def recalculate_kpis():

    #load urban canopy object
    path_urban_canopy_object = r"C:\Users\julius.jandl\OneDrive - Technion\Julius PhD\Paper\results\Simulation_September 2024\EROI 1.5\Simulation_temp"
    urban_canopy_object = SimulationCommonMethods.create_or_load_urban_canopy_object(path_simulation_folder = path_urban_canopy_object)


