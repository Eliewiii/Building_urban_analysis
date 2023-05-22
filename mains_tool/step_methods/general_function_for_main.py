"""
Common methods to most of the simulations
"""

from mains_tool.utils_general import *
from mains_tool.step_methods.utils_step_methods import *

class SimulationCommonMethods:
    # todo @Sharon: should we really make global variables?, can it interfere with some parameters with the same name
    @staticmethod
    def make_simulation_folder(path_folder_simulation):
        """ #todo @Elie"""
        # make simulation folder
        os.makedirs(path_folder_simulation, exist_ok=True)
        # make the folder that will contain the logs of the simulation for the components in Grasshopper
        os.makedirs(os.path.join(path_folder_simulation,name_folder_gh_components_logs), exist_ok=True)
        # make the folder that will contain the temporary files of the simulation
        os.makedirs(os.path.join(path_folder_simulation,name_folder_temporary_files), exist_ok=True)


    @staticmethod
    def create_or_load_urban_canopy_object(path_folder_simulation):
        # todo @Elie, correct the function
        path_urban_canopy_pkl = os.path.join(path_folder_simulation, "urban_canopy.pkl")
        if os.path.isfile(path_urban_canopy_pkl):
            urban_canopy = UrbanCanopy.make_urban_canopy_from_pkl(path_urban_canopy_pkl)
            logging.info("An urban canopy already exist in the simulation folder, the input GIS will be added to it")
        else:
            urban_canopy = UrbanCanopy()
            logging.info("New urban canopy object was created")
        return urban_canopy

    @staticmethod
    def save_urban_canopy_object_to_pickle(urban_canopy_object,path_folder_simulation):
        """ #todo"""
        # todo @Elie, correct the function
        urban_canopy_object.export_urban_canopy_to_pkl(path_folder=path_folder_simulation)
        logging.info("Urban canopy object saved successfully")

    @staticmethod
    def save_urban_canopy_to_json(urban_canopy_object,path_folder_simulation):
        """ todo @Elie"""

        # todo @Elie after checking/correcting the code of Hilany


    @staticmethod
    def write_gh_component_user_logs(path_folder_simulation, name_gh_component,logs):
        """ todo @Elie"""
        # todo @Elie, write th elogs in path_folder_simulation/gh_components_logs/name_gh_component.log
        # gh_components_logs variable is defined in utils_general.py