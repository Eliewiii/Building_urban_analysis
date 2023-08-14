"""
todo
"""

import os
import logging
import shutil

from honeybee_radiance.sensorgrid import SensorGrid

from building.solar_radiations_and_panel.utils_sensorgrid import generate_sensor_grid_for_hb_model
from building.solar_radiations_and_panel.utils_solar_radiation import \
    run_hb_model_annual_irradiance_simulation, \
    move_radiation_results

from utils.utils_configuration import name_temporary_files_folder, name_radiation_simulation_folder

user_logger = logging.getLogger("user")
dev_logger = logging.getLogger("dev")

empty_parameter_dict = {
    "roof": {
        "grid_x": None,
        "grid_y": None,
        "offset": None,
        "panel_technology": None
    },
    "facades": {
        "grid_x": None,
        "grid_y": None,
        "offset": None,
        "panel_technology": None
    },
    "minimum_ratio_energy_harvested_on_primary_energy": None,
    "study_duration_in_years": None,
    "replacement_scenario": {}
}
empty_results_dict = {
    "roof": {
        "annual_panel_irradiance_list": None,
        "energy_harvested": {"yearly": None, "total": None},
        "lca_cradle_to_installation_primary_energy": {"yearly": None, "total": None},
        "lca_cradle_to_installation_carbon": {"yearly": None, "total": None},
        "dmfa_waste": {"yearly": None, "total": None},
        "lca_recycling_primary_energy": {"yearly": None, "total": None},
        "lca_recycling_carbon": {"yearly": None, "total": None}
    },
    "facades": {
        "annual_panel_irradiance_list": None,
        "energy_harvested": {"yearly": None, "total": None},
        "lca_cradle_to_installation_primary_energy": {"yearly": None, "total": None},
        "lca_cradle_to_installation_carbon": {"yearly": None, "total": None},
        "dmfa_waste": {"yearly": None, "total": None},
        "lca_recycling_primary_energy": {"yearly": None, "total": None},
        "lca_recycling_carbon": {"yearly": None, "total": None}
    },
"facades": {
        "energy_harvested": {"yearly": None, "total": None},
        "lca_cradle_to_installation_primary_energy": {"yearly": None, "total": None},
        "lca_cradle_to_installation_carbon": {"yearly": None, "total": None},
        "dmfa_waste": {"yearly": None, "total": None},
        "lca_recycling_primary_energy": {"yearly": None, "total": None},
        "lca_recycling_carbon": {"yearly": None, "total": None}
    }
}


class SolarRadAndBipvSimulation:
    """

    """

    def __init__(self):
        """
        todo @Elie
        """
        self.on_roof = False
        self.on_facade = False
        # SensorGrid objects
        self.roof_sensorgrid_dict = None
        self.facade_sensorgrid_dict = None
        # Panel objects
        self.roof_panel_list = None
        self.facade_panel_list = None
        # results
        self.results_dict = empty_results_dict
        # parameters
        self.parameter_dict = empty_parameter_dict

    def set_mesh_paraneters(self, do_simulation_on_roof, do_simulation_on_facade, roof_grid_size_x=1,
                            facade_grid_size_x=1, roof_grid_size_y=1, facade_grid_size_y=1, offset_dist=0.1):
        """
        Set the mesh parameters for the simulation
        :param do_simulation_on_roof: bool: default=True
        :param do_simulation_on_facade: bool: default=True
        :param roof_grid_size_x: Number for the size of the test grid
        :param facade_grid_size_x: Number for the size of the test grid
        :param roof_grid_size_y: Number for the size of the test grid
        :param facade_grid_size_y: Number for the size of the test grid
        :param offset_dist: Number for the distance to move points from the surfaces of the geometry of the model.
        """
        self.on_roof = do_simulation_on_roof
        self.on_facade = do_simulation_on_facade
        self.parameter_dict["roof"]["grid_x"] = roof_grid_size_x
        self.parameter_dict["roof"]["grid_y"] = roof_grid_size_y
        self.parameter_dict["facades"]["grid_x"] = facade_grid_size_x
        self.parameter_dict["facades"]["grid_y"] = facade_grid_size_y
        self.parameter_dict["roof"]["offset"] = offset_dist
        self.parameter_dict["facades"]["offset"] = offset_dist

    def generate_sensorgrids(self, hb_model_obj, roof_grid_size_x=1, facade_grid_size_x=1, roof_grid_size_y=1,
                             facade_grid_size_y=1, offset_dist=0.1):
        """Create a HoneyBee SensorGrid from a HoneyBe model for the roof, the facades or both and add it to the
        model
        todo @Elie
        :param grid_size : Number for the size of the test grid
        :param offset_dist : Number for the distance to move points from the surfaces of the geometry of the model. Typically, this
        :param on_roof: bool: default=True
        :param on_facades: bool: default=True"""

        if self.on_roof:
            self.roof_sensorgrid_dict = generate_sensor_grid_for_hb_model(hb_model_obj, roof_grid_size_x,
                                                                          roof_grid_size_y, offset_dist,
                                                                          "roof")
        elif self.on_facade:
            self.facade_sensorgrid_dict = generate_sensor_grid_for_hb_model(hb_model_obj, facade_grid_size_x,
                                                                            facade_grid_size_y, offset_dist,
                                                                            "facades")


        else:
            user_logger.warning(f"You did not precise whether you want to run the simulation on the roof, "
                                f"the facades or both")
            dev_logger.warning(f"You did not precise whether you want to run the simulation on the roof, "
                               f"the facades or both")

    def run_annual_solar_radiation(self, building_id, hb_model_obj, context_shading_hb_aperture_list,
                                   path_folder_simulation, path_epw_file, overwrite=False,
                                   north_angle=0, silent=False):
        """

        """
        path_folder_run_radiation_temp = os.path.join(path_folder_simulation, name_temporary_files_folder,
                                                      str(building_id))
        path_result_folder = os.path.join(path_folder_simulation, name_radiation_simulation_folder,
                                          str(building_id))
        annual_irradiance_file_name = str(building_id) + ".ill"

        # Distinguish between roof and facades
        if self.roof_sensorgrid_dict is not None:
            # Check if the simulation has already been run
            if self.results_dict["roof"]["annual_panel_irradiance_list"] is None or overwrite:
                # Make a copy of the Honeybee Model and add the sensorgrid and context to it
                hb_model_copy_roof = hb_model_obj.duplicate()
                hb_model_copy_roof.properties.radiance.add_sensor_grid(
                    SensorGrid.from_dict(self.roof_sensorgrid_dict))
                hb_model_copy_roof.add_shades(context_shading_hb_aperture_list)
                # run in the temporary folder
                path_folder_run_radiation_temp_roof = os.path.join(path_folder_run_radiation_temp, "roof")
                self.results_dict["roof"][
                    "annual_panel_irradiance_list"] = run_hb_model_annual_irradiance_simulation(
                    hb_model_obj=hb_model_obj,
                    path_folder_run=path_folder_run_radiation_temp_roof,
                    path_weather_file=path_epw_file,
                    timestep=1,
                    visible=False, north=north_angle,
                    radiance_parameters='-ab 2 -ad 5000 -lw 2e-05',
                    silent=silent)
                # Delete the useless results files and mov ethe results to the right folder
                annual_irradiance_roof_result_file_name = "roof" + ".ill"
                path_temp_result_folder_roof = path_folder_run_radiation_temp_roof = os.path.join(
                    path_folder_simulation, name_temporary_files_folder, str(building_id), "roof",
                    "annual_irradiance",
                    "results", "total")
                move_radiation_results(path_temp_result_folder=path_temp_result_folder_roof,
                                       path_result_folder=path_result_folder,
                                       result_file_name=annual_irradiance_file_name,
                                       new_result_file_name=annual_irradiance_roof_result_file_name)

        # Do not run the simulation if there is no SensorGrid on the facades
        if self.facade_sensorgrid_dict is not None:
            # Check if the simulation has already been run
            if self.results_dict["facades"]["annual_panel_irradiance_list"] is None or overwrite:
                # Make a copy of the Honeybee Model and add the SensorGrid and context to it
                hb_model_copy_facade = hb_model_obj.duplicate()
                hb_model_copy_facade.properties.radiance.add_sensor_grid(
                    SensorGrid.from_dict(self.facade_sensorgrid_dict))
                hb_model_copy_facade.add_shades(context_shading_hb_aperture_list)
                # run in the temporary folder
                path_folder_run_radiation_temp_facade = os.path.join(path_folder_run_radiation_temp, "facades")
                self.results_dict["facades"][
                    "annual_panel_irradiance_list"] = run_hb_model_annual_irradiance_simulation(
                    hb_model_obj=hb_model_obj,
                    path_folder_run=path_folder_run_radiation_temp_facade,
                    path_weather_file=path_epw_file,
                    timestep=1,
                    visible=False, north=north_angle,
                    radiance_parameters='-ab 2 -ad 5000 -lw 2e-05',
                    silent=silent)
                # Delete the useless results files and mov ethe results to the right folder
                annual_irradiance_facade_result_file_name = "facades" + ".ill"
                path_temp_result_folder_facade = path_folder_run_radiation_temp_facade = os.path.join(
                    path_folder_simulation, name_temporary_files_folder, str(building_id), "facades",
                    "annual_irradiance", "results", "total")
                move_radiation_results(path_temp_result_folder=path_temp_result_folder_facade,
                                       path_result_folder=path_result_folder,
                                       result_file_name=annual_irradiance_file_name,
                                       new_result_file_name=annual_irradiance_facade_result_file_name)

        # delete all the temporary files if they exist
        if os.path.isdir(path_folder_run_radiation_temp):
            shutil.rmtree(path_folder_run_radiation_temp)
