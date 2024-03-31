"""
Common methods to perform the energy simulation of a building with EnergyPlus
"""

import os
import shutil
import logging

from time import time

from urban_canopy.urban_canopy import UrbanCanopy

from utils.utils_default_values_user_parameters import default_path_simulation_folder, \
    default_path_weather_file, \
    default_path_hbjson_simulation_parameter_file, default_cop_heating, default_cop_cooling

user_logger = logging.getLogger("user")  # f"{__name__} user"
dev_logger = logging.getLogger("dev")  # f"{__name__} dev"


class UrbanBuildingEnergySimulationFunctions:

    @staticmethod
    def load_epw_and_hb_simulation_parameters_for_ubes_in_urban_canopy(urban_canopy_obj: UrbanCanopy,
                                                                       path_simulation_folder=default_path_simulation_folder,
                                                                       path_hbjson_simulation_parameter_file=default_path_hbjson_simulation_parameter_file,
                                                                       path_file_epw=default_path_weather_file,
                                                                       ddy_file=None,
                                                                       overwrite=False):
        """
        Load the simulation parameters from the simulation parameter file and check and correct them if needed.
        :param urban_canopy_obj: UrbanCanopy object
        :param path_simulation_folder: str, path to the simulation folder
        :param path_hbjson_simulation_parameter_file: str, path to the simulation parameter file
        :param path_weather_file: str, path to the weather file
        :param ddy_file: str, path to the ddy file
        :param overwrite: bool, if True, overwrite the existing simulation parameter file
        """

        urban_canopy_obj.load_epw_and_hb_simulation_parameters_for_ubes(
            path_simulation_folder=path_simulation_folder,
            path_hbjson_simulation_parameter_file=path_hbjson_simulation_parameter_file,
            path_file_epw=path_file_epw, ddy_file=ddy_file, overwrite=overwrite)

        # user_logger.info("")
        dev_logger.info("EPW file and HB simulation parameters loaded")
        return

    @staticmethod
    def generate_idf_files_for_ubes_with_openstudio_in_urban_canopy(urban_canopy_obj: UrbanCanopy,
                                                                    path_simulation_folder=default_path_simulation_folder,
                                                                    building_id_list=None,
                                                                    overwrite=False,
                                                                    silent=False):
        """
        Generate idf files of buildings in the Urban Canopy through OpenStudio for further simulation with EnergyPlus.
        :param urban_canopy_obj: UrbanCanopy object
        :param path_simulation_folder: str, path to the simulation folder
        :param building_id_list: list of str, list of building id to run the simulation on
        :param overwrite: bool, if True, overwrite the existing idf files
        :param silent: bool, if True, do not print the progress
        """

        urban_canopy_obj.generate_idf_files_for_ubes_with_openstudio(
            path_simulation_folder=path_simulation_folder,
            building_id_list=building_id_list,
            overwrite=overwrite,
            silent=silent)

        user_logger.info("The idf files for the UBES were generated")
        dev_logger.info("The idf files for the UBES were generated")

        return

    @staticmethod
    def run_idf_files_with_energyplus_for_ubes_in_urban_canopy(urban_canopy_obj: UrbanCanopy,
                                                               path_simulation_folder=default_path_simulation_folder,
                                                               building_id_list=None,
                                                               overwrite=False,
                                                               silent=False,
                                                               run_in_parallel=False):
        """
        Run idf files of buildings in the Urban Canopy through EnergyPlus
        :param urban_canopy_obj: UrbanCanopy object
        :param path_simulation_folder: str, path to the simulation folder
        :param building_id_list: list of str, list of building id to run the simulation on
        :param overwrite: bool, if True, overwrite the existing idf files
        :param silent: bool, if True, do not print the progress
        :param run_in_parallel: bool, True if the idf files should be run in parallel
        :return total_duration: float, total duration of the simulation
        :return duration_dict: dict, duration of the simulation for each building
        """
        timer = time()

        duration_dict = urban_canopy_obj.run_idf_files_for_ubes_with_energyplus(
            path_simulation_folder=path_simulation_folder,
            building_id_list=building_id_list,
            overwrite=overwrite,
            silent=silent,
            run_in_parallel=run_in_parallel)

        tot_duration = time() - timer

        user_logger.info("EnergyPlus simulation was run")
        dev_logger.info("EnergyPlus simulation was run")

        return tot_duration, duration_dict

    @staticmethod
    def extract_results_from_ep_simulation(urban_canopy_obj: UrbanCanopy,
                                           path_simulation_folder=default_path_simulation_folder,
                                           cop_heating=default_cop_heating, cop_cooling=default_cop_cooling):

        urban_canopy_obj.extract_ubes_results(path_simulation_folder=path_simulation_folder,
                                                            cop_heating=cop_heating, cop_cooling=cop_cooling)

        user_logger.info("UBES results were extracted")
        dev_logger.info("UBES results were extracted")
        return
