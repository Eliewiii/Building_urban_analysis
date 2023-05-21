"""

"""
from math import log, ceil
import random
import json
from libraries_addons.solar_panels.pv_efficiency_functions import get_efficiency_loss_function_from_string


class PanelTechnology:
    """ """

    def __init__(self, identifier):
        self.identifier = identifier
        self.efficiency_function = None
        self.weibull_law_failure_parameters = {"lifetime": None, "shape": None}
        self.DMFA = None  # per square meter
        self.carbon_footprint_manufacturing = None  # per square meter
        self.panel_area = None  # in square meter

    @classmethod
    def load_pv_technology(cls, identifier, path_json_file):
        """ Create the PanelTechnology objects from json file"""
        with open(path_json_file) as f:
            pv_dict_data = json.load(f)
            pv_tech = cls(identifier)
            pv_tech.efficiency_function = get_efficiency_loss_function_from_string(pv_dict_data[pv_tech.identifier]
                                                                                   ["efficiency_function"])
            pv_tech.weibull_law_failure_parameters["lifetime"] = pv_dict_data[identifier]["weibull_lifetime"]
            pv_tech.weibull_law_failure_parameters["shape"] = pv_dict_data[identifier]["weibull_shape"]
            pv_tech.DMFA = pv_dict_data[identifier]["DMFA"]
            pv_tech.carbon_footprint_manufacturing = pv_dict_data[identifier]["carbon_footprint_manufacturing"]
            pv_tech.panel_area = pv_dict_data[identifier]["panel_area"]

        return pv_tech

    def add_weibull_law_failure_parameters(self, path_json_file):
        """ Get the Weibull parameters from json file (depending on the identifier of the technology) and load them in
        the self"""
        with open(path_json_file) as f:
            pv_dict_data = json.load(f)
            self.weibull_law_failure_parameters["lifetime"] = pv_dict_data[self.identifier]["weibull_lifetime"]
            self.weibull_law_failure_parameters["shape"] = pv_dict_data[self.identifier]["weibull_shape"]

    def add_efficiency_function(self, path_json_file):
        """ Get the efficiency loss function
        For now, it will be considered as a linear function which depends on the initial efficiency of the PV (ie. type
        of PV) and on its age"""
        with open(path_json_file) as f:
            pv_dict_data = json.load(f)
            self.efficiency_function = get_efficiency_loss_function_from_string(pv_dict_data[self.identifier]
                                                                                ["efficiency_function"])

    def get_life_expectancy_of_a_panel(self):
        """ Get the probabilistic time failure of a panel using the inverse of the quantile (inverse of the cumulative
        distribution0) function for the Weibull distribution"""

        # if we realize that the Weibull parameters haven't been loaded yet, we do so
        # else, we directly calculate the time of failure
        if self.weibull_law_failure_parameters["lifetime"] is None \
                or self.weibull_law_failure_parameters["shape"] is None:
            self.get_weibull_law_failure_parameters()
        y = random.random()  # we randomly choose a value between 0 and 1
        shape = self.weibull_law_failure_parameters["shape"]  # extract the failure parameters
        lifetime = self.weibull_law_failure_parameters["lifetime"]
        life_expectancy = ceil(
            shape * (-log(1 - y)) ** (1 / lifetime))  # Quantile function for the Weibull distribution
        return life_expectancy
