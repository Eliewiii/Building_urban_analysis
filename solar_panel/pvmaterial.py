"""

"""
from math import log, ceil
import random
import json
from solar_panel.pv_efficiency_functions import linear_efficiency_loss


class PanelTechnology:
    """ """

    def __init__(self, identifier):
        self.identifier = identifier
        self.efficiency_function = None
        self.weibull_law_failure_parameters = {"lifetime": None, "shape": None}
        self.DMFA = None  # per square meter
        self.carbon_footprint = None  # per square meter
        self.panel_area = None

    @classmethod
    def load_technologies(cls, path_json_file):
        """ Create the PanelTechnology objects from dataset and make a dictionary """
        # todo
        dict = None

        return dict

    def get_weibull_law_failure_parameters(self, path_json_file):
        """ Get the Weibull parameters from json file (depending on the identifier of the technology) and load them in
        the self"""
        with open(path_json_file) as f:
            pv_dict_data = json.load(f)
            self.weibull_law_failure_parameters["lifetime"] = pv_dict_data[self.identifier]["lifetime"]
            self.weibull_law_failure_parameters["shape"] = pv_dict_data[self.identifier]["shape"]

    def get_efficiency_function(self, identifier, path):
        """ Get the efficiency loss function
        For now, it will be considered as a linear function which depends on the initial efficiency of the PV (ie. type
        of PV) and on its age"""
        self.efficiency_function = linear_efficiency_loss()

    def get_time_failure_of_a_panel(self):
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
        time_of_failure = ceil(
            shape * (-log(1 - y)) ** (1 / lifetime))  # Quantile function for the Weibull distribution
        return time_of_failure
