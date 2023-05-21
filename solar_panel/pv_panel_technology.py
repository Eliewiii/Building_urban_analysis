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
        self.weibull_law_failure_parameters = {"lifetime": None, "shape": None}
        self.DMFA = None  # per square meter
        self.carbon_footprint_manufacturing = None  # per square meter
        self.panel_area = None  # in square meter

    @classmethod
    def load_pv_technology(cls, identifier, path_json_file):
        """ Create the PanelTechnology objects from json file"""
        # todo @Hilany, how do you know the identifier ?
        #  maybe rename the function load_pv_technologies_from_json_library(ppath_json_file),
        #  read the json file once, loop over all the technologies and then retur directly the dictionnary with all the
        #  pv_technology_obj.
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
        """ Get the probabilistic time failure of a panel using the inverse of the quantile (inverse of the cumulative
        distribution0) function for the Weibull distribution"""

        # todo @ Hilany don't think this fiorst check is useful as all the object are created with these parameters
        #  if we want to check if if the parameters are correct we need to do it during the extraction of the paramters
        # if we realize that the Weibull parameters haven't been loaded yet, we do so
        # else, we directly calculate the time of failure
        if self.weibull_law_failure_parameters["lifetime"] is None \
                or self.weibull_law_failure_parameters["shape"] is None:
            self.get_weibull_law_failure_parameters()

        y = random.random()  # we randomly choose a value between 0 and 1
        shape = self.weibull_law_failure_parameters["shape"]  # extract the failure parameters
        lifetime = self.weibull_law_failure_parameters["lifetime"]
        # Quantile function for the Weibull distribution
        life_expectancy = ceil(shape * (-log(1 - y)) ** (1 / lifetime))
        return life_expectancy
