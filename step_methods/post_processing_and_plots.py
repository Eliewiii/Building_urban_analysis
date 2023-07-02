"""

"""

from mains_tool.utils_general import *
from urban_canopy.utils_urban_canopy import *


class SimulationPostProcessingAndPlots:
    """ todo @Elie"""

    @staticmethod
    def generate_hb_model_contains_all_building_envelopes_to_plot_Grasshopper(urban_canopy_object,
                                                                              path_folder_simulation):
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

    @staticmethod
    def generate_csv_panels_simulation_results(urban_canopy_object, path_folder_simulation):
        UrbanCanopyAdditionalFunction.write_to_csv_panels_simulation_results(json_dict=urban_canopy_object.json_dict,
                                                                             building_dict=urban_canopy_object.
                                                                             building_dict,
                                                                             path_folder_simulation=
                                                                             path_folder_simulation)

    @staticmethod
    def plot_graphs(urban_canopy_object, path_folder_simulation, study_duration_years, country_ghe_cost):
        urban_canopy_object.plot_graphs(path_folder_simulation=path_folder_simulation,
                                        study_duration_years=study_duration_years,
                                        country_ghe_cost=country_ghe_cost)

