"""
Common methods to most of the simulations
"""

from mains_tool.utils_general import *
from mains_tool.step_methods.load_bat_file_arguments import LoadArguments

class SimulationCommonMethods:
    global path_folder_simulation, path_additional_gis_attribute_key_dict, \
            path_gis, move_buildings_to_origin, unit, make_hb_model_envelops, path_folder_hbjson, parser
    # todo @Sharon: should we really make global variables?, can it interfere with some parameters with the same name
    @staticmethod
    def load_bat_file_user_arguments(parser):
        """

        :param parser:
        :return:
        """
        LoadArguments.load_user_parameters(parser)
        LoadArguments.load_user_simulation_steps(parser)
        LoadArguments.parse_arguments(parser)

        return parser

    @staticmethod
    def make_simulation_folder(path_folder_simulation):
        os.makedirs(path_folder_simulation, exist_ok=True)

    @staticmethod
    def create_or_load_urban_canopy_object(path_folder_simulation):
        path_urban_canopy_pkl = os.path.join(path_folder_simulation, "urban_canopy.pkl")
        if os.path.isfile(path_urban_canopy_pkl):
            urban_canopy = UrbanCanopy.make_urban_canopy_from_pkl(path_urban_canopy_pkl)
            logging.info("An urban canopy already exist in the simulation folder, the input GIS will be added to it")
        else:
            urban_canopy = UrbanCanopy()
            logging.info("New urban canopy object was created")
        return urban_canopy

    @staticmethod
    def save_urban_canopy_object_to_pickle(path_folder_simulation):
        UrbanCanopy.export_urban_canopy_to_pkl(path_folder=path_folder_simulation)
        logging.info("Urban canopy object saved successfully")
