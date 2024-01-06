"""
Performs the energy simulation of a building using the EnergyPlus software and saves the results in a dictionary.
"""

import logging

from copy import deepcopy

user_logger = logging.getLogger("user")
dev_logger = logging.getLogger("dev")

empty_bes_results_dict = {
    "heating": {"monthly": [], "monthly_cumulative": [], "yearly": None},
    "cooling": {"monthly": [], "monthly_cumulative": [], "yearly": None},
    "equipment": {"monthly": [], "monthly_cumulative": [], "yearly": None},
    "lighting": {"monthly": [], "monthly_cumulative": [], "yearly": None},
    "ventilation": {"monthly": [], "monthly_cumulative": [], "yearly": None},  # Unused for now
    "total": {"monthly": [], "monthly_cumulative": [], "yearly": None}
}


class BuildingEnergySimulation:
    """
    Class to perform the energy simulation of a building using the EnergyPlus software and saves the results in a
    dictionary.
    """

    def __init__(self, building_id):
        """
        Initialize the BuildingEnergySimulation class.
        :param building_id: str, id of the building the object belongs to
        """

        self.building_id = building_id
        # Parameters
        self.cop_heating = None
        self.cop_cooling = None
        # Flags
        self.has_run = False
        # Results
        self.bes_results_dict = None

    def re_initialize(self):
        """
        Re-initialize the values of the attributes of the BuildingEnergySimulation object.
        """
        # Parameters
        self.cop_heating = None
        self.cop_cooling = None
        # Flags
        self.has_run = False
        # Results
        self.bes_results_dict = None

    def set_parameters(self, hb_simulation_parameter_obj, epw_name, cop_heating, cop_cooling):
        """

        """

    def make_idf_with_openstudio(self, path_bes_folder, path_epw_file, path_simulation_parameter):
        """
        Make
        """
        #
        # (path_osm, path_idf) = from_hbjson_to_idf(dir_to_write_idf_in, path_hbjson_file, path_epw_file,
        #                                   path_simulation_parameter)

    @staticmethod
    def make_hbjson_from_hb_model_and_shades(hb_model, hb_shade_list):
        """
        Make a hbjson file from a hb model and a list of shades
        :param hb_model: Honeybee Model
        :param hb_shade_list: list of Honeybee Shades
        """
