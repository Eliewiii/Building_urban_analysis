"""

"""
from math import log, ceil
import random
import json
from libraries_addons.solar_panels.pv_efficiency_functions import get_efficiency_loss_function_from_string


class BipvTechnology:
    """ """

    def __init__(self, identifier):
        self.identifier = identifier
        # Efficiency
        self.efficiency_function = None
        self.initial_efficiency = None
        self.panel_performance_ratio = None
        self.first_year_degrading_rate = 0.02  # todo : add the parameters to the dictionnary
        self.degrading_rate = 0.005
        # Failure
        self.weibull_law_failure_parameters = {"lifetime": None, "shape": None}
        # LCA and DMFA parameters
        self.panel_area = None  # in square meter
        self.primary_energy_manufacturing = None  # per square meter
        self.carbon_manufacturing = None
        self.primary_energy_transport = None
        self.carbon_transport = None
        self.weight = None  # per square meter
        self.primary_energy_recycling = None
        self.carbon_recycling = None

    @classmethod
    def load_pv_technologies_from_json_to_dictionary(cls, path_json_file):
        """
        Create the PanelTechnology objects from json file and save them in a dictionary
        :param path_json_file: path to a json file database of the pv technologies
        : return pv_technologies_dict: dictionary of the technologies
        """
        pv_technologies_dict = {}  # initialize the dictionary
        with open(path_json_file) as f:  # open and load the json file
            pv_dict_data = json.load(f)
            for identifier_key in pv_dict_data:  # for every technology in the json, we create and load the
                # PVPanelTechnology object
                pv_tech = cls(identifier_key)
                efficiency_function_name = pv_dict_data[pv_tech.identifier]["efficiency_function"]
                # todo : add a try to check if the function exist, use the defaukt function if it does not exist, and return a warning
                pv_tech.efficiency_function = getattr(pv_tech, efficiency_function_name)
                # todo add panel performance ratio
                pv_tech.initial_efficiency = pv_dict_data[identifier_key]["initial_efficiency"]
                pv_tech.weibull_law_failure_parameters["lifetime"] = pv_dict_data[identifier_key][
                    "weibull_lifetime"]
                pv_tech.weibull_law_failure_parameters["shape"] = pv_dict_data[identifier_key][
                    "weibull_shape"]
                pv_tech.panel_area = pv_dict_data[identifier_key]["panel_area"]
                pv_tech.weight = pv_dict_data[identifier_key]["weight"]
                pv_tech.primary_energy_manufacturing = pv_dict_data[identifier_key][
                    "primary_energy_manufacturing_in_kWh_per_panel"]
                pv_tech.carbon_manufacturing = pv_dict_data[identifier_key][
                    "gh_gas_emissions_manufacturing_in_kgCO2eq_per_panel"]
                pv_tech.primary_energy_transport = pv_dict_data[identifier_key][
                    "primary_energy_transport_in_kWh_per_panel"]
                pv_tech.carbon_transport = pv_dict_data[identifier_key]["carbon_transport_in_kgCO2_per_panel"]
                pv_tech.weight = pv_dict_data[identifier_key]["weight"]
                pv_tech.primary_energy_recycling = pv_dict_data[identifier_key][
                    "end_of_life_primary_energy_in_kWh_per_panel"]
                pv_tech.carbon_recycling = pv_dict_data[identifier_key][
                    "end_of_life_carbon_in_kgCO2_per_panel"]

                pv_technologies_dict[
                    identifier_key] = pv_tech  # then we add this object to the dictionary containing
                # all the different technologies
        return pv_technologies_dict

    def add_weibull_law_failure_parameters(self, path_json_file):
        """ Get the Weibull parameters from json file (depending on the identifier of the technology) and load them in
        the self"""
        # todo @Hilany, seems useless now because of load_pv_technology(), to delete?
        with open(path_json_file) as f:
            pv_dict_data = json.load(f)
            self.weibull_law_failure_parameters["lifetime"] = pv_dict_data[self.identifier][
                "weibull_lifetime"]
            self.weibull_law_failure_parameters["shape"] = pv_dict_data[self.identifier]["weibull_shape"]

    def add_efficiency_function(self, path_json_file):
        # todo @Hilany, seems useless now because of load_pv_technology(), to delete?
        """ Get the efficiency loss function
        For now, it will be considered as a linear function which depends on the initial efficiency of the PV (ie. type
        of PV) and on its age"""
        with open(path_json_file) as f:
            pv_dict_data = json.load(f)
            self.efficiency_function = get_efficiency_loss_function_from_string(pv_dict_data[self.identifier]
                                                                                ["efficiency_function"])

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

    def degrading_rate_efficiency_loss(self, age):
        """ loose 2% efficiency the first year and then 0.5% every year"""
        if age == 0:
            return self.initial_efficiency
        else :
            return self.initial_efficiency * (1 - self.first_year_degrading_rate) * (1 - self.degrading_rate) ** (
                    age - 1)

    def irradiance_dependent_efficiency(self, irradiance):
        """ todo: this one is just an example, to be changed"""
        return self.initial_efficiency * irradiance * self.param_1_irradiance + self.param_2_irradiance * irradiance ** 2

    def irradiance_temperature_and_age_dependent_efficiency(self, irradiance,outdoor_temperature,age):
        """ todo: this one is just an example, to be changed"""
        return self.initial_efficiency * irradiance * self.param_1_irradiance + self.param_2_irradiance * irradiance ** 2


# todo to delete
# def get_efficiency_loss_function_from_string(self,fucntion_name):
#     """todo"""
#     if fucntion_name == "degrading_rate_efficiency_loss":
#         return self.degrading_rate_efficiency_loss
