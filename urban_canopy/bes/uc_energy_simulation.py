"""
Performs the energy simulation of a building using the EnergyPlus software and saves the results in a dictionary.
"""

import os
import logging
import json

from copy import deepcopy

from honeybee_energy.simulation.parameter import SimulationParameter
from ladybug.epw import EPW

from urban_canopy.bes.check_simulation_parameter import check_simulation_parameter
from building.energy_simulation.building_energy_simulation import empty_bes_results_dict

user_logger = logging.getLogger("user")
dev_logger = logging.getLogger("dev")


class UrbanBuildingEnergySimulation:
    """
    Class to perform the energy simulation of a building using the EnergyPlus software and saves the results in a
    dictionary.
    """

    def __init__(self):
        """
        Initialize the BuildingEnergySimulation class.
        :param building_id: str, id of the building the object belongs to
        """

        # Parameters
        self.hb_simulation_parameters_obj = None
        self.lb_epw_obj = None
        # Flags
        self.has_run = False
        # Results
        self.bes_results_dict = deepcopy(empty_bes_results_dict)

    def set_parameters(self, hb_simulation_parameter_obj, epw_name):
        """

        """

    def load_epw_and_hb_simulation_parameters(self, path_hbjson_simulation_parameter_file, path_file_epw, ddy_file=None,
                                              overwrite=False):
        """
        Load the epw file and simulation parameters from the simulation parameter file and check and correct teh
        simulation parameters if needed.
        :param path_hbjson_simulation_parameter_file: str, path to the simulation parameter hbjson file
        :param path_file_epw: str, path to the epw file
        :param overwrite: bool, if True, overwrite the existing simulation parameters
        """
        # Flag
        flag_re_initialize_building_bes = False
        
        # Check that the UrbanBuildingEnergySimulation does not already have a simulation parameter and epw file
        if self.hb_simulation_parameters is not None and self.lb_epw_obj is not None and not overwrite:
            return flag_re_initialize_building_bes
        
        # Check if the simulation parameter file and epw file are valid and correct them if needed
        hb_sim_parameter_obj, lb_epw_obj = check_simulation_parameter(path_hbjson_simulation_parameter_file, path_file_epw)
        # Set the simulation parameter and epw file
        self.hb_simulation_parameters = hb_sim_parameter_obj
        self.lb_epw_obj = lb_epw_obj
        if overwrite:
            # Put back the has_run flag to False as all the simulation will need to be run again
            self.has_run = False
            # Flag that the building bes needs to be re-initialized, it will be done by the Urban Canopy
            flag_re_initialize_building_bes = True
        
        return flag_re_initialize_building_bes

    @staticmethod
    def re_initialize_building_bes(building_bes_obj_list):
        """
        Re-initialize the values of the attributes of the BuildingEnergySimulation object.
        """
        for building_bes_obj in building_bes_obj_list:
            building_bes_obj.re_initialize()

    def make_idf_with_openstudio(self, path_bes_folder, path_epw_file, path_simulation_parameter):
        """
        Make
        """

        # (path_osm, path_idf) = from_hbjson_to_idf(dir_to_write_idf_in, path_hbjson_file, path_epw_file,
        #                                           path_simulation_parameter)

    @staticmethod
    def make_hbjson_from_hb_model_and_shades(hb_model, hb_shade_list):
        """
        Make a hbjson file from a hb model and a list of shades
        :param hb_model: Honeybee Model
        :param hb_shade_list: list of Honeybee Shades
        """
