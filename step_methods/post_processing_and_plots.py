"""

"""

import logging

from urban_canopy.urban_canopy_additional_functions import UrbanCanopyAdditionalFunction

user_logger = logging.getLogger("user")  # f"{__name__} user"
dev_logger = logging.getLogger("dev")  # f"{__name__} dev"


class SimulationPostProcessingAndPlots:
    """ todo @Elie"""

    @staticmethod
    def generate_hb_model_contains_all_building_envelopes_to_plot_Grasshopper(urban_canopy_object,
                                                                              path_simulation_folder):
        """
            todo @Elie, change it, so tha it is writen in the json file
        """
        urban_canopy_object.make_HB_model_envelops_from_buildings(path_folder=path_simulation_folder)
        user_logger.info("HB model for the building envelop created successfully")
        dev_logger.info("HB model for the building envelop created successfully")


    @staticmethod
    def generate_csv_panels_simulation_results(urban_canopy_object, path_simulation_folder):
        UrbanCanopyAdditionalFunction.write_to_csv_panels_simulation_results(json_dict=urban_canopy_object.json_dict,
                                                                             building_dict=urban_canopy_object.
                                                                             building_dict,
                                                                             path_simulation_folder=
                                                                             path_simulation_folder)
        UrbanCanopyAdditionalFunction.write_to_csv_urban_canopy_results(building_dict=urban_canopy_object.building_dict,
                                                                        path_simulation_folder=path_simulation_folder)

    @staticmethod
    def plot_graphs_each_building(urban_canopy_object, path_simulation_folder, study_duration_years, country_ghe_cost):
        urban_canopy_object.plot_graphs_buildings(path_simulation_folder=path_simulation_folder,
                                                  study_duration_years=study_duration_years,
                                                  country_ghe_cost=country_ghe_cost)

    @staticmethod
    def plot_graphs_total_urban_canopy(urban_canopy_object, path_simulation_folder, study_duration_years,
                                       country_ghe_cost):
        urban_canopy_object.plot_graphs_urban_canopy(path_simulation_folder=path_simulation_folder,
                                                     study_duration_years=study_duration_years,
                                                     country_ghe_cost=country_ghe_cost)

    def plot_graphs(self):
        """
            todo @Elie
        """
