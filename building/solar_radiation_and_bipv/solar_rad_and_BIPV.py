"""
todo
"""

import os
import logging
import shutil
import csv

from copy import deepcopy
from datetime import datetime

from honeybee_radiance.sensorgrid import SensorGrid

from building.solar_radiation_and_bipv.utils_sensorgrid import generate_sensor_grid_for_hb_model
from building.solar_radiation_and_bipv.utils_solar_radiation import \
    run_hb_model_annual_irradiance_simulation, \
    move_annual_irr_hb_radiance_results
from building.solar_radiation_and_bipv.utils_bipv import init_bipv_on_sensor_grid, \
    bipv_energy_harvesting_simulation_yearly_annual_irradiance, \
    bipv_energy_harvesting_simulation_hourly_annual_irradiance, bipv_lca_dmfa_eol_computation

from utils.utils_configuration import name_temporary_files_folder, name_radiation_simulation_folder

user_logger = logging.getLogger("user")
dev_logger = logging.getLogger("dev")

empty_sub_parameter_dict = {
    "grid_x": None,
    "grid_y": None,
    "offset": None,
    "panel_technology": None,
    "minimum_panel_eroi": None,
    "start_year": None,
    "study_duration_in_years": 0,
    "replacement_scenario": {"id": None,
                             "replacement_frequency_year": None},
    "efficiency_computation_method": {"id": None,
                                      "parameter": None}
}

empty_parameter_dict = {
    "roof": deepcopy(empty_sub_parameter_dict),
    "facades": deepcopy(empty_sub_parameter_dict)
}
empty_sub_bipv_results_dict = {
    "energy_harvested": {"yearly": [], "cumulative": None, "total": None},
    "lca_primary_energy": {
        "material_extraction_and_manufacturing": {"yearly": [], "cumulative": None, "total": None},
        "transportation": {"yearly": [], "cumulative": None, "total": None},
        "recycling": {"yearly": [], "cumulative": None, "total": None},
        "total": {"yearly": [], "cumulative": None, "total": None}
    },
    "lca_carbon_footprint": {
        "material_extraction_and_manufacturing": {"yearly": [], "cumulative": None, "total": None},
        "transportation": {"yearly": [], "cumulative": None, "total": None},
        "recycling": {"yearly": [], "cumulative": None, "total": None},
        "total": {"yearly": [], "cumulative": None, "total": None}
    },
    "dmfa_waste": {"yearly": [], "cumulative": None, "total": None}
}

empty_bipv_results_dict = {
    "roof": deepcopy(empty_sub_bipv_results_dict),
    "facades": deepcopy(empty_sub_bipv_results_dict),
    "total": deepcopy(empty_sub_bipv_results_dict)
}

sun_up_hours_file_name = "sun-up-hours.txt"
name_roof_ill_file = "roof.ill"
name_facades_ill_file = "facades.ill"
name_roof_sun_up_hours_file = "roof_" + sun_up_hours_file_name
name_facades_sun_up_hours_file = "facades_" + sun_up_hours_file_name
name_results_file_csv = "bipv_results.csv"


class SolarRadAndBipvSimulation:
    """

    """

    def __init__(self):
        """
        todo @Elie
        """
        self.on_roof = False
        self.on_facades = False
        # SensorGrid objects
        self.roof_sensorgrid_dict = None
        self.facades_sensorgrid_dict = None
        # Panel objects
        self.roof_panel_list = None
        self.facades_panel_list = None
        # solar_irradiance results
        self.roof_annual_panel_irradiance_list = None
        self.facades_annual_panel_irradiance_list = None
        # bipv results
        self.bipv_results_dict = empty_bipv_results_dict
        # parameters
        self.parameter_dict = empty_parameter_dict

    def set_mesh_parameters(self, roof_or_facades, on_roof_or_facades, roof_grid_size_x=1, roof_grid_size_y=1,
                            offset_dist=0.1):
        """
        Set the mesh parameters for the simulation
        :param roof_or_facades: str: roof or facades
        :param on_roof_or_facades: bool: default=True, whether to run the simulation on the roof or the facades
        :param roof_grid_size_x: Number for the size of the test grid
        :param roof_grid_size_y: Number for the size of the test grid
        :param offset_dist: Number for the distance to move points from the surfaces of the geometry of the model.
        """
        if roof_or_facades == "roof":
            self.on_roof = on_roof_or_facades
        elif roof_or_facades == "facades":
            self.on_facades = on_roof_or_facades
        else:
            dev_logger.warning(f"The roof_or_facades parameter should be either roof or facades")
            return
        if on_roof_or_facades:
            self.parameter_dict[roof_or_facades]["grid_x"] = roof_grid_size_x
            self.parameter_dict[roof_or_facades]["grid_y"] = roof_grid_size_y
            self.parameter_dict[roof_or_facades]["offset"] = offset_dist

    def set_bipv_parameters(self, roof_or_facades, pv_tech_obj, minimum_panel_eroi,
                            study_duration_in_years, start_year, replacement_scenario,
                            efficiency_computation_method,
                            **kwargs):
        """
        Set the BIPV parameters for the simulation
        :param roof_or_facades: str: roof or facades
        :param pv_tech_obj: PVPanelTechnology object
        :param minimum_panel_eroi: float : the minimum EROI of the panels
        :param study_duration_in_years: int : the duration of the study in years
        :param start_year: int : the start year of the study
        :param replacement_scenario: str : the replacement scenario of the panels
        :param efficiency_computation_method: str : the method to compute the efficiency of the panels
        :param kwargs: dict : other parameters
        todo: add the additional parameters
        """
        self.parameter_dict[roof_or_facades]["panel_technology"] = pv_tech_obj
        self.parameter_dict[roof_or_facades]["minimum_panel_eroi"] = minimum_panel_eroi
        self.parameter_dict[roof_or_facades]["replacement_scenario"]["id"] = replacement_scenario
        self.parameter_dict[roof_or_facades]["efficiency_computation_method"]["id"] = efficiency_computation_method
        self.parameter_dict[roof_or_facades]["start_year"] = start_year
        # todo: add the additional paameters
        if "replacement_frequency_in_years" in kwargs.keys():
            self.parameter_dict[roof_or_facades]["replacement_scenario"][
                "replacement_frequency_in_years"] = kwargs["replacement_frequency_in_years"]

    def generate_sensor_grid(self, hb_model_obj, bipv_on_roof=True, bipv_on_facades=True, roof_grid_size_x=1,
                             facades_grid_size_x=1, roof_grid_size_y=1, facades_grid_size_y=1,
                             offset_dist=0.1, overwrite=False):
        """
        Generate the sensor grid for the BIPV simulation
        :param hb_model_obj: Honeybee model object
        :param bipv_on_roof: bool: default=True
        :param bipv_on_facades: bool: default=True
        :param roof_grid_size_x: Number for the size of the test grid
        :param facades_grid_size_x: Number for the size of the test grid
        :param roof_grid_size_y: Number for the size of the test grid
        :param facades_grid_size_y: Number for the size of the test grid
        :param offset_dist: Number for the distance to move points from the surfaces of the geometry
        :param overwrite: bool: Overwrite the existing mesh if there is one default=False

        of the model.
        """

        if not bipv_on_roof and not bipv_on_facades:
            user_logger.warning(f"You did not precise whether you want to run the simulation on the roof, "
                                f"the facades or both")
            dev_logger.warning(f"You did not precise whether you want to run the simulation on the roof, "
                               f"the facades or both")
            return

        # Generate the sensor grid on roof or facades
        if bipv_on_roof and (self.roof_sensorgrid_dict is None or overwrite):
            self.roof_sensorgrid_dict = generate_sensor_grid_for_hb_model(hb_model_obj, roof_grid_size_x,
                                                                          roof_grid_size_y, offset_dist,
                                                                          "roof")
            self.set_mesh_parameters(roof_or_facades="roof", on_roof_or_facades=bipv_on_roof,
                                     roof_grid_size_x=roof_grid_size_x, roof_grid_size_y=roof_grid_size_y,
                                     offset_dist=offset_dist)
        if bipv_on_facades and (self.facades_sensorgrid_dict is None or overwrite):
            self.facades_sensorgrid_dict = generate_sensor_grid_for_hb_model(hb_model_obj,
                                                                             facades_grid_size_x,
                                                                             facades_grid_size_y, offset_dist,
                                                                             "facades")
            self.set_mesh_parameters(roof_or_facades="facades", on_roof_or_facades=bipv_on_facades,
                                     facades_grid_size_x=facades_grid_size_x,
                                     facades_grid_size_y=facades_grid_size_y,
                                     offset_dist=offset_dist)

    def run_annual_solar_irradiance_simulation(self, path_simulation_folder, building_id, hb_model_obj,
                                               context_shading_hb_shade_list, path_epw_file, overwrite=False,
                                               north_angle=0, silent=False):
        """
        Run the annual solar radiation simulation for the roof and/or the facades
        :param path_simulation_folder: str : the path to the simulation folder
        :param building_id: int : the id of the building
        :param hb_model_obj: Honeybee Model object
        :param context_shading_hb_shade_list: list of Honeybee Aperture objects for the context shading
        :param path_epw_file: str : the path to the epw file
        :param overwrite: bool : whether to overwrite the existing results
        :param north_angle: float : the north angle of the building
        :param silent: bool : whether to print the logs or not
        """
        path_folder_run_radiation_temp = os.path.join(path_simulation_folder, name_temporary_files_folder,
                                                      str(building_id))
        path_result_folder = os.path.join(path_simulation_folder, name_radiation_simulation_folder,
                                          str(building_id))

        # Distinguish between roof and facades
        if self.roof_sensorgrid_dict is not None:
            # Check if the simulation has already been run
            if self.roof_annual_panel_irradiance_list is None or overwrite:
                # Make a copy of the Honeybee Model and add the sensorgrid and context to it
                hb_model_copy_roof = hb_model_obj.duplicate()
                hb_model_copy_roof.properties.radiance.add_sensor_grid(
                    SensorGrid.from_dict(self.roof_sensorgrid_dict))
                hb_model_copy_roof.add_shades(context_shading_hb_shade_list)
                # run in the temporary folder
                path_folder_run_radiation_temp_roof = os.path.join(path_folder_run_radiation_temp, "roof")
                self.roof_annual_panel_irradiance_list = run_hb_model_annual_irradiance_simulation(
                    hb_model_obj=hb_model_copy_roof,
                    path_folder_run=path_folder_run_radiation_temp_roof,
                    path_weather_file=path_epw_file,
                    timestep=1,
                    visible=False, north=north_angle,
                    radiance_parameters='-ab 2 -ad 5000 -lw 2e-05',
                    silent=silent)
                # Delete the useless results files and move the results to the right folder
                path_folder_result_run_radiation_temp_roof = os.path.join(path_folder_run_radiation_temp_roof,
                                                                          "annual_irradiance",
                                                                          "results", "total")
                annual_irradiance_file_name = SensorGrid.from_dict(
                    self.roof_sensorgrid_dict).identifier + ".ill"
                path_result_file_ill = os.path.join(path_folder_result_run_radiation_temp_roof,
                                                    annual_irradiance_file_name)
                path_sun_hours_file = os.path.join(path_folder_result_run_radiation_temp_roof,
                                                   sun_up_hours_file_name)
                move_annual_irr_hb_radiance_results(path_temp_ill_result_file=path_result_file_ill,
                                                    path_temp_sun_hours_file=path_sun_hours_file,
                                                    new_ill_file_name=name_roof_ill_file,
                                                    new_sun_hours_file_name=name_roof_sun_up_hours_file,
                                                    path_result_folder=path_result_folder)

        # Do not run the simulation if there is no SensorGrid on the facades
        if self.facades_sensorgrid_dict is not None:
            # Check if the simulation has already been run
            if self.facades_annual_panel_irradiance_list is None or overwrite:
                # Make a copy of the Honeybee Model and add the SensorGrid and context to it
                hb_model_copy_facades = hb_model_obj.duplicate()
                hb_model_copy_facades.properties.radiance.add_sensor_grid(
                    SensorGrid.from_dict(self.facades_sensorgrid_dict))
                hb_model_copy_facades.add_shades(context_shading_hb_shade_list)
                # run in the temporary folder
                path_folder_run_radiation_temp_facades = os.path.join(path_folder_run_radiation_temp,
                                                                      "facades")
                self.facades_annual_panel_irradiance_list = run_hb_model_annual_irradiance_simulation(
                    hb_model_obj=hb_model_copy_facades,
                    path_folder_run=path_folder_run_radiation_temp_facades,
                    path_weather_file=path_epw_file,
                    timestep=1,
                    visible=False, north=north_angle,
                    radiance_parameters='-ab 2 -ad 5000 -lw 2e-05',
                    silent=silent)
                # Delete the useless results files and mov ethe results to the right folder
                path_folder_result_run_radiation_temp_facades = os.path.join(
                    path_folder_run_radiation_temp_facades,
                    "annual_irradiance",
                    "results", "total")
                annual_irradiance_file_name = SensorGrid.from_dict(
                    self.facades_sensorgrid_dict).identifier + ".ill"
                path_result_file_ill = os.path.join(path_folder_result_run_radiation_temp_facades,
                                                    annual_irradiance_file_name)
                path_sun_hours_file = os.path.join(path_folder_result_run_radiation_temp_facades,
                                                   sun_up_hours_file_name)
                move_annual_irr_hb_radiance_results(path_temp_ill_result_file=path_result_file_ill,
                                                    path_temp_sun_hours_file=path_sun_hours_file,
                                                    new_ill_file_name=name_facades_ill_file,
                                                    new_sun_hours_file_name=name_facades_sun_up_hours_file,
                                                    path_result_folder=path_result_folder)
        # delete all the temporary files if they exist
        if os.path.isdir(path_folder_run_radiation_temp):
            shutil.rmtree(path_folder_run_radiation_temp)

    def run_bipv_panel_simulation(self, path_simulation_folder, building_id, roof_pv_tech_obj,
                                  facades_pv_tech_obj, uc_start_year, uc_current_year, uc_last_year,
                                  efficiency_computation_method="yearly",
                                  minimum_panel_eroi=1.2,
                                  replacement_scenario="replace_failed_panels_every_X_years",
                                  continue_simulation=False, **kwargs):
        """
        Run the simulation of the energy harvested by the bipvs
        :param path_simulation_folder: path to the simulation folder
        :param building_id: str: id of the building
        :param roof_pv_tech_obj: BipvTechnology object of the roof BIPV panels
        :param facades_pv_tech_obj: BipvTechnology object of the facades BIPV panels
        :param efficiency_computation_method: str: method to compute the efficiency of the panels
        :param minimum_panel_eroi: float: minimum EROI of the PV panels
        :param iteration_duration_in_years: int: duration of the iteration in years, optionnal parameter, relevant only
        :param current_year: int: start year of the iteration
        :param replacement_scenario: dict: replacement scenario of the panels
        :param kwargs: todo
        """
        # Set BIPV parameters

        # Init flags
        run_bipv_on_roof = False
        run_bipv_on_facades = False
        simulation_continued = False
        # Roof
        if self.on_roof and self.roof_sensorgrid_dict is not None and self.roof_annual_panel_irradiance_list is not None:
            run_bipv_on_roof = True

            # Init the BIPV panels on the roof if necessary
            if not continue_simulation or self.roof_panel_list is None:
                """ If there is no panel list, we init the panels, but if we want to continue the simulation and there 
                are already panels, we do not init them again """

                self.set_bipv_parameters(roof_pv_tech_obj=roof_pv_tech_obj, facades_pv_tech_obj=facades_pv_tech_obj,
                                         efficiency_computation_method=efficiency_computation_method,
                                         minimum_panel_eroi=minimum_panel_eroi,
                                         study_duration_in_years=uc_last_year - uc_current_year,
                                         start_year=uc_current_year,
                                         replacement_scenario=replacement_scenario, **kwargs)

                self.roof_panel_list = init_bipv_on_sensor_grid(
                    sensor_grid=SensorGrid.from_dict(self.roof_sensorgrid_dict),
                    pv_technology_obj=roof_pv_tech_obj,
                    annual_panel_irradiance_list=self.roof_annual_panel_irradiance_list,
                    minimum_panel_eroi=minimum_panel_eroi)

            else:  # If the simulation continue we keep the existing panels and the parameters
                simulation_continued = True
                # Update the panel technology,
                """ The new panel that will be installed will have the new technology, it will affect their efficiency 
                and the LCA and DMFA results. It will not affect the existing panels as the computation of LCA and DMFA
                is done at the moment of the installation of the panels and the panel know which panel technology they
                belong to."""
                # todo : maybe to make a function out of it
                if kwargs["update_panel"] == True:
                    self.parameter_dict["roof"]["panel_technology"] = roof_pv_tech_obj
                else:
                    roof_pv_tech_obj = self.parameter_dict["roof"]["panel_technology"]

                start_year = self.parameter_dict["start_year"]
                self.parameter_dict["study_duration_in_years"] = self.parameter_dict["start_year"] - uc_last_year

                efficiency_computation_method = self.parameter_dict["efficiency_computation_method"]["id"]
                # add the parameters if the efficiency computation method id needed
                minimum_panel_eroi = self.parameter_dict["minimum_panel_eroi"]
                replacement_scenario = self.parameter_dict["replacement_scenario"]["id"]
                # todo with the kwarg as well and put it ion a function eventually
                if self.parameter_dict["replacement_scenario"]["replacement_frequency_in_years"] is not None:
                    kwargs["replacement_frequency_in_years"] = self.parameter_dict["replacement_scenario"][
                        "replacement_frequency_in_years"]

            # Run the simulation roof
            if efficiency_computation_method == "yearly":
                roof_energy_harvested_yearly_list, roof_nb_of_panels_installed_yearly_list = bipv_energy_harvesting_simulation_yearly_annual_irradiance(
                    pv_panel_obj_list=self.roof_panel_list,
                    annual_solar_irradiance_value=self.roof_annual_panel_irradiance_list,
                    iteration_duration_in_years=iteration_duration_in_years,
                    replacement_scenario=replacement_scenario, **kwargs)
            # The hourly method is not implemented yet
            elif efficiency_computation_method == "hourly":
                path_result_folder = os.path.join(path_simulation_folder, name_radiation_simulation_folder,
                                                  str(building_id))
                path_ill_file = os.path.join(path_result_folder, name_roof_ill_file)
                path_sun_up_hours_file = os.path.join(path_result_folder, name_roof_sun_up_hours_file)
                roof_energy_harvested_yearly_list, roof_nb_of_panels_installed_yearly_list = bipv_energy_harvesting_simulation_hourly_annual_irradiance(
                    pv_panel_obj_list=self.roof_panel_list,
                    path_ill_file=path_ill_file,
                    path_sun_up_hours_file=path_sun_up_hours_file,
                    iteration_duration_in_years=iteration_duration_in_years,
                    replacement_scenario=replacement_scenario, **kwargs)
            else:
                raise ValueError("The efficiency computation method is not valid")
            # Post process and run LCA and DMFA results
            roof_primary_energy_material_extraction_and_manufacturing_yearly_list, \
                roof_primary_energy_transportation_yearly_list, roof_primary_energy_recycling_yearly_list, \
                roof_total_primary_energy_yearly_list, roof_carbon_transportation_yearly_list, \
                roof_carbon_material_extraction_and_manufacturing_yearly_list, \
                roof_carbon_recycling_yearly_list, roof_total_carbon_yearly_list, \
                roof_dmfa_waste_yearly_lis = bipv_lca_dmfa_eol_computation(
                nb_of_panels_installed_yearly_list=roof_nb_of_panels_installed_yearly_list,
                pv_tech_obj=roof_pv_tech_obj)
            # Save the results in obj
            self.bipv_results_dict["roof"] = self.add_results_to_dict(
                bipv_reults_dict=self.bipv_results_dict["roof"],
                energy_harvested_yearly_list=roof_energy_harvested_yearly_list,
                primary_energy_material_extraction_and_manufacturing_yearly_list=roof_primary_energy_material_extraction_and_manufacturing_yearly_list,
                primary_energy_transportation_yearly_list=roof_primary_energy_transportation_yearly_list,
                primary_energy_recycling_yearly_list=roof_primary_energy_recycling_yearly_list,
                carbon_material_extraction_and_manufacturing_yearly_list=roof_carbon_material_extraction_and_manufacturing_yearly_list,
                carbon_transportation_yearly_list=roof_carbon_transportation_yearly_list,
                carbon_recycling_yearly_list=roof_carbon_recycling_yearly_list,
                dmfa_waste_yearly_list=roof_dmfa_waste_yearly_lis)
            # Facade
        if self.on_facades and self.facades_sensorgrid_dict is not None and self.facade_annual_panel_irradiance_list is not None:
            run_bipv_on_facades = True
            # Init the BIPV panels on the facades if necessary
            if not continue_simulation or self.facades_panel_list is None:
                """ If there is no panel list, we init the panels, but if we want to continue the simulation and there 
                are already panels, we do not init them again """
                self.facades_panel_list = init_bipv_on_sensor_grid(
                    sensor_grid=SensorGrid.from_dict(self.facades_sensorgrid_dict),
                    pv_technology_obj=facades_pv_tech_obj,
                    annual_panel_irradiance_list=self.facade_annual_panel_irradiance_list,
                    minimum_panel_eroi=minimum_panel_eroi)
            else:
                simulation_continued = True
                # todo: add the parameters
            # Run the simulation facades
            if efficiency_computation_method == "yearly":
                facades_energy_harvested_yearly_list, facades_nb_of_panels_installed_yearly_list = bipv_energy_harvesting_simulation_yearly_annual_irradiance(
                    pv_panel_obj_list=self.facades_panel_list,
                    annual_solar_irradiance_value=self.facade_annual_panel_irradiance_list,
                    study_duration_in_years=study_duration_in_years,
                    replacement_scenario=replacement_scenario, **kwargs)
            elif efficiency_computation_method == "hourly":
                path_result_folder = os.path.join(path_simulation_folder, name_radiation_simulation_folder,
                                                  str(building_id))
                path_ill_file = os.path.join(path_result_folder, name_facades_ill_file)
                path_sun_up_hours_file = os.path.join(path_result_folder, name_facades_sun_up_hours_file)
                facades_energy_harvested_yearly_list, facades_nb_of_panels_installed_yearly_list = bipv_energy_harvesting_simulation_hourly_annual_irradiance(
                    pv_panel_obj_list=self.facades_panel_list,
                    path_ill_file=path_ill_file,
                    path_sun_up_hours_file=path_sun_up_hours_file,
                    study_duration_in_years=study_duration_in_years,
                    replacement_scenario=replacement_scenario, **kwargs)
            else:
                raise ValueError("The efficiency computation method is not valid")
                # Post process and run LCA and DMFA results
                facades_primary_energy_material_extraction_and_manufacturing_yearly_list, \
                    facades_primary_energy_transportation_yearly_list, facades_primary_energy_recycling_yearly_list, \
                    facades_carbon_transportation_yearly_list, \
                    facades_carbon_material_extraction_and_manufacturing_yearly_list, \
                    facades_carbon_recycling_yearly_list, \
                    facades_dmfa_waste_yearly_lis = bipv_lca_dmfa_eol_computation(
                    nb_of_panels_installed_yearly_list=facades_nb_of_panels_installed_yearly_list,
                    pv_tech_obj=facades_pv_tech_obj)

                # Save the results in obj
                self.bipv_results_dict["facades"] = self.add_results_to_dict(
                    bipv_reults_dict=self.bipv_results_dict["facades"],
                    energy_harvested_yearly_list=facades_energy_harvested_yearly_list,
                    primary_energy_material_extraction_and_manufacturing_yearly_list=facades_primary_energy_material_extraction_and_manufacturing_yearly_list,
                    primary_energy_transportation_yearly_list=facades_primary_energy_transportation_yearly_list,
                    primary_energy_recycling_yearly_list=facades_primary_energy_recycling_yearly_list,
                    carbon_material_extraction_and_manufacturing_yearly_list=facades_carbon_material_extraction_and_manufacturing_yearly_list,
                    carbon_transportation_yearly_list=facades_carbon_transportation_yearly_list,
                    carbon_recycling_yearly_list=facades_carbon_recycling_yearly_list,
                    dmfa_waste_yearly_list=facades_dmfa_waste_yearly_lis)

        # Total results
        if run_bipv_on_roof and run_bipv_on_facades:
            self.bipv_results_dict["total"] = sum_dicts(self.bipv_results_dict["roof"],
                                                        self.bipv_results_dict["facades"])
        elif run_bipv_on_roof:
            self.bipv_results_dict["total"] = self.bipv_results_dict["roof"]
        elif run_bipv_on_facades:
            self.bipv_results_dict["total"] = self.bipv_results_dict["facades"]
        else:
            None

        self.set_bipv_parameters(roof_pv_tech_obj=roof_pv_tech_obj, facades_pv_tech_obj=facades_pv_tech_obj,
                                 efficiency_computation_method=efficiency_computation_method,
                                 minimum_panel_eroi=minimum_panel_eroi,
                                 study_duration_in_years=study_duration_in_years, start_year=start_year,
                                 replacement_scenario=replacement_scenario, **kwargs)

    def run_bipv_panel_simulation(self):
        """

        """

        run_bipv_on_roof = self.run_bipv_panel_simulation_on_roof_or_facades(roof_or_facades="roof")
        run_bipv_on_facades = self.run_bipv_panel_simulation_on_roof_or_facades(roof_or_facades="facades")

        # Total results
        if run_bipv_on_roof and run_bipv_on_facades:
            self.bipv_results_dict["total"] = sum_dicts(self.bipv_results_dict["roof"],
                                                        self.bipv_results_dict["facades"])
        elif run_bipv_on_roof:
            self.bipv_results_dict["total"] = self.bipv_results_dict["roof"]
        elif run_bipv_on_facades:
            self.bipv_results_dict["total"] = self.bipv_results_dict["facades"]
        else:
            None

    def run_bipv_panel_simulation_on_roof_or_facades(self, roof_or_facades, on_roof_or_facades, sensorgrid_dict,
                                                     annual_panel_irradiance_list, panel_list, path_simulation_folder,
                                                     building_id, pv_tech_obj,
                                                     uc_last_year,
                                                     efficiency_computation_method, minimum_panel_eroi, uc_current_year,
                                                     study_duration_in_years, start_year, replacement_scenario,
                                                     continue_simulation=False, **kwargs):
        """

        """
        # Condition to run the simulation
        if on_roof_or_facades and sensorgrid_dict is not None and annual_panel_irradiance_list is not None:
            simulation_has_run = True  # run flag

            # Init the BIPV panels if necessary
            if not continue_simulation or self.roof_panel_list is None:
                """ If there is no panel list, we init the panels, but if we want to continue the simulation and there 
                are already panels, we do not init them again """

                self.set_bipv_parameters(roof_or_facades=roof_or_facades, pv_tech_obj=pv_tech_obj,
                                         efficiency_computation_method=efficiency_computation_method,
                                         minimum_panel_eroi=minimum_panel_eroi,
                                         study_duration_in_years=uc_last_year - uc_current_year,
                                         start_year=uc_current_year,
                                         replacement_scenario=replacement_scenario, **kwargs)

                panel_list = init_bipv_on_sensor_grid(
                    sensor_grid=SensorGrid.from_dict(sensorgrid_dict),
                    pv_technology_obj=pv_tech_obj,
                    annual_panel_irradiance_list=annual_panel_irradiance_list,
                    minimum_panel_eroi=minimum_panel_eroi)

            # If the simulation continue we keep the existing panels and the parameters
            else:
                simulation_continued = True
                # Update the panel technology,
                """ The new panel that will be installed will have the new technology, it will affect their efficiency 
                and the LCA and DMFA results. It will not affect the existing panels as the computation of LCA and DMFA
                is done at the moment of the installation of the panels and the panel know which panel technology they
                belong to."""
                if kwargs["update_panel_technology"]:
                    self.parameter_dict[roof_or_facades]["panel_technology"] = pv_tech_obj
                else:
                    pv_tech_obj = self.parameter_dict[roof_or_facades]["panel_technology"]
                # Update the study duiration and keep the start year
                start_year = self.parameter_dict["start_year"]
                self.parameter_dict["study_duration_in_years"] = self.parameter_dict["start_year"] - uc_last_year
                # Keep all the other parameters
                efficiency_computation_method = self.parameter_dict["efficiency_computation_method"][
                    "id"]  # add the parameters if the efficiency computation method id needed
                minimum_panel_eroi = self.parameter_dict["minimum_panel_eroi"]
                replacement_scenario = self.parameter_dict["replacement_scenario"]["id"]
                # todo with the kwarg as well and put it ion a function eventually
                if self.parameter_dict[roof_or_facades]["replacement_scenario"][
                    "replacement_frequency_in_years"] is not None:
                    kwargs["replacement_frequency_in_years"] = self.parameter_dict["replacement_scenario"][
                        "replacement_frequency_in_years"]

            # Run the simulation
            if efficiency_computation_method == "yearly":
                energy_harvested_yearly_list, nb_of_panels_installed_yearly_list = bipv_energy_harvesting_simulation_yearly_annual_irradiance(
                    pv_panel_obj_list=panel_list,
                    annual_solar_irradiance_value=annual_panel_irradiance_list,
                    iteration_duration_in_years=iteration_duration_in_years,
                    replacement_scenario=replacement_scenario, **kwargs)
            # The hourly method is not implemented yet
            elif efficiency_computation_method == "hourly":
                path_result_folder = os.path.join(path_simulation_folder, name_radiation_simulation_folder,
                                                  str(building_id))
                if roof_or_facades == "roof":
                    path_ill_file = os.path.join(path_result_folder, name_roof_ill_file)
                    path_sun_up_hours_file = os.path.join(path_result_folder, name_roof_sun_up_hours_file)
                elif roof_or_facades == "facades":
                    path_ill_file = os.path.join(path_result_folder, name_facades_ill_file)
                    path_sun_up_hours_file = os.path.join(path_result_folder, name_facades_sun_up_hours_file)

                roof_energy_harvested_yearly_list, roof_nb_of_panels_installed_yearly_list = bipv_energy_harvesting_simulation_hourly_annual_irradiance(
                    pv_panel_obj_list=self.roof_panel_list,
                    path_ill_file=path_ill_file,
                    path_sun_up_hours_file=path_sun_up_hours_file,
                    iteration_duration_in_years=iteration_duration_in_years,
                    replacement_scenario=replacement_scenario, **kwargs)
            else:
                raise ValueError("The efficiency computation method is not valid")

            # Post process and run LCA and DMFA results
            primary_energy_material_extraction_and_manufacturing_yearly_list, \
                primary_energy_transportation_yearly_list, primary_energy_recycling_yearly_list, \
                total_primary_energy_yearly_list, carbon_transportation_yearly_list, \
                carbon_material_extraction_and_manufacturing_yearly_list, \
                carbon_recycling_yearly_list, total_carbon_yearly_list, \
                dmfa_waste_yearly_lis = bipv_lca_dmfa_eol_computation(
                nb_of_panels_installed_yearly_list=nb_of_panels_installed_yearly_list,
                pv_tech_obj=pv_tech_obj)
            # Save the results in obj
            self.bipv_results_dict[roof_or_facades] = self.add_results_to_dict(
                bipv_reults_dict=self.bipv_results_dict[roof_or_facades],
                energy_harvested_yearly_list=energy_harvested_yearly_list,
                primary_energy_material_extraction_and_manufacturing_yearly_list=primary_energy_material_extraction_and_manufacturing_yearly_list,
                primary_energy_transportation_yearly_list=primary_energy_transportation_yearly_list,
                primary_energy_recycling_yearly_list=primary_energy_recycling_yearly_list,
                carbon_material_extraction_and_manufacturing_yearly_list=carbon_material_extraction_and_manufacturing_yearly_list,
                carbon_transportation_yearly_list=carbon_transportation_yearly_list,
                carbon_recycling_yearly_list=carbon_recycling_yearly_list,
                dmfa_waste_yearly_list=dmfa_waste_yearly_lis)

            # Update the duration in year of the simulation
            self.parameter_dict[roof_or_facades]["study_duration_in_years"] = self.parameter_dict["start_year"] - uc_last_year

        else:
            simulation_has_run = False

        return simulation_has_run

    @classmethod
    def sum_bipv_results_at_urban_scale(cls, solar_rad_and_bipv_obj_list):
        """
        Sum the results dictionary of the BIPV simulations at the urban scale
        :param solar_rad_and_bipv_simulation_list: list of SolarRadAndBipvSimulation objects
        :return: dict of the results
        """
        bipv_results_dict = deepcopy(empty_bipv_results_dict)
        for solar_rad_and_bipv_obj in solar_rad_and_bipv_obj_list:
            bipv_results_dict = sum_dicts(bipv_results_dict, solar_rad_and_bipv_obj.bipv_results_dict)
        return bipv_results_dict

    @staticmethod
    def add_results_to_dict(bipv_results_dict, energy_harvested_yearly_list,
                            primary_energy_material_extraction_and_manufacturing_yearly_list,
                            primary_energy_transportation_yearly_list,
                            primary_energy_recycling_yearly_list,
                            carbon_material_extraction_and_manufacturing_yearly_list,
                            carbon_transportation_yearly_list, carbon_recycling_yearly_list,
                            dmfa_waste_yearly_list):
        """
        Convert the results to a dict
        :param bipv_results_dict: dict of the results
        :param energy_harvested_yearly_list: list of the energy harvested yearly
        :param primary_energy_material_extraction_and_manufacturing_yearly_list: list of the primary energy used for the material extraction and manufacturing
        :param primary_energy_transportation_yearly_list: list of the primary energy used for the transportation
        :param primary_energy_recycling_yearly_list: list of the primary energy used for the recycling
        :param carbon_material_extraction_and_manufacturing_yearly_list: list of the carbon used for the material extraction and manufacturing
        :param carbon_transportation_yearly_list: list of the carbon used for the transportation
        :param carbon_recycling_yearly_list: list of the carbon used for the recycling
        :param dmfa_waste_yearly_list: list of the waste
        :return: dict of the results
        """

        # Energy harvested
        bipv_results_dict["energy_harvested"]["yearly"] += energy_harvested_yearly_list
        # LCA primary
        bipv_results_dict["lca_primary_energy"]["material_extraction_and_manufacturing"][
            "yearly"] += primary_energy_material_extraction_and_manufacturing_yearly_list
        bipv_results_dict["lca_primary_energy"]["transportation"][
            "yearly"] += primary_energy_transportation_yearly_list
        bipv_results_dict["lca_primary_energy"]["recycling"]["yearly"] += primary_energy_recycling_yearly_list
        bipv_results_dict["lca_primary_energy"]["total"]["yearly"] += [sum(i) for i in zip(
            primary_energy_transportation_yearly_list,
            primary_energy_material_extraction_and_manufacturing_yearly_list,
            primary_energy_recycling_yearly_list)]
        # LCA carbon footprint
        bipv_results_dict["lca_carbon_footprint"]["material_extraction_and_manufacturing"][
            "yearly"] += carbon_material_extraction_and_manufacturing_yearly_list
        bipv_results_dict["lca_carbon_footprint"]["transportation"][
            "yearly"] += carbon_transportation_yearly_list
        bipv_results_dict["lca_carbon_footprint"]["recycling"]["yearly"] += carbon_recycling_yearly_list
        bipv_results_dict["lca_carbon_footprint"]["total"]["yearly"] += [sum(i) for i in zip(
            carbon_transportation_yearly_list, carbon_material_extraction_and_manufacturing_yearly_list,
            carbon_recycling_yearly_list)]
        # DMFA
        bipv_results_dict["dmfa_waste"]["yearly"] += dmfa_waste_yearly_list
        # Compute cumulative and total values
        bipv_results_dict = compute_cumulative_and_total_value_bipv_result_dict(bipv_results_dict)

        return bipv_results_dict

    @classmethod
    def urban_canopy_make_bipv_results_scenario(cls, solar_rad_and_bipv_obj_list):
        """
        Sum the results dictionary of the BIPV simulations at the urban scale
        :param solar_rad_and_bipv_simulation_list: list of SolarRadAndBipvSimulation objects
        :return: dict of the results
        """
        bipv_results_dict_list = [result_dict for result_dict in
                                  solar_rad_and_bipv_obj_list.bipv_results_dict]
        starting_year_list = [solar_rad_and_bipv_obj.parameter_dict["start_year"] for solar_rad_and_bipv_obj
                              in solar_rad_and_bipv_obj_list]
        study_duration_list = [solar_rad_and_bipv_obj.parameter_dict["study_duration_in_years"] for
                               solar_rad_and_bipv_obj in solar_rad_and_bipv_obj_list]
        earliest_year, latest_year = cls.urban_canopy_scenarios_boundary_years(starting_year_list,
                                                                               study_duration_list)

        uc_bipv_results_dict = deepcopy(bipv_results_dict_list[0])
        starting_year_it = starting_year_list[0]  # Initialize the starting year
        for i, bipv_results_dict in enumerate(bipv_results_dict_list, start=1):
            starting_year_list = [starting_year_it, starting_year_list[i]]
            uc_bipv_results_dict = cls.urban_canopy_sum_bipv_results_dicts_with_different_years(
                dict_1=uc_bipv_results_dict, dict_2=bipv_results_dict, starting_year_list=starting_year_list,
                earliest_year=earliest_year, latest_year=latest_year)
            starting_year_it = earliest_year  # After the first iteration, the starting year is the earliest year

        new_solar_rad_and_bipv_obj = cls()
        new_solar_rad_and_bipv_obj.bipv_results_dict = uc_bipv_results_dict
        new_solar_rad_and_bipv_obj.parameter_dict["start_year"] = earliest_year
        new_solar_rad_and_bipv_obj.parameter_dict["study_duration_in_years"] = latest_year - earliest_year + 1

        return new_solar_rad_and_bipv_obj

    # def urban_canopy_concatenate_bipv_result_scenario(cls, solar_rad_and_bipv_obj_list):
    #     """
    #     Sum the results dictionary of the BIPV simulations at the urban scale
    #     :param solar_rad_and_bipv_simulation_list: list of SolarRadAndBipvSimulation objects
    #     :return: dict of the results
    #     """
    #     bipv_results_dict = deepcopy(empty_bipv_results_dict)
    #     for solar_rad_and_bipv_obj in solar_rad_and_bipv_obj_list:
    #         bipv_results_dict = sum_dicts(bipv_results_dict, solar_rad_and_bipv_obj.bipv_results_dict)
    #
    #     return bipv_results_dict

    def bipv_results_to_csv(self, path_simulation_folder, building_id_or_uc_scenario_name):
        """
        Save bipv simulation results in a csv file
        :param: path_simulation_folder: path to the simulation folder
        :param: building_id_or_uc_scenario_name: building id or urban canopy scenario name
        """
        path_result_folder = os.path.join(path_simulation_folder, name_radiation_simulation_folder,
                                          str(building_id_or_uc_scenario_name))
        # create the folder if it does not exist, especially for the urban canopy
        if not os.path.isdir(path_result_folder):
            os.makedirs(path_result_folder)
        path_csv_file = os.path.join(path_result_folder, name_results_file_csv)
        with open(path_csv_file, mode='w', newline='') as file:
            # flatten the dict to read and write the data easily
            flattened_dict = flatten_dict(self.bipv_results_dict)
            fieldnames = ["years"]
            for k in flattened_dict.keys():
                if not k.endswith("_total"):
                    fieldnames.append(k)

            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()

            for i in range(self.parameter_dict["study_duration_in_years"]):
                row_data = {f"{self.parameter_dict['start_year'] + i}"}
                for k, v in flattened_dict.items():
                    # do not include the total values
                    if not k.endswith("_total"):
                        row_data[k] = v[i]
                writer.writerow(row_data)

    # def results_to_figures(self):
    #     """
    #
    #     """

    @staticmethod
    def urban_canopy_sum_bipv_results_dicts_with_different_years(dict_1, dict_2, starting_year_list,
                                                                 earliest_year, latest_year):
        """
            Sum the values dictionnaries
            :param dict_1: dict of the results
            :param dict_2: dict of the results
            :param starting_year_list: list of the starting years of the simulations
            :param earliest_year: earliest year of the simulations
            :param latest_year: latest year of the simulations
            :return: dict of the results
        """

        result_dict = {}
        for key in dict_1:
            if isinstance(dict_1[key], dict):
                result_dict[key] = sum_dicts(dict_1[key], dict_2[key], starting_year_list, earliest_year,
                                             latest_year)
            elif isinstance(dict_1[key], list):
                list_1 = [0.0] * (latest_year - earliest_year + 1)
                list_1[
                starting_year_list[0] - earliest_year:starting_year_list[0] - earliest_year + len(
                    dict_1[key])] = \
                    dict_1[key]
                list_2 = [0.0] * (latest_year - earliest_year + 1)
                list_2[
                starting_year_list[1] - earliest_year:starting_year_list[1] - earliest_year + len(
                    dict_2[key])] = \
                    dict_2[key]
                result_dict[key] = [x + y for x, y in zip(list_1, list_2)]
            else:  # assuming ints or floats
                result_dict[key] = dict_1[key] + dict_2[key]

        return result_dict

    @staticmethod
    def urban_canopy_scenarios_boundary_years(starting_year_list, study_duration_list):
        """
        Find the earliest and latest years across all dictionaries
        :param starting_year_list: list of the starting years of the simulations
        :param study_duration_list: list of the study durations of the simulations
        """
        # Find the earliest and latest years across all dictionaries
        earliest_year = min(starting_year_list)
        latest_year = max(starting_year + study_duration - 1 for starting_year, study_duration in
                          zip(starting_year_list, study_duration_list))
        """ -1 because the first year is included """

        return earliest_year, latest_year


def compute_cumulative_and_total_value_bipv_result_dict(bipv_results_dict):
    """
    Sum the values dictionnaries
    """

    for key in bipv_results_dict:
        if isinstance(bipv_results_dict[key], dict):
            bipv_results_dict[key] = compute_cumulative_and_total_value_bipv_result_dict(
                bipv_results_dict[key])
        elif isinstance(bipv_results_dict[key], list) and key == "yearly":
            bipv_results_dict["cumulative"] = [sum(bipv_results_dict["yearly"][0:i]) for i in
                                               range(1, len(bipv_results_dict["yearly"]) + 1)]
            bipv_results_dict["total"] = bipv_results_dict["cumulative"][-1]

    return bipv_results_dict


def sum_dicts(*args):
    """
    Sum the values dictionnaries
    """
    if not args:
        return {}
    # Initialize with teh first dict
    result_dict = args[0].copy()

    for d in args[1:]:
        for key in d:
            if isinstance(d[key], dict):
                result_dict[key] = sum_dicts(result_dict[key], d[key])
            elif isinstance(d[key], list):
                result_dict[key] = [x + y for x, y in zip(result_dict[key], d[key])]
            else:  # assuming ints or floats
                result_dict[key] += d[key]

    return result_dict


def flatten_dict(d):
    """
    Flatten a nested dictionnary
    """
    result = {}
    for key, value in d.items():
        if isinstance(value, dict):
            nested = flatten_dict(value)
            for k, v in nested.items():
                result[f"{key}_{k}"] = v
        else:
            result[key] = value
    return result
