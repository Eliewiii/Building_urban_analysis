"""
Functions to be run by the main to perform the different steps of teh solar radiation and BIPV simulation
"""
import logging

from utils.utils_default_values_user_parameters import default_path_simulation_folder, \
    default_path_weather_file

from utils.utils_default_values_user_parameters import default_roof_grid_size_x, default_facades_grid_size_x, \
    default_roof_grid_size_y, default_facades_grid_size_y, default_offset_dist

from utils.utils_default_values_user_parameters import default_path_pv_tech_dictionary_folder, default_id_pv_tech_roof, \
    default_id_pv_tech_facades, default_minimum_panel_eroi, default_start_year, default_end_year, \
    default_efficiency_computation_method, default_replacement_scenario, default_replacement_frequency_in_years, \
    default_bipv_scenario_identifier

dev_logger = logging.getLogger("dev")
user_logger = logging.getLogger("user")


class SimFunSolarRadAndBipv:

    @staticmethod
    def generate_sensor_grid(urban_canopy_object, building_id_list=None,
                             bipv_on_roof=True,
                             bipv_on_facades=True,
                             roof_grid_size_x=default_roof_grid_size_x,
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
                                               path_epw_file=default_path_weather_file,
                                               overwrite=False, north_angle=0, silent=False):
        """
        Make oriented bounding boxes of buildings in the urban canopy
        :param urban_canopy_object: urban canopy object
        :param path_simulation_folder: path to the folder where the simulation will be run
        :param building_id_list: list of building id to be considered
        :param path_epw_file: path to the weather file
        :param overwrite: bool: default=False: if True, overwrite the existing simulation
        :param north_angle: number: default=0: number of degrees to rotate the roof mesh
        :param silent: bool: default=False: if True, run the simulation silently
        """

        urban_canopy_object.run_annual_solar_irradiance_simulation_on_buildings(
            path_simulation_folder=path_simulation_folder,
            building_id_list=building_id_list,
            path_epw_file=path_epw_file,
            overwrite=overwrite, north_angle=north_angle,
            silent=silent)
        user_logger.info("The annual solar irradiance simulation have been performed successfully")
        dev_logger.info("The annual solar irradiance simulation have been performed successfully")

    @staticmethod
    def run_bipv_harvesting_and_lca_simulation(urban_canopy_object,
                                               path_simulation_folder=default_path_simulation_folder,
                                               bipv_scenario_identifier=default_bipv_scenario_identifier,
                                               path_folder_pv_tech_dictionary_json=default_path_pv_tech_dictionary_folder,
                                               building_id_list=None, roof_id_pv_tech=default_id_pv_tech_roof,
                                               facades_id_pv_tech=default_id_pv_tech_facades,
                                               efficiency_computation_method=default_efficiency_computation_method,
                                               minimum_panel_eroi=default_minimum_panel_eroi,
                                               start_year=default_start_year,
                                               end_year=default_end_year,
                                               replacement_scenario=default_replacement_scenario,
                                               continue_simulation=False, **kwargs):
        """
        Make oriented bounding boxes of buildings in the urban canopy
        :param urban_canopy_object: urban canopy object
        :param path_simulation_folder: path to the folder where the simulation will be run
        :param bipv_scenario_identifier: str: identifier of the BIPV scenario
        :param path_folder_pv_tech_dictionary_json: path to the folder containing the json files with the PV technology
        :param building_id_list: list of building id to be considered
        :param roof_id_pv_tech: str: identifier of the PV technology to be used on the roof
        :param facades_id_pv_tech: str: identifier of the PV technology to be used on the facades
        :param efficiency_computation_method: str: default="yearly": method to compute the efficiency of the panels
        :param minimum_panel_eroi: number: default=1.2: minimum energy return on investment of the panels
        :param start_year: int: default=datetime.now().year: year when the scenario starts
        :param end_year: int: default=start_year+50: year when the scenario ends
        :param replacement_scenario: str: default="replace_failed_panels_every_X_years": scenario for the replacement
        :param continue_simulation: bool: default=False: if True, continue the simulation
        :param kwargs: dict: other parameters
        """

        urban_canopy_object.run_bipv_panel_simulation_on_buildings(path_simulation_folder=path_simulation_folder,
                                                                   bipv_scenario_identifier=bipv_scenario_identifier,
                                                                   path_folder_pv_tech_dictionary_json=path_folder_pv_tech_dictionary_json,
                                                                   building_id_list=building_id_list,
                                                                   roof_id_pv_tech=roof_id_pv_tech,
                                                                   facades_id_pv_tech=facades_id_pv_tech,
                                                                   efficiency_computation_method=efficiency_computation_method,
                                                                   minimum_panel_eroi=minimum_panel_eroi,
                                                                   start_year=start_year,
                                                                   end_year=end_year,
                                                                   replacement_scenario=replacement_scenario,
                                                                   continue_simulation=continue_simulation, **kwargs)

        user_logger.info("The BIPV simulation have been performed successfully")
        dev_logger.info("The BIPV simulation have been performed successfully")