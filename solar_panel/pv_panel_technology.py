"""

"""
from math import log, ceil
import random
import json
from libraries_addons.solar_panels.pv_efficiency_functions import get_efficiency_loss_function_from_string


class PvPanelTechnology:
    """ """

    def __init__(self, identifier):
        self.identifier = identifier
        self.efficiency_function = None
        self.initial_efficiency = None
        self.weibull_law_failure_parameters = {"lifetime": None, "shape": None}
        self.DMFA = None  # per square meter
        self.energy_manufacturing = None  # per square meter
        self.carbon_manufacturing = None
        self.panel_area = None  # in square meter

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
                pv_tech.efficiency_function = pv_dict_data[pv_tech.identifier]["efficiency_function"]
                pv_tech.initial_efficiency = pv_dict_data[identifier_key]["initial_efficiency"]
                pv_tech.weibull_law_failure_parameters["lifetime"] = pv_dict_data[identifier_key]["weibull_lifetime"]
                pv_tech.weibull_law_failure_parameters["shape"] = pv_dict_data[identifier_key]["weibull_shape"]
                pv_tech.DMFA = pv_dict_data[identifier_key]["DMFA"]
                pv_tech.energy_manufacturing = pv_dict_data[identifier_key]["primary_energy_manufacturing_in_kWh_per_panel"]
                pv_tech.carbon_manufacturing = pv_dict_data[identifier_key]["gh_gas_emissions_manufacturing_in_kgCO2eq_per_panel"]
                pv_tech.panel_area = pv_dict_data[identifier_key]["panel_area"]

                pv_technologies_dict[identifier_key] = pv_tech  # then we add this object to the dictionary containing
                # all the different technologies
        return pv_technologies_dict

    def add_weibull_law_failure_parameters(self, path_json_file):
        """ Get the Weibull parameters from json file (depending on the identifier of the technology) and load them in
        the self"""
        # todo @Hilany, seems useless now because of load_pv_technology(), to delete?
        with open(path_json_file) as f:
            pv_dict_data = json.load(f)
            self.weibull_law_failure_parameters["lifetime"] = pv_dict_data[self.identifier]["weibull_lifetime"]
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
