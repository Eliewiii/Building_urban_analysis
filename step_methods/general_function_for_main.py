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
    @staticmethod
    def make_simulation_folder(path_simulation_folder = path_simulation_temp_folder):
        """ #todo @Elie"""
        # make simulation folder
        os.makedirs(path_simulation_folder, exist_ok=True)
        # make the folder that will contain the logs of the simulation for the components in Grasshopper
        os.makedirs(os.path.join(path_simulation_folder,name_gh_components_logs_folder), exist_ok=True)
        # make the folder that will contain the temporary files of the simulation
        os.makedirs(os.path.join(path_simulation_folder,name_temporary_files_folder), exist_ok=True)


    @staticmethod
    def create_or_load_urban_canopy_object(path_simulation_folder):
        # todo @Elie, correct the function
        path_urban_canopy_pkl = os.path.join(path_simulation_folder, "urban_canopy.pkl")
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
    def save_urban_canopy_object_to_pickle(urban_canopy_object, path_simulation_folder):
        """ #todo"""
        # todo @Elie, correct the function
        urban_canopy_object.to_pkl(path_simulation_folder=path_simulation_folder)
        user_logger.info("Urban canopy object saved as pkl successfully")
        dev_logger.info("Urban canopy object saved as pkl successfully")

    @staticmethod
    def save_urban_canopy_to_json(urban_canopy_object, path_simulation_folder):
        """ todo @Elie"""
        urban_canopy_object.to_json(path_simulation_folder=path_simulation_folder)
        user_logger.info("Urban canopy object saved as json successfully")
        dev_logger.info("Urban canopy object saved as json successfully")


    @staticmethod
    def write_gh_component_user_logs(path_simulation_folder, name_gh_component,logs):
        """ todo @Elie"""
        # todo @Elie, write th elogs in path_simulation_folder/gh_components_logs/name_gh_component.log
        # gh_components_logs variable is defined in utils_general.py