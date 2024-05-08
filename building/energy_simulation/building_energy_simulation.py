"""
Performs the energy simulation of a building using the EnergyPlus software and saves the results in a dictionary.
"""

import os
import logging
import shutil

from time import time
from copy import deepcopy

from honeybee.model import Model
from honeybee_energy.run import to_openstudio_osw, run_osw, run_idf
from honeybee_energy.result.eui import eui_from_sql

user_logger = logging.getLogger("user")
dev_logger = logging.getLogger("dev")

empty_bes_results_dict = {
    "heating": {"monthly": [], "monthly_cumulative": [], "yearly": None},
    "cooling": {"monthly": [], "monthly_cumulative": [], "yearly": None},
    "equipment": {"monthly": [], "monthly_cumulative": [], "yearly": None},
    "lighting": {"monthly": [], "monthly_cumulative": [], "yearly": None},
    # "ventilation": {"monthly": [], "monthly_cumulative": [], "yearly": None},  # Unused for now
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

    def set_cop(self, cop_heating, cop_cooling):
        """
        Set the coefficient of performance of the heating and cooling systems.
        :param cop_heating: float, coefficient of performance of the heating system
        :param cop_cooling: float, coefficient of performance of the cooling system
        """
        self.cop_heating = cop_heating
        self.cop_cooling = cop_cooling

    def to_dict(self):
        """
        Export the BuildingEnergySimulation object to a dictionary.
        :return: dict, BuildingEnergySimulation object as a dictionary
        """
        # todo check, make one for UC and make the UC add it to dict
        return {
            "building_id": self.building_id,
            "cop_heating": self.cop_heating,
            "cop_cooling": self.cop_cooling,
            "idf_generated": self.idf_generated,
            "has_run": self.has_run,
            "bes_results_dict": self.bes_results_dict,
            "sim_duration": self.sim_duration
        }

    def generate_idf_with_openstudio(self, path_building_bes_temp_folder, path_epw_file,
                                     path_hbjson_simulation_parameters, hb_model_obj: Model, silent=False):
        """
        Generate the idf file using OpenStudio.
        :param path_building_bes_temp_folder: str, path to the folder where the idf file will be saved
        :param path_epw_file: str, path to the epw file
        :param path_hbjson_simulation_parameters: str, path to the simulation parameter file
        :param hb_model_obj: Honeybee Model object
        :param silent: bool, if True, the EnergyPlus output will not be printed in the console
        """

        # Export the Honeybee Model to a hbjson file in the path_building_bes_temp_folder
        path_hbjson_file = hb_model_obj.to_hbjson(name=self.building_id, folder=path_building_bes_temp_folder)

        from_hbjson_to_idf(dir_to_write_idf_in=path_building_bes_temp_folder,
                           path_hbjson_file=path_hbjson_file,
                           path_epw_file=path_epw_file,
                           path_hbjson_simulation_parameters=path_hbjson_simulation_parameters, silent=silent)

        self.idf_generated = True

    def run_idf_with_energyplus(self, path_building_bes_temp_folder, path_epw_file, silent=False):
        """
        Run the energy simulation of the building.
        :param path_building_bes_temp_folder: str, path to the folder where the idf file will be saved
        :param path_epw_file: str, path to the epw file
        :param silent: bool, if True, the EnergyPlus output will not be printed in the console
        """
        # Get the path to the idf file and check if it exists
        path_idf_file = os.path.join(path_building_bes_temp_folder, "run", "in.idf")
        if os.path.isfile(path_idf_file) is False:
            raise ValueError("The idf file does not exist. Please generate it first.")
        # Run the simulation using EnergyPlus
        duration = time()
        run_idf(idf_file_path=path_idf_file, epw_file_path=path_epw_file, silent=silent)
        self.sim_duration = time() - duration

        self.has_run = True

    def move_result_files_from_temp_to_result_folder(self, path_ubes_temp_sim_folder,
                                                     path_ubes_sim_result_folder):
        """
        Move the result files from the temporary folder to the result folder.
        :param path_ubes_temp_sim_folder: str, path to the temporary folder
        :param path_ubes_sim_result_folder: str, path to the result folder
        """
        if self.has_run is False:
            return  # No result files to move
        # Paths to the temp and result BES folder
        path_bes_temp_folder = os.path.join(path_ubes_temp_sim_folder, self.building_id)
        path_bes_result_folder = os.path.join(path_ubes_sim_result_folder, self.building_id)
        # Paths to the results files
        path_eplusout_err = os.path.join(path_bes_temp_folder, "run", "eplusout.err")
        path_eplusout_sql = os.path.join(path_bes_temp_folder, "run", "eplusout.sql")
        path_idf = os.path.join(path_bes_temp_folder, "run", "in.idf")

        # Check if the simulation temp folder exists (and thus if there are result files to move)
        if not os.path.isdir(path_bes_temp_folder):
            return
        elif not os.path.isfile(path_eplusout_err) or not os.path.isfile(
                path_eplusout_sql) or not os.path.isfile(path_idf):
            user_logger.warning(
                f"The result files of the simulation of building id:{self.building_id} are missing. "
                f"It seems like an error occurred during  the idf generation of the simulation.")
            dev_logger.warning(
                f"The result files of the simulation of building id:{self.building_id} are missing. "
                f"It seems like an error occurred during  the idf generation of the simulation.")
            # delete the temp folder
            shutil.rmtree(path_bes_temp_folder, ignore_errors=True)
            return
        else:
            # Make the result folder if it does not exist
            if not os.path.isdir(path_bes_result_folder):
                os.mkdir(path_bes_result_folder)
            # Move the result and idf files to the result folder
            shutil.move(path_eplusout_err, path_bes_result_folder)
            shutil.move(path_eplusout_sql, path_bes_result_folder)
            shutil.move(path_idf, path_bes_result_folder)
            # Delete the temp folder
            shutil.rmtree(path_bes_temp_folder, ignore_errors=True)

    def extract_total_energy_use(self, path_ubes_sim_result_folder):
        """
        Extract the energy use intensity at the building scale from the result files.
        :param path_ubes_sim_result_folder: str, path to the result folder
        """
        if self.has_run is False:
            return  # No result files to move
        elif self.bes_results_dict is not None:
            return  # The results have already been extracted
        # Paths to the result BES folder
        path_bes_result_folder = os.path.join(path_ubes_sim_result_folder, self.building_id)
        # Paths to the results files
        path_eplusout_sql = os.path.join(path_bes_result_folder, "eplusout.sql")

        # Check if the BES result folder and the result files exist
        if not os.path.isdir(path_bes_result_folder):
            return
        elif not os.path.isfile(path_eplusout_sql):
            return
        # Initialize the results dictionary
        self.bes_results_dict = deepcopy(empty_bes_results_dict)
        # Extract the sql file
        eui_dict = eui_from_sql(path_eplusout_sql)
        total_floor_area = eui_dict["total_floor_area"]

        self.bes_results_dict["heating"]["yearly"] = eui_dict["end_uses"][
                                                         "Heating"] * total_floor_area / self.cop_heating
        self.bes_results_dict["cooling"]["yearly"] = eui_dict["end_uses"][
                                                         "Cooling"] * total_floor_area / self.cop_cooling
        self.bes_results_dict["equipment"]["yearly"] = eui_dict["end_uses"]["Electric Equipment"] * total_floor_area
        self.bes_results_dict["lighting"]["yearly"] = eui_dict["end_uses"]["Interior Lighting"] * total_floor_area
        # self.bes_results_dict["ventilation"]["yearly"] = eui_dict["end_uses"]["ventilation"] * total_floor_area
        self.bes_results_dict["total"]["yearly"] = sum([self.bes_results_dict["heating"]["yearly"],
                                                        self.bes_results_dict["cooling"]["yearly"],
                                                        self.bes_results_dict["equipment"]["yearly"],
                                                        # self.bes_results_dict["ventilation"]["yearly"],
                                                        self.bes_results_dict["lighting"]["yearly"]])

    def to_csv(self, path_ubes_sim_result_folder):
        """
        Export the results to a csv file.
        :param path_ubes_sim_result_folder: str, path to the result folder
        """
        if not self.has_run or self.bes_results_dict is None:
            return
        # Paths to the result BES folder
        path_bes_result_folder = os.path.join(path_ubes_sim_result_folder, self.building_id)
        # Paths to the results files
        path_csv_file = os.path.join(path_bes_result_folder, f"{self.building_id}_results.csv")
        # Check if the BES result folder and the result files exist
        if not os.path.isdir(path_bes_result_folder):
            return
        """ Write the file even if it exist already as monthly values could have been extracted 
        in the meantime """
        bes_result_dict_to_csv(bes_results_dict=self.bes_results_dict, path_csv_file=path_csv_file)

    def get_total_energy_consumption(self):
        """
        Get the total energy consumption of the building.
        :return: float, total energy consumption of the building
        """
        if self.has_run is False or self.bes_results_dict["total"]["yearly"] is None:
            user_logger.warning(
                f"The Building Energy Simulation has not been run yet for building id:{self.building_id}.")
            return 0.
        return self.bes_results_dict["total"]["yearly"]


def from_hbjson_to_idf(dir_to_write_idf_in, path_hbjson_file, path_epw_file,
                       path_hbjson_simulation_parameters, silent=False):
    """
    Convert a hbjson file to an idf file (input for EnergyPlus)
    """
    # pass the hbjson file to Openstudio to convert it to idf
    osw = to_openstudio_osw(osw_directory=dir_to_write_idf_in,
                            model_path=path_hbjson_file,
                            sim_par_json_path=path_hbjson_simulation_parameters,
                            epw_file=path_epw_file)
    ## Run simulation in OpenStudio to generate IDF ##
    (path_osm, path_idf) = run_osw(osw, silent=silent)


def bes_result_dict_to_csv(bes_results_dict, path_csv_file):
    """
    Export the results to a csv file.
    :param bes_results_dict: dict, results of the building energy simulation
    :param path_csv_file: str, path to the csv file
    :return: bool, True if the file was written
    """
    # Write the results to a csv file
    month_list = ["January", "February", "March", "April", "May", "June", "July", "August", "September",
                  "October", "November", "December"]
    with open(path_csv_file, 'w') as f:
        f.write(" ,")  # Empty cell for the first column
        for header in bes_results_dict.keys():
            f.write(header + ",")
        f.write("\n")
        for index, month in enumerate(month_list):
            f.write(f"{month},")
            for key, value in bes_results_dict.items():
                if value['monthly'] != []:
                    monthly_value = value['monthly'][index]
                else:
                    monthly_value = None
                f.write(f"{monthly_value},")
            f.write("\n")
        f.write("Total,")
        for key, value in bes_results_dict.items():
            f.write(f"{value['yearly']},")


def clean_directory(path):
    """

    """
    if os.path.exists(path):
        shutil.rmtree(path)
    os.mkdir(path)
