"""
Functions to be run by the main to perform the different steps of teh solar radiation and BIPV simulation
"""
import logging

from utils.utils_default_values_user_parameters import default_path_simulation_folder, \
    default_path_weather_file

from utils.utils_default_values_user_parameters import default_roof_grid_size_x, default_facades_grid_size_x, \
    default_roof_grid_size_y, default_facades_grid_size_y, default_offset_dist

dev_logger = logging.getLogger("dev")
user_logger = logging.getLogger("user")


class SimFunSolarRadAndBipv:

    @staticmethod
    def generate_sensor_grid(urban_canopy_object, building_id_list=None,
                             bipv_on_roof=True,
                             bipv_on_facades=True,
                             roof_grid_size_x=default_roof_grid_size_y,
                             facades_grid_size_x=default_facades_grid_size_x,
                             roof_grid_size_y=default_roof_grid_size_y,
                             facades_grid_size_y=default_facades_grid_size_y,
                             offset_dist=default_offset_dist):
        """
        Make oriented bounding boxes of buildings in the urban canopy
        :param urban_canopy_object: urban canopy object
        :param building_id_list: list of building id to be considered
        :param bipv_on_roof: bool: default=True if True, generate sensor grid on the roof
        :param bipv_on_facades: bool: default=True if True, generate sensor grid on the facades
        :param roof_grid_size_x: number: default=1.5: grid size of the roof mesh in the x direction
        :param facades_grid_size_x: number: default=1.5: grid size of the facades mesh in the x direction
        :param roof_grid_size_y: number: default=1.5: grid size of the roof mesh in the y direction
        :param facades_grid_size_y: number: default=1.5: grid size of the facades mesh in the y direction
        :param offset_dist: number: default=0.1: offset distance to move the sensor grid from the building surface
        """

        urban_canopy_object.generate_sensor_grid_on_buildings(building_id_list=building_id_list,
                                                              bipv_on_roof=bipv_on_roof,
                                                              bipv_on_facades=bipv_on_facades,
                                                              roof_grid_size_x=roof_grid_size_x,
                                                              facades_grid_size_x=facades_grid_size_x,
                                                              roof_grid_size_y=roof_grid_size_y,
                                                              facades_grid_size_y=facades_grid_size_y,
                                                              offset_dist=offset_dist)
        user_logger.info("Honeybee SensorGrids on the buildings have been generated successfully")
        dev_logger.info("Honeybee SensorGrids on the buildings have been generated successfully")

    @staticmethod
    def run_annual_solar_irradiance_simulation(urban_canopy_object,
                                               path_simulation_folder=default_path_simulation_folder,
                                               building_id_list=None,
                                               path_weather_file=default_path_weather_file,
                                               overwrite=False, north_angle=0, silent=False):
        """
        Make oriented bounding boxes of buildings in the urban canopy
        :param urban_canopy_object: urban canopy object
        :param path_simulation_folder: path to the folder where the simulation will be run
        :param building_id_list: list of building id to be considered
        :param path_weather_file: path to the weather file
        :param overwrite: bool: default=False: if True, overwrite the existing simulation
        :param north_angle: number: default=0: number of degrees to rotate the roof mesh
        :param silent: bool: default=False: if True, run the simulation silently
        """

        urban_canopy_object.run_solar_radiation_simulation_for_buildings(
            path_simulation_folder=path_simulation_folder,
            building_id_list=building_id_list,
            path_weather_file=path_weather_file,
            overwrite=overwrite, north_angle=north_angle,
            silent=silent)
        user_logger.info("The annual solar irradiance on have been performed successfully")
        dev_logger.info("The annual solar irradiance on have been performed successfully")

    @staticmethod
    def run_bipv_harvesting_and_lca_simulation(urban_canopy_object,
                                               path_simulation_folder=default_path_simulation_folder,
                                               building_id_list=None,
                                               ):
        """
        Make oriented bounding boxes of buildings in the urban canopy
        :param urban_canopy_object: urban canopy object
        :param path_simulation_folder: path to the folder where the simulation will be run
        :param building_id_list: list of building id to be considered
        todo @Elie: add the other parameters
        """

        # urban_canopy_object.run_solar_radiation_simulation_for_buildings(path_simulation_folder=path_simulation_folder,
        #                                                                  building_id_list=building_id_list,
        #                                                                  path_weather_file=path_weather_file,
        #                                                                  overwrite=overwrite, north_angle=north_angle,
        #                                                                  silent=silent)

        # user_logger.info("The annual solar irradiance on have been performed successfully")
        # dev_logger.info("The annual solar irradiance on have been performed successfully")
