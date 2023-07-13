"""

"""

from mains_tool.utils_general import *
from urban_canopy_pack.utils_urban_canopy import *

user_logger = logging.getLogger("user")  # f"{__name__} user"
dev_logger = logging.getLogger("dev")  # f"{__name__} dev"


class SimulationPostProcessingAndPlots:
    """ todo @Elie"""

    @staticmethod
    def generate_hb_model_contains_all_building_envelopes_to_plot_Grasshopper(urban_canopy_object,
                                                                              path_folder_simulation):
        """
            todo @Elie, change it, so tha it is writen in the json file
        """
        urban_canopy_object.make_HB_model_envelops_from_buildings(path_folder=path_folder_simulation)
        user_logger.info("HB model for the building envelop created successfully")
        dev_logger.info("HB model for the building envelop created successfully")

    @staticmethod
    def add_building_envelops_to_urban_canopy_json(urban_canopy_object):
        """

        :param urban_canopy_object:
        """
        urban_canopy_object.add_hb_model_envelop_to_json_dict()
        user_logger.info(" ")  # todo
        dev_logger.info(" ")  # todo

    @staticmethod
    def generate_csv_panels_simulation_results(urban_canopy_object, path_folder_simulation):
        UrbanCanopyAdditionalFunction.write_to_csv_panels_simulation_results(json_dict=urban_canopy_object.json_dict,
                                                                             building_dict=urban_canopy_object.
                                                                             building_dict,
                                                                             path_folder_simulation=
                                                                             path_folder_simulation)

    @staticmethod
    def plot_graphs_each_building(urban_canopy_object, path_folder_simulation, study_duration_years, country_ghe_cost):
        urban_canopy_object.plot_graphs_buildings(path_folder_simulation=path_folder_simulation,
                                                  study_duration_years=study_duration_years,
                                                  country_ghe_cost=country_ghe_cost)

    @staticmethod
    def plot_graphs_total_urban_canopy(urban_canopy_object, path_folder_simulation, study_duration_years,
                                       country_ghe_cost):
        urban_canopy_object.plot_graphs_urban_canopy(path_folder_simulation=path_folder_simulation,
                                                     study_duration_years=study_duration_years,
                                                     country_ghe_cost=country_ghe_cost)
