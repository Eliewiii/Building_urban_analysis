"""

"""
from math import log, ceil
import random


class PanelTechnology:
    """ """

    def __init__(self, identifier):
        self.identifier = identifier
        self.efficiency_function = None
        self.weibull_law_failure_parameters = None
        self.DMFA = None  # per square meter
        self.carbon_footprint = None  # per square meter
        self.panel_area = None

    @classmethod
    def load_technologies(cls, path_json_file):
        """ Create the PanelTechnology objects from dataset and make a dictionary """
        # todo
        dict = None

        return dict

    def get_weibull_law_failure_parameters(self):
        """ Get the Weibull parameters from json file (depending on the identifier of the technology) and put them in
        the dictionary"""
        # todo

    def get_time_failure_of_a_panel(self):
        """ Get the probabilistic time failure of a panel using the inverse of the quantile (inverse of the cumulative
        distribution0) function for the Weibull distribution"""

        # if we realize that the Weibull parameters haven't been loaded yet, we do so
        # else, we directly calculate the time of failure
        if self.weibull_law_failure_parameters is None:
            self.get_weibull_law_failure_parameters()
        y = random.random()  # we randomly choose a value between 0 and 1
        lambda_param = self.weibull_law_failure_parameters["lambda"]  # extract the failure parameters
        k = self.weibull_law_failure_parameters["k"]
        time_of_failure = ceil(lambda_param * (-log(1 - y)) ** (1 / k)) # Quantile function for the Weibull distribution
        return time_of_failure
