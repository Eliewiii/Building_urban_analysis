"""
Performs the energy simulation of a building using the EnergyPlus software and saves the results in a dictionary.
"""

import logging

from copy import deepcopy

from building.energy_simulation.building_energy_simulation import empty_bes_results_dict

user_logger = logging.getLogger("user")
dev_logger = logging.getLogger("dev")

class Urban_canopyEnergySimulation:
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
        self.simulation_parameters = None
        self.epw_name = None
        self.cop_heating = None
        self.cop_cooling = None
        # Flags
        self.has_run = False
        # Results
        self.bes_results_dict = deepcopy(empty_bes_results_dict)


    def set_parameters(self, hb_simulation_parameter_obj, epw_name, cop_heating, cop_cooling):
        """

        """


    def make_idf_with_openstudio(self,path_bes_folder,path_epw_file, path_simulation_parameter):
        """
        Make
        """

        (path_osm, path_idf) = from_hbjson_to_idf(dir_to_write_idf_in, path_hbjson_file, path_epw_file,
                                          path_simulation_parameter)

    @staticmethod
    def make_hbjson_from_hb_model_and_shades(hb_model, hb_shade_list):
        """
        Make a hbjson file from a hb model and a list of shades
        :param hb_model: Honeybee Model
        :param hb_shade_list: list of Honeybee Shades
        """



































