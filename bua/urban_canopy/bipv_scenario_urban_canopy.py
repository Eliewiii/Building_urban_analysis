"""
 Object that manage bipv simulation at the urban canopy scale, enabling multiple scenarios
"""

import os

from copy import deepcopy

from bua.building.solar_radiation_and_bipv.solar_rad_and_BIPV import empty_bipv_results_dict, \
    sum_bipv_results_dicts_with_different_years, bipv_results_to_csv

from bua.urban_canopy.urban_canopy import UrbanCanopyKPIs


class BipvScenario:
    """
    Class to manage and generated multiple BIPV scenarios at the urban canopy scale.
    """

    def __init__(self, identifier, start_year, end_year):
        """
        Initialize the BIPV scenario
        :param identifier: str: id of the scenario
        :param start_year: int: year when the scenario starts
        :param end_year: int: year when the scenario ends

        """
        self.id = identifier
        self.start_year = start_year
        self.end_year = end_year
        self.bipv_simulation_has_run = False
        self.bipv_simulated_building_id_list = None
        self.bipv_results_dict = None
        self.urban_canopy_bipv_kpis_obj = UrbanCanopyKPIs()
        # Initialize the results dictionaries
        self.init_bipv_results_dict()

    def init_bipv_results_dict(self):
        """
        Initialize the BIPV results
        """
        self.bipv_results_dict = deepcopy(empty_bipv_results_dict)

    def set_simulated_building_id_list(self, building_id_list):
        """
        Set the list of the simulated building ids
        :param simulated_building_id_list: list: list of the simulated building ids
        """
        self.bipv_simulated_building_id_list = building_id_list

    def to_dict(self):
        """
        Convert the object to a dictionary
        """
        return {
            "id": self.id,
            "start_year": self.start_year,
            "end_year": self.end_year,

            "bipv_results_dict": self.bipv_results_dict,
            "bipv_simulated_building_id_list": self.bipv_simulated_building_id_list,
            "kpis_results_dict": self.urban_canopy_bipv_kpis_obj.to_dict()
        }

    def continue_simulation(self, start_year: int, end_year: int):
        """
        Check if the simulation can be continued
        :param start_year: int: year when the scenario starts
        :param end_year: int: year when the scenario ends
        """
        if start_year < self.start_year:
            # raise an error
            raise ValueError(f"The start year input is lower than the original start year of the scenario"
                             f" start_year={self.start_year}, start a new simulation with the overall start year "
                             f"you want directly ")
        elif end_year > self.end_year:
            self.end_year = end_year
        else:
            pass

    def sum_bipv_results_at_urban_scale(self, solar_rad_and_bipv_obj_list):
        """
        Sum the results of the BIPV simulations at the urban scale
        :param solar_rad_and_bipv_obj_list: list: list of the SolarRadAndBipvSimulation objects
        """
        # Initialize the results dictionary
        self.init_bipv_results_dict()

        earliest_year = self.start_year
        latest_year = self.end_year

        # Sum the dictionaries
        for solar_rad_and_bipv_obj in solar_rad_and_bipv_obj_list:
            # sum the results for the roof
            self.bipv_results_dict["roof"] = sum_bipv_results_dicts_with_different_years(
                dict_1=self.bipv_results_dict["roof"],
                dict_2=solar_rad_and_bipv_obj.bipv_results_dict["roof"],
                start_year_1=earliest_year,
                start_year_2=solar_rad_and_bipv_obj.parameter_dict["roof"]["start_year"],
                earliest_year=earliest_year,
                latest_year=latest_year)
            # sum the results for the facades
            self.bipv_results_dict["facades"] = sum_bipv_results_dicts_with_different_years(
                dict_1=self.bipv_results_dict["facades"],
                dict_2=solar_rad_and_bipv_obj.bipv_results_dict["facades"],
                start_year_1=earliest_year,
                start_year_2=solar_rad_and_bipv_obj.parameter_dict["facades"]["start_year"],
                earliest_year=earliest_year,
                latest_year=latest_year)

        # sum the total results
        self.bipv_results_dict["total"] = sum_bipv_results_dicts_with_different_years(
            dict_1=self.bipv_results_dict["roof"],
            dict_2=self.bipv_results_dict["facades"],
            start_year_1=earliest_year,
            start_year_2=earliest_year,
            earliest_year=earliest_year,
            latest_year=latest_year)

    def write_bipv_results_to_csv(self, path_radiation_and_bipv_result_folder):
        """
        Write the BIPV results to a csv file
        :param path_to_csv: str: path to the csv file
        """
        bipv_results_to_csv(path_radiation_and_bipv_result_folder=path_radiation_and_bipv_result_folder,
                            building_id_or_uc_scenario_name=self.id,
                            bipv_results_dict=self.bipv_results_dict, start_year=self.start_year,
                            study_duration_in_years=self.end_year - self.start_year)

    def set_parameters_for_kpis_computation(self, grid_ghg_intensity, grid_energy_intensity,
                                            grid_electricity_sell_price,
                                            ubes_electricity_consumption, conditioned_apartment_area,
                                            zone_area):
        """
        Set the parameters needed for the computation of the KPIs
        todo: add the other parameters
        """
        self.urban_canopy_bipv_kpis_obj.set_parameters(grid_ghg_intensity=grid_ghg_intensity,
                                                       grid_energy_intensity=grid_energy_intensity,
                                                       grid_electricity_sell_price=grid_electricity_sell_price,
                                                       ubes_electricity_consumption=ubes_electricity_consumption,
                                                       conditioned_apartment_area=conditioned_apartment_area,
                                                       zone_area=zone_area)

    def compute_scenario_kpis(self, grid_ghg_intensity, grid_energy_intensity, grid_electricity_sell_price,
                     ubes_electricity_consumption, conditioned_apartment_area, zone_area):
        """
        Compute the KPIs of the scenario
        :param grid_ghg_intensity: float: kgCO2/kWh: grid GHG intensity
        :param grid_energy_intensity: float: kWh/m2: grid energy intensity
        :param grid_electricity_sell_price: float: €/kWh: grid electricity sell price
        :param ubes_electricity_consumption: float: kWh: electricity consumption of the buildings
        :param conditioned_apartment_area: float: m2: conditioned apartment area
        :param zone_area: float: m2: area of the zone

        """
        # Initialize the KPIs object (once again, in case it already exists)
        self.urban_canopy_bipv_kpis_obj = UrbanCanopyKPIs()
        # Set the parameters
        self.set_parameters_for_kpis_computation(grid_ghg_intensity=grid_ghg_intensity,
                                                 grid_energy_intensity=grid_energy_intensity,
                                                 grid_electricity_sell_price=grid_electricity_sell_price,
                                                 ubes_electricity_consumption=ubes_electricity_consumption,
                                                 conditioned_apartment_area=conditioned_apartment_area,
                                                 zone_area=zone_area)
        # Compute the KPIs
        self.urban_canopy_bipv_kpis_obj.compute_kpis(
            bipv_results_dict=self.bipv_results_dict)

    def write_kpis_to_csv(self, path_radiation_and_bipv_result_folder):
        """
        Write the KPIs to a csv file
        :param path_radiation_and_bipv_result_folder: str: path to the folder to save the csv files in
        """
        path_folder = os.path.join(path_radiation_and_bipv_result_folder, self.id)
        self.urban_canopy_bipv_kpis_obj.to_csv(path_folder=path_folder, start_year=self.start_year,
                                               end_year=self.end_year,prefix=self.id)
