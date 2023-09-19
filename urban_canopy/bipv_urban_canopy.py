"""

"""

from copy import deepcopy

from building.solar_radiation_and_bipv.solar_rad_and_BIPV import empty_bipv_results_dict, \
    sum_bipv_results_dicts_with_different_years, bipv_results_to_csv


class BipvScenario:
    """

    """

    def __init__(self, identifier, start_year, end_year):
        """
        todo
        :param identifier: str: id of the scenario
        :param start_year: int: year when the scenario starts
        :param end_year: int: year when the scenario ends

        """
        self.id = identifier
        self.start_year = start_year
        self.end_year = end_year
        self.bipv_results_dict=None
        self.init_bipv_results_dict()

    def init_bipv_results_dict(self):
        """
        Initialize the BIPV results
        """
        self.bipv_results_dict = deepcopy(empty_bipv_results_dict)

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

    def write_bipv_results_to_csv(self, path_simulation_folder):
        """
        Write the BIPV results to a csv file
        :param path_to_csv: str: path to the csv file
        """
        bipv_results_to_csv(path_simulation_folder=path_simulation_folder,
                            building_id_or_uc_scenario_name=self.id,
                            bipv_results_dict=self.bipv_results_dict, start_year=self.start_year,
                            study_duration_in_years=self.end_year - self.start_year)
