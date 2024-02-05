"""

"""
import os
import json
import random

from math import log, ceil

temp_ref = 25  # temperature reference for the efficiency of the panel


class BipvTechnology:
    """

    Example of a json file containing the data of the pv technologies
      "mitrex_roof c-Si": {
            "weibull_lifetime": 30,
            "weibull_shape": 5.3759,
            "initial_efficiency": 0.1920,
            "panel_area": 2.03,
            "efficiency_function" : "degrading_rate_efficiency_loss",
            "weight" : 22,
            "primary_energy_manufacturing_in_kWh_per_panel": 2189.9,
            "gh_gas_emissions_manufacturing_in_kgCO2eq_per_panel" : 384.849,
            "primary_energy_transport_in_kWh_per_panel": 0,
            "carbon_transport_in_kgCO2_per_panel": 0,
            "end_of_life_primary_energy_in_kWh_per_panel": 16.99,
            "end_of_life_carbon_in_kgCO2_per_panel": 8.14
                      }"""

    def __init__(self, identifier):
        self.identifier = identifier
        #
        self.panel_area = None  # in square meter
        self.weight = None  # per square meter

        # Efficiency
        self.efficiency_function = None
        self.initial_efficiency = None
        self.panel_performance_ratio = None
        self.first_year_degrading_rate = None
        self.degrading_rate = None
        # Failure
        self.weibull_law_failure_parameters = {"lifetime": None, "shape": None}
        # LCA and DMFA parameters
        self.primary_energy_manufacturing = None  # per square meter
        self.carbon_manufacturing = None
        self.primary_energy_transport = None
        self.carbon_transport = None
        self.primary_energy_recycling = None
        self.carbon_recycling = None

    @classmethod
    def load_pv_technologies_from_json_to_dictionary(cls, path_json_folder):
        """
        Create the PanelTechnology objects from json file and save them in a dictionary
        :param path_json_folder: path to the folder containing the json file
        :return pv_technologies_dict: dictionary of the technologies
        """
        pv_technologies_dict = {}  # initialize the dictionary
        for json_file in os.listdir(path_json_folder):  # for every json file in the folder
            if json_file.endswith(".json"):
                path_json_file = os.path.join(path_json_folder, json_file)  # get the path to the json file
                with open(path_json_file) as f:  # open and load the json file
                    pv_dict_data = json.load(f)
                    for identifier_key in pv_dict_data:  # for every technology in the json, we create and load the
                        # Initialize the object
                        pv_tech_obj = cls(identifier_key)
                        # Load physical paramters
                        pv_tech_obj.panel_area = pv_dict_data[identifier_key]["physical_parameters"][
                            "panel_area"]
                        pv_tech_obj.weight = pv_dict_data[identifier_key]["physical_parameters"][
                            "panel_weight"]
                        # Load failure parameters
                        pv_tech_obj.weibull_law_failure_parameters["lifetime"] = pv_dict_data[identifier_key][
                            "failure_parameters"]["weibull_scale_parameter"]
                        pv_tech_obj.weibull_law_failure_parameters["shape"] = pv_dict_data[identifier_key][
                            "failure_parameters"]["weibull_shape_parameter"]
                        # Load efficiency parameters
                        pv_tech_obj.initial_efficiency = \
                            pv_dict_data[identifier_key]["efficiency_parameters"][
                                "initial_efficiency"]
                        pv_tech_obj.first_year_degrading_rate = \
                            pv_dict_data[identifier_key]["efficiency_parameters"][
                                "first_year_degrading_rate"]
                        pv_tech_obj.degrading_rate = pv_dict_data[identifier_key]["efficiency_parameters"][
                            "degrading_rate"]
                        pv_tech_obj.panel_performance_ratio = \
                            pv_dict_data[identifier_key]["efficiency_parameters"][
                                "panel_performance_ratio"]
                        efficiency_function_name = pv_dict_data[identifier_key]["efficiency_parameters"][
                            "efficiency_function"]
                        pv_tech_obj.efficiency_function = getattr(pv_tech_obj, efficiency_function_name)
                        # Load LCA parameters
                        pv_tech_obj.primary_energy_manufacturing = \
                            pv_dict_data[identifier_key]["lca_parameters"][
                                "primary_energy_manufacturing_in_kWh_per_panel"]
                        pv_tech_obj.carbon_manufacturing = pv_dict_data[identifier_key]["lca_parameters"][
                            "carbon_footprint_manufacturing_in_kgCO2eq_per_panel"]
                        pv_tech_obj.primary_energy_transport = pv_dict_data[identifier_key]["lca_parameters"][
                            "primary_energy_transport_in_kWh_per_panel"]
                        pv_tech_obj.carbon_transport = pv_dict_data[identifier_key]["lca_parameters"][
                            "carbon_footprint_transport_in_kgCO2eq_per_panel"]

                        pv_tech_obj.primary_energy_recycling = pv_dict_data[identifier_key]["lca_parameters"][
                            "end_of_life_primary_energy_in_kWh_per_panel"]
                        pv_tech_obj.carbon_recycling = pv_dict_data[identifier_key]["lca_parameters"][
                            "end_of_life_carbon_footprint_in_kgCO2eq_per_panel"]

                        pv_technologies_dict[identifier_key] = pv_tech_obj
        return pv_technologies_dict

    def compute_transportation_energy(self):
        """
        Compute the energy needed for the transportation of the panels

        """
        # todo

    def get_life_expectancy_of_a_panel(self):
        """
        Get the probabilistic time failure of a panel using the inverse of the quantile (inverse of the cumulative
        distribution0) function for the Weibull distribution
        return life_expectancy: life expectancy of a panel according to the probabilistic law of Weibull
        """

        y = random.random()  # we randomly choose a value between 0 and 1
        shape = self.weibull_law_failure_parameters["shape"]  # extract the failure parameters
        lifetime = self.weibull_law_failure_parameters["lifetime"]
        # Quantile function for the Weibull distribution
        life_expectancy = ceil(lifetime * (-log(1 - y)) ** (1 / shape))
        return life_expectancy

    def get_energy_harvested_by_panel(self, irradiance, age, **kwargs):
        """
        Get the energy harvested by a panel in Watt
        :param irradiance: irradiance on the panel
        :param age: age of the panel
        :param kwargs: kwargs


        :return: energy_harvested: energy harvested by the panel
        """

        # Check if the efficiency function is defined in the kwargs
        if "efficiency_function" in kwargs and kwargs["efficiency_function"] in [
            getattr(self, method_name) for method_name in dir(self) if callable(getattr(self, method_name))]:
            """ The efficiency function can be defined in the kwargs. If it is not defined, the default efficiency function
                    is used. If it is defined, the efficiency function is used. The efficiency function must be a method of the
                    class."""
            efficiency_function = kwargs["efficiency_function"]
            efficiency = efficiency_function(age=age, irradiance=irradiance, **kwargs)
        else:
            efficiency = self.efficiency_function(age=age, irradiance=irradiance, **kwargs)

        energy_harvested = efficiency * irradiance * self.panel_performance_ratio * self.panel_area

        return energy_harvested

    def constant_efficiency(self, **kwargs):
        """ Constant efficiency through the life of the panel """
        return self.initial_efficiency

    def degrading_rate_efficiency_loss(self, age, **kwargs):
        """ loose 2% efficiency the first year and then 0.5% every year"""
        if age == 0:
            return self.initial_efficiency
        else:
            return self.initial_efficiency * (1 - self.first_year_degrading_rate - self.degrading_rate * (age - 1))

    def irradiance_dependent_efficiency(self, irradiance, **kwargs):
        """ todo: this one is just an example, to be changed"""
        return self.initial_efficiency * irradiance * self.param_1_irradiance + self.param_2_irradiance * irradiance ** 2

    def irradiance_temperature_and_age_dependent_efficiency(self, irradiance, age,
                                                            outdoor_temperature=temp_ref, **kwargs):
        """ todo: this one is just an example, to be changed"""
        return self.initial_efficiency * irradiance * self.param_1_irradiance + self.param_2_irradiance * irradiance ** 2

# todo to delete
# def get_efficiency_loss_function_from_string(self,fucntion_name):
#     """todo"""
#     if fucntion_name == "degrading_rate_efficiency_loss":
#         return self.degrading_rate_efficiency_loss
