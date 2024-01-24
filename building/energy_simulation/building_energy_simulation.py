"""
Performs the energy simulation of a building using the EnergyPlus software and saves the results in a dictionary.
"""

import os
import logging

from time import time
from copy import deepcopy

from honeybee_energy.run import to_openstudio_osw, run_osw, run_idf
from honeybee.model import Model

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
        self.idf_generated = False
        self.has_run = False
        # Results
        self.bes_results_dict = None
        # Simulation tracking
        self.sim_duration = None

    def re_initialize(self, keep_idf=False, keep_run=False):
        """
        Re-initialize the values of the attributes of the BuildingEnergySimulation object.
        """
        # Parameters
        self.cop_heating = None
        self.cop_cooling = None
        # Flags
        if not keep_idf:
            self.idf_generated = False
        if not keep_run:
            self.has_run = False
        # Results
        self.bes_results_dict = None

    def set_parameters(self, hb_simulation_parameter_obj, epw_name, cop_heating, cop_cooling):
        """

        """

    def generate_idf_with_openstudio(self, path_building_bes_temp_folder, path_epw_file,
                                     path_hbjson_simulation_parameters, hb_model_obj: Model):
        """
        Generate the idf file using OpenStudio.
        :param path_building_bes_temp_folder: str, path to the folder where the idf file will be saved
        :param path_epw_file: str, path to the epw file
        :param path_hbjson_simulation_parameters: str, path to the simulation parameter file
        :param hb_model_obj: Honeybee Model object
        """
        # Export the Honeybee Model to a hbjson file in the path_building_bes_temp_folder
        path_hbjson_file = hb_model_obj.to_hbjson(name=self.building_id, folder=path_building_bes_temp_folder)

        from_hbjson_to_idf(dir_to_write_idf_in=path_building_bes_temp_folder,
                           path_hbjson_file=path_hbjson_file,
                           path_epw_file=path_epw_file,
                           path_hbjson_simulation_parameters=path_hbjson_simulation_parameters)

        self.idf_generated = True

    def run_idf_with_energyplus(self, path_building_bes_temp_folder, path_epw_file, silent=False):
        """
        Run the energy simulation of the building.
        :param path_building_bes_temp_folder: str, path to the folder where the idf file will be saved
        :param path_epw_file: str, path to the epw file
        :param silent: bool, if True, the EnergyPlus output will not be printed in the console
        """
        # Get the path to the idf file and check if it exists
        path_idf_file = os.path.join(path_building_bes_temp_folder,"run", "in.idf")
        if os.path.isfile(path_idf_file) is False:
            raise ValueError("The idf file does not exist. Please generate it first.")
        # Run the simulation using EnergyPlus
        duration = time()
        run_idf(idf_file_path=path_idf_file, epw_file_path=path_epw_file, silent=silent)
        self.sim_duration = time() - duration

        self.has_run = True


def from_hbjson_to_idf(dir_to_write_idf_in, path_hbjson_file, path_epw_file,
                       path_hbjson_simulation_parameters):
    """
    Convert a hbjson file to an idf file (input for EnergyPlus)
    """
    # pass the hbjson file to Openstudio to convert it to idf
    osw = to_openstudio_osw(osw_directory=dir_to_write_idf_in,
                            model_path=path_hbjson_file,
                            sim_par_json_path=path_hbjson_simulation_parameters,
                            epw_file=path_epw_file)
    ## Run simulation in OpenStudio to generate IDF ##
    (path_osm, path_idf) = run_osw(osw, silent=False)
