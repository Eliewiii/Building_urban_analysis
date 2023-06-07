from mains_tool.utils_general import *


class SolarOrPanelSimulation:

    @staticmethod
    def solar_radiation_simulation(urban_canopy_object, path_folder_simulation, path_weather_file, list_id, grid_size,
                                   offset_dist, on_roof, on_facades):
        """
        Run solar radiation simulation
        """

        urban_canopy_object.radiation_simulation_urban_canopy(path_folder_simulation, path_weather_file, list_id,
                                                              grid_size, offset_dist, on_roof, on_facades)
        logging.info("The solar radiation simulation was run on the buildings of the urban canopy")

    @staticmethod
    def panel_simulation(urban_canopy_object, path_folder_simulation, path_pv_tech_dictionary_json, id_pv_tech_roof,
                         id_pv_tech_facades, study_duration_in_years, replacement_scenario):
        """
        Run panel simulation
        """

        urban_canopy_object.run_panel_simulation(path_folder_simulation, path_pv_tech_dictionary_json, id_pv_tech_roof,
                                                 id_pv_tech_facades, study_duration_in_years, replacement_scenario)
        logging.info("The panel simulation was run on the buildings of the urban canopy")
