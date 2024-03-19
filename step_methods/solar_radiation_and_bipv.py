"""
Functions to be run by the main to perform the different steps of teh solar radiation and BIPV simulation
"""
import logging

from urban_canopy.urban_canopy import UrbanCanopy

from utils.utils_default_values_user_parameters import default_path_simulation_folder, \
    default_path_weather_file

from utils.utils_default_values_user_parameters import default_roof_grid_size_x, default_facades_grid_size_x, \
    default_roof_grid_size_y, default_facades_grid_size_y, default_offset_dist

from utils.utils_default_values_user_parameters import default_id_pv_tech_roof, \
    default_id_pv_tech_facades, default_roof_transport_id, default_facades_transport_id, \
    default_roof_inverter_id, default_facades_inverter_id, default_roof_inverter_sizing_ratio, \
    default_facades_inverter_sizing_ratio, default_minimum_panel_eroi, default_start_year, default_end_year, \
    default_efficiency_computation_method, default_replacement_scenario, \
    default_replacement_frequency_in_years, \
    default_bipv_scenario_identifier, default_grid_ghg_intensity, default_grid_energy_intensity, \
    default_grid_electricity_sell_price

dev_logger = logging.getLogger("dev")
user_logger = logging.getLogger("user")


class SimFunSolarRadAndBipv:

    @staticmethod
    def generate_sensor_grid(urban_canopy_object: UrbanCanopy, building_id_list=None,
                             bipv_on_roof=True,
                             bipv_on_facades=True,
                             roof_grid_size_x=default_roof_grid_size_x,
                             facades_grid_size_x=default_facades_grid_size_x,
                             roof_grid_size_y=default_roof_grid_size_y,
                             facades_grid_size_y=default_facades_grid_size_y,
                             offset_dist=default_offset_dist,
                             overwrite=False):
        """
        Make oriented bounding boxes of buildings in the urban canopy
        :param urban_canopy_object: urban canopy object
        :param building_id_list: list of building id to be considered
        :param bipv_on_roof: bool: default=True if True, generate sensor grid on the roof
        :param bipv_on_facades: bool: default=True if True, generate sensor grid on the facades
        :param roof_grid_size_x: float: default=1.5: grid size of the roof mesh in the x direction
        :param facades_grid_size_x: float: default=1.5: grid size of the facades mesh in the x direction
        :param roof_grid_size_y: float: default=1.5: grid size of the roof mesh in the y direction
        :param facades_grid_size_y: float: default=1.5: grid size of the facades mesh in the y direction
        :param offset_dist: float: default=0.1: offset distance to move the sensor grid from the building surface
        """

        urban_canopy_object.generate_sensor_grid_on_buildings(building_id_list=building_id_list,
                                                              bipv_on_roof=bipv_on_roof,
                                                              bipv_on_facades=bipv_on_facades,
                                                              roof_grid_size_x=roof_grid_size_x,
                                                              facades_grid_size_x=facades_grid_size_x,
                                                              roof_grid_size_y=roof_grid_size_y,
                                                              facades_grid_size_y=facades_grid_size_y,
                                                              offset_dist=offset_dist,
                                                              overwrite=overwrite)
        user_logger.info("Honeybee SensorGrids on the buildings have been generated successfully")
        dev_logger.info("Honeybee SensorGrids on the buildings have been generated successfully")

    @staticmethod
    def run_annual_solar_irradiance_simulation(urban_canopy_object: UrbanCanopy,
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
        :param north_angle: float: default=0: number of degrees to rotate the roof mesh
        :param silent: bool: default=False: if True, run the simulation silently
        """

        urban_canopy_object.run_annual_solar_irradiance_simulation_on_buildings(
            path_simulation_folder=path_simulation_folder,
            building_id_list=building_id_list,
            path_weather_file=path_weather_file,
            overwrite=overwrite, north_angle=north_angle,
            silent=silent)
        user_logger.info("The annual solar irradiance simulation have been performed successfully")
        dev_logger.info("The annual solar irradiance simulation have been performed successfully")

    @staticmethod
    def run_bipv_harvesting_and_lca_simulation(urban_canopy_object: UrbanCanopy,
                                               path_simulation_folder=default_path_simulation_folder,
                                               bipv_scenario_identifier=default_bipv_scenario_identifier,
                                               building_id_list=None, roof_id_pv_tech=default_id_pv_tech_roof,
                                               facades_id_pv_tech=default_id_pv_tech_facades,
                                               roof_transport_id=default_roof_transport_id,
                                               facades_transport_id=default_facades_transport_id,
                                               roof_inverter_id=default_roof_inverter_id,
                                               facades_inverter_id=default_facades_inverter_id,
                                               roof_inverter_sizing_ratio=default_roof_inverter_sizing_ratio,
                                               facades_inverter_sizing_ratio=default_facades_inverter_sizing_ratio,
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
        :param building_id_list: list of building id to be considered
        :param roof_id_pv_tech: str: identifier of the PV technology to be used on the roof
        :param facades_id_pv_tech: str: identifier of the PV technology to be used on the facades
        :param roof_transport_id: str: identifier of the transport technology to be used on the roof
        :param facades_transport_id: str: identifier of the transport technology to be used on the facades
        :param roof_inverter_id: str: identifier of the inverter technology to be used on the roof
        :param facades_inverter_id: str: identifier of the inverter technology to be used on the facades
        :param roof_inverter_sizing_ratio: float: default=1.1: sizing ratio of the inverter on the roof
        :param facades_inverter_sizing_ratio: float: default=1.1: sizing ratio of the inverter on the facades
        :param efficiency_computation_method: str: default="yearly": method to compute the efficiency of the panels
        :param minimum_panel_eroi: float: default=1.2: minimum energy return on investment of the panels
        :param start_year: int: default=datetime.now().year: year when the scenario starts
        :param end_year: int: default=start_year+50: year when the scenario ends
        :param replacement_scenario: str: default="replace_failed_panels_every_X_years": scenario for the replacement
        :param continue_simulation: bool: default=False: if True, continue the simulation
        :param kwargs: dict: other parameters
        """

        urban_canopy_object.run_bipv_panel_simulation_on_buildings(
            path_simulation_folder=path_simulation_folder,
            bipv_scenario_identifier=bipv_scenario_identifier,
            building_id_list=building_id_list,
            roof_id_pv_tech=roof_id_pv_tech,
            facades_id_pv_tech=facades_id_pv_tech,
            roof_transport_id=roof_transport_id,
            facades_transport_id=facades_transport_id,
            roof_inverter_id=roof_inverter_id,
            facades_inverter_id=facades_inverter_id,
            roof_inverter_sizing_ratio=roof_inverter_sizing_ratio,
            facades_inverter_sizing_ratio=facades_inverter_sizing_ratio,
            efficiency_computation_method=efficiency_computation_method,
            minimum_panel_eroi=minimum_panel_eroi,
            start_year=start_year,
            end_year=end_year,
            replacement_scenario=replacement_scenario,
            continue_simulation=continue_simulation, **kwargs)

        user_logger.info("The BIPV simulation have been performed successfully")
        dev_logger.info("The BIPV simulation have been performed successfully")

    @staticmethod
    def run_kpi_simulation(urban_canopy_object: UrbanCanopy,
                           path_simulation_folder=default_path_simulation_folder,
                           bipv_scenario_identifier=default_bipv_scenario_identifier,
                           grid_ghg_intensity=default_grid_ghg_intensity,
                           grid_energy_intensity=default_grid_energy_intensity,
                           grid_electricity_sell_price=default_grid_electricity_sell_price, zone_area=None):
        """
        Compute the KPIs at the urban scale. It includes BIPV and UBES KPIs.
        :param urban_canopy_object: UrbanCanopy: urban canopy object
        :param path_simulation_folder: str: path to the simulation folder
        :param bipv_scenario_identifier: str: identifier of the BIPV scenario
        :param grid_ghg_intensity: float: grid GHG intensity in gCO2/kWh
        :param grid_energy_intensity: float: grid energy intensity in kWh/kWh
        :param grid_electricity_sell_price: float: grid electricity sell price in $/kWh
        :param zone_area: float: m2: area of the zone of the studied area.
        """

        urban_canopy_object.compute_bipv_kpis_at_urban_scale(path_simulation_folder=path_simulation_folder,
                                                             bipv_scenario_identifier=bipv_scenario_identifier,
                                                             grid_ghg_intensity=grid_ghg_intensity,
                                                             grid_energy_intensity=grid_energy_intensity,
                                                             grid_electricity_sell_price=grid_electricity_sell_price,
                                                             zone_area=zone_area)

        user_logger.info("KPIS have been computed successfully")
        dev_logger.info("KPIS have been computed successfully")
