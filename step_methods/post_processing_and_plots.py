"""

"""

from mains_tool.utils_general import *


class SimulationPostProcessingAndPlots:
    """ todo @Elie"""
    @staticmethod
    def generate_hb_model_contains_all_building_envelopes_to_plot_Grasshopper(urban_canopy_object,path_folder_simulation):
        """
            todo @Elie, change it, so tha it is writen in the json file
        """
        urban_canopy_object.make_HB_model_envelops_from_buildings(path_folder=path_folder_simulation)
        logging.info("HB model for the building envelop created successfully")

    @staticmethod
    def add_building_envelops_to_urban_canopy_json(urban_canopy_object):
        """

        :param urban_canopy_object:
        """
        urban_canopy_object.add_hb_model_envelop_to_json_dict()
        logging.info(" ")  # todo
