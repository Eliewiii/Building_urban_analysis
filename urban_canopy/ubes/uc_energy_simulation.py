"""
Performs the energy simulation of a building using the EnergyPlus software and saves the results in a dictionary.
"""

import os
import logging
import json

from copy import deepcopy

from honeybee_energy.simulation.parameter import SimulationParameter
from ladybug.epw import EPW

from utils.utils_configuration import name_ubes_epw_file, name_ubes_hbjson_simulation_parameters_file
from urban_canopy.ubes.check_simulation_parameter import check_simulation_parameters
from building.energy_simulation.building_energy_simulation import empty_bes_results_dict,bes_result_dict_to_csv


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
        self.ubes_results_dict = deepcopy(empty_bes_results_dict)

    def to_csv(self, path_ubes_sim_result_folder):
        """
        Save the results to a csv file.
        :param path_ubes_sim_result_folder: str, path to the folder to write the  csv file
        """

        if not self.has_run or self.ubes_results_dict is None:
            return
        # Paths to the results files
        path_csv_file = os.path.join(path_ubes_sim_result_folder, "urban_canopy_ubes_results.csv")
        # Check if the BES result folder and the result files exist
        if not os.path.isdir(path_ubes_sim_result_folder):
            return
        """ Write the file even if it exist already as monthly values could have been extracted 
        in the meantime """
        bes_result_dict_to_csv(bes_result_dict=self.ubes_results_dict, path_csv_file=path_csv_file)

    def load_epw_and_hb_simulation_parameters(self, path_hbjson_simulation_parameter_file, path_file_epw,
                                              ddy_file=None,
                                              overwrite=False):
        """
        Load the epw file and simulation parameters from the simulation parameter file and check and correct teh
        simulation parameters if needed.
        :param path_hbjson_simulation_parameter_file: str, path to the simulation parameter hbjson file
        :param path_file_epw: str, path to the epw file
        :param ddy_file: str, path to the ddy (design day) file
        :param overwrite: bool, if True, overwrite the existing simulation parameters
        :return flag_re_initialize_building_bes: bool, True if the building bes needs to be re-initialized because
        the simulation parameters or epw file were changed.
        """
        # Flag that the building bes needs to be re-initialized, it will be done by the Urban Canopy
        flag_re_initialize_building_bes = False

        """ If the simulation parameter file and epw file are already loaded and they should not be overwritten, 
        nothing should be done. """
        if self.hb_simulation_parameters_obj is not None and self.lb_epw_obj is not None and not overwrite:
            return flag_re_initialize_building_bes

        # Check if the simulation parameter file and epw file are valid and adjust them if needed
        hb_sim_parameter_obj, lb_epw_obj = check_simulation_parameters(
            path_hbjson_simulation_parameter_file=path_hbjson_simulation_parameter_file,
            path_file_epw=path_file_epw,
            ddy_file=ddy_file)
        # Set the simulation parameter and epw file
        self.hb_simulation_parameters_obj = hb_sim_parameter_obj
        self.lb_epw_obj = lb_epw_obj

        """ If the the simulation parameters and the epw should be overwritten, all the simulation that were run before
        have to be run again, thus the has_run attribute is set back to False and a flag is raised to re-initialize the
        bes of the buildings that run"""
        if overwrite:
            self.has_run = False
            flag_re_initialize_building_bes = True

        return flag_re_initialize_building_bes

    def write_epw_and_hb_simulation_parameters(self, path_ubes_temp_sim_folder):
        """
        Write the epw file and simulation parameters files to the temporary UBES simulation folder
        if they don't exist already.
        Return the path to the two files.
        :param path_ubes_temp_sim_folder: str, path to the UBES simulation folder
        :return path_file_epw: str, path to the epw file
        :return path_file_simulation_parameter: str, path to the simulation parameter file
        """
        # Path to the two files
        path_file_epw = os.path.join(path_ubes_temp_sim_folder, name_ubes_epw_file)
        path_file_simulation_parameter = os.path.join(path_ubes_temp_sim_folder,
                                                        name_ubes_hbjson_simulation_parameters_file)
        # Check if the epw files exist
        if not os.path.isfile(path_file_epw):
            self.lb_epw_obj.write(path_file_epw)
        # Check if the simulation parameter file exists
        if not os.path.isfile(path_file_simulation_parameter):
            with open(path_file_simulation_parameter, "w") as fp:
                json.dump(self.hb_simulation_parameters_obj.to_dict(), fp, indent=4)

        return path_file_epw, path_file_simulation_parameter



    def compute_ubes_results(self,bes_result_dict_list):
        """
        Compute the UBES results from the list of building energy simulation results.
        """
        # Sum the results
        self.ubes_results_dict = sum_dicts(bes_result_dict_list)



def sum_dicts(*args):
    """
    Sum the values dictionnaries
    # todo: same function as in solar_rad_and_bipv.py, gather  them somewhere
    """
    if not args:
        return {}
    # Initialize with teh first dict
    result_dict = args[0].copy()

    for d in args[1:]:
        for key in d:
            if isinstance(d[key], dict):
                result_dict[key] = sum_dicts(result_dict[key], d[key])
            elif isinstance(d[key], list):
                result_dict[key] = [x + y for x, y in zip(result_dict[key], d[key])]
            else:  # assuming ints or floats
                result_dict[key] += d[key]

    return result_dict













































