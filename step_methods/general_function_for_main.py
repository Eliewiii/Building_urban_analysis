"""
Common methods to most of the simulations
"""

import os
import logging

from urban_canopy_pack.urban_canopy import UrbanCanopy
from utils.utils_configuration import path_simulation_temp_folder,name_gh_components_logs_folder,name_temporary_files_folder

user_logger = logging.getLogger("user")  # f"{__name__} user"
dev_logger = logging.getLogger("dev")  # f"{__name__} dev"

class SimulationCommonMethods:
    # todo @Sharon: should we really make global variables?, can it interfere with some parameters with the same name
    @staticmethod
    def make_simulation_folder(path_folder_simulation = path_simulation_temp_folder):
        """ #todo @Elie"""
        # make simulation folder
        os.makedirs(path_folder_simulation, exist_ok=True)
        # make the folder that will contain the logs of the simulation for the components in Grasshopper
        os.makedirs(os.path.join(path_folder_simulation,name_gh_components_logs_folder), exist_ok=True)
        # make the folder that will contain the temporary files of the simulation
        os.makedirs(os.path.join(path_folder_simulation,name_temporary_files_folder), exist_ok=True)


    @staticmethod
    def create_or_load_urban_canopy_object(path_folder_simulation):
        # todo @Elie, correct the function
        path_urban_canopy_pkl = os.path.join(path_folder_simulation, "urban_canopy.pkl")
        if os.path.isfile(path_urban_canopy_pkl):
            urban_canopy = UrbanCanopy.make_urban_canopy_from_pkl(path_urban_canopy_pkl)
            user_logger.info("An urban canopy already exist in the simulation folder, the input GIS will be added to it")
            dev_logger.info("An urban canopy already exist in the simulation folder, the input GIS will be added to it")
        else:
            urban_canopy = UrbanCanopy()
            user_logger.info("New urban canopy object was created")
            dev_logger.info("New urban canopy object was created")
        return urban_canopy

    @staticmethod
    def save_urban_canopy_object_to_pickle(urban_canopy_object, path_folder_simulation):
        """ #todo"""
        # todo @Elie, correct the function
        urban_canopy_object.export_urban_canopy_to_pkl(path_folder_simulation=path_folder_simulation)
        user_logger.info("Urban canopy object saved as pkl successfully")
        dev_logger.info("Urban canopy object saved as pkl successfully")

    @staticmethod
    def save_urban_canopy_to_json(urban_canopy_object, path_folder_simulation):
        """ todo @Elie"""
        urban_canopy_object.export_urban_canopy_to_json(path_folder_simulation=path_folder_simulation)
        user_logger.info("Urban canopy object saved as json successfully")
        dev_logger.info("Urban canopy object saved as json successfully")


    @staticmethod
    def write_gh_component_user_logs(path_folder_simulation, name_gh_component,logs):
        """ todo @Elie"""
        # todo @Elie, write th elogs in path_folder_simulation/gh_components_logs/name_gh_component.log
        # gh_components_logs variable is defined in utils_general.py