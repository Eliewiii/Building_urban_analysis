"""
Utils Functions for running the coupled simulation with PyFMI
"""

import os

from utils.utils_file_folder_functions import clean_directory


def initialize_models(model_list, path_to_run_temp_fmu_list, start_time: int, end_time: int):
    """
    Initialize the models before the simulation
    :param model_list: list of models
    :param path_to_run_temp_fmu_list: list of paths to the temporary directories to run the FMUs
    :param start_time: start time of the simulation
    :param end_time: end time of the simulation
    :return:
    """
    for count, (model, path_to_run_temp_fmu) in enumerate(zip(model_list, path_to_run_temp_fmu_list)):
        # Create a temporary directory to run the FMU in the directory of the FMU
        clean_directory(path_to_run_temp_fmu)
        # Change the working directory to the temporary directory
        os.chdir(path_to_run_temp_fmu)
        cur_dir = os.getcwd()
        # Set the start and end time of the simulation
        model.setup_experiment(start_time=start_time, stop_time=end_time)
        # Initialize the model
        """ In the case of EnergyPlus, it runs the warmup period as define in the IDF file 
        (defined by the Honeybee simulation parameters) """
        model.initialize()
