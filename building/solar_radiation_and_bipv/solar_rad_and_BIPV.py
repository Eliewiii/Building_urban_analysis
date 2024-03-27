"""
todo
"""

import os
import logging
import shutil
import csv

from copy import deepcopy
from datetime import datetime
from time import time

from honeybee_radiance.sensorgrid import SensorGrid
from ladybug_geometry.geometry3d.face import Face3D

from building.solar_radiation_and_bipv.utils_sensorgrid import generate_sensor_grid_for_hb_model
from building.solar_radiation_and_bipv.utils_solar_radiation import \
    run_hb_model_annual_irradiance_simulation, move_annual_irr_hb_radiance_results, \
    get_hourly_irradiance_table
from building.solar_radiation_and_bipv.utils_bipv import init_bipv_on_sensor_grid, \
    simulate_bipv_yearly_energy_harvesting, compute_lca_and_cost_for_gtg, \
    compute_lca_cost_and_dmfa_for_recycling, \
    compute_lca_and_cost_for_transportation, \
    compute_lca_and_cost_for_inverter, compute_lca_and_cost_for_maintenance

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
                             "replacement_frequency_in_years": None},
    "efficiency_computation_method": {"id": None,
                                      "parameter": None},
    "inverter": {"technology": None,
                 "sizing_ratio": None,
                 "capacity": None,
                 "sub_capacities": None}
}

empty_parameter_dict = {
    "roof": deepcopy(empty_sub_parameter_dict),
    "facades": deepcopy(empty_sub_parameter_dict)
}
empty_sub_bipv_results_dict = {
    "energy_harvested": {"yearly": [], "cumulative": [], "total": 0.0},
    "primary_energy": {
        "gate_to_gate": {"yearly": [], "cumulative": [], "total": 0.0},
        "transportation": {
            "gate_to_gate": {"yearly": [], "cumulative": [], "total": 0.0},
            "recycling": {"yearly": [], "cumulative": [], "total": 0.0},
            "total": {"yearly": [], "cumulative": [], "total": 0.0}
        },
        "maintenance": {"yearly": [], "cumulative": [], "total": 0.0},
        "inverter": {"yearly": [], "cumulative": [], "total": 0.0},
        "recycling": {"yearly": [], "cumulative": [], "total": 0.0},
        "total": {"yearly": [], "cumulative": [], "total": 0.0}
    },
    "ghg": {
        "gate_to_gate": {"yearly": [], "cumulative": [], "total": 0.0},
        "transportation": {
            "gate_to_gate": {"yearly": [], "cumulative": [], "total": 0.0},
            "recycling": {"yearly": [], "cumulative": [], "total": 0.0},
            "total": {"yearly": [], "cumulative": [], "total": 0.0}
        },
        "maintenance": {"yearly": [], "cumulative": [], "total": 0.0},
        "inverter": {"yearly": [], "cumulative": [], "total": 0.0},
        "recycling": {"yearly": [], "cumulative": [], "total": 0.0},
        "total": {"yearly": [], "cumulative": [], "total": 0.0}
    },
    "cost": {
        "investment": {
            "gate_to_gate": {"yearly": [], "cumulative": [], "total": 0.0},
            "transportation": {
                "gate_to_gate": {"yearly": [], "cumulative": [], "total": 0.0},
                "recycling": {"yearly": [], "cumulative": [], "total": 0.0},
                "total": {"yearly": [], "cumulative": [], "total": 0.0}
            },
            "maintenance": {"yearly": [], "cumulative": [], "total": 0.0},
            "inverter": {"yearly": [], "cumulative": [], "total": 0.0},
            "recycling": {"yearly": [], "cumulative": [], "total": 0.0},
            "total": {"yearly": [], "cumulative": [], "total": 0.0}
        },
        "revenue": {
            "substituted_construction_material": {"yearly": [], "cumulative": [], "total": 0.0},
            "material_recovery": {"yearly": [], "cumulative": [], "total": 0.0},
            "total": {"yearly": [], "cumulative": [], "total": 0.0}

        },
        "net_profit": {"yearly": [], "cumulative": [], "total": 0.0}
    },
    "dmfa": {"yearly": [], "cumulative": [], "total": 0.0}
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
    todo @Elie
    """

    def __init__(self, building_id):

        # Building id
        self.building_id = building_id
        # Run the simulations for roof and/or facades
        self.on_roof = False
        self.on_facades = False
        # SensorGrid objects
        self.roof_sensorgrid_dict = None
        self.facades_sensorgrid_dict = None
        # Panel objects
        self.roof_panel_list = None
        self.facades_panel_list = None
        # Solar irradiance on each of the face of the mesh
        self.roof_annual_panel_irradiance_list = None
        self.facades_annual_panel_irradiance_list = None
        self.irradiance_simulation_duration = {"roof": None, "facades": None}
        # bipv results
        self.bipv_results_dict = None
        self.init_bipv_results_dict()
        # parameters
        self.parameter_dict = deepcopy(empty_parameter_dict)
        # flags
        self.roof_irradiance_run = False
        self.facades_irradiance_run = False
        self.roof_bipv_sim_run = False
        self.facades_bipv_sim_run = False

    def set_mesh_parameters(self, roof_or_facades, on_roof_or_facades, grid_size_x=1, grid_size_y=1,
                            offset_dist=0.1):
        """
        Set the mesh parameters for the simulation
        :param roof_or_facades: str: roof or facades
        :param on_roof_or_facades: bool: default=True, whether to run the simulation on the roof or the facades
        :param grid_size_x: Number for the size of the test grid
        :param grid_size_y: Number for the size of the test grid
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
            self.parameter_dict[roof_or_facades]["grid_x"] = grid_size_x
            self.parameter_dict[roof_or_facades]["grid_y"] = grid_size_y
            self.parameter_dict[roof_or_facades]["offset"] = offset_dist

    def init_bipv_simulation(self):
        """

        """
        self.init_bipv_results_dict()
        self.roof_panel_list = None
        self.facades_panel_list = None
        for roof_or_facade in ["roof", "facades"]:
            self.parameter_dict[roof_or_facade]["panel_technology"] = None
            self.parameter_dict[roof_or_facade]["minimum_panel_eroi"] = None
            self.parameter_dict[roof_or_facade]["start_year"] = None
            self.parameter_dict[roof_or_facade]["study_duration_in_years"] = None
            self.parameter_dict[roof_or_facade]["replacement_scenario"] = {"id": None,
                                                                           "replacement_frequency_in_years": None}
            self.parameter_dict[roof_or_facade]["efficiency_computation_method"] = {"id": None,
                                                                                    "parameter": None}

    def set_bipv_parameters(self, roof_or_facades, pv_tech_obj, minimum_panel_eroi, start_year,
                            replacement_scenario,
                            efficiency_computation_method, **kwargs):
        """
        Set the BIPV parameters for the simulation
        :param roof_or_facades: str: roof or facades
        :param pv_tech_obj: PVPanelTechnology object
        :param minimum_panel_eroi: float : the minimum EROI of the panels
        :param start_year: int : the start year of the study
        :param replacement_scenario: str : the replacement scenario of the panels
        :param efficiency_computation_method: str : the method to compute the efficiency of the panels
        :param kwargs: dict : other parameters
        todo: add the additional parameters
        """
        self.parameter_dict[roof_or_facades]["panel_technology"] = pv_tech_obj
        self.parameter_dict[roof_or_facades]["minimum_panel_eroi"] = minimum_panel_eroi
        self.parameter_dict[roof_or_facades]["replacement_scenario"]["id"] = replacement_scenario
        self.parameter_dict[roof_or_facades]["efficiency_computation_method"][
            "id"] = efficiency_computation_method
        self.parameter_dict[roof_or_facades]["start_year"] = start_year
        self.parameter_dict[roof_or_facades]["study_duration_in_years"] = 0
        # todo: add the additional paameters
        if "replacement_frequency_in_years" in kwargs.keys():
            self.parameter_dict[roof_or_facades]["replacement_scenario"][
                "replacement_frequency_in_years"] = kwargs["replacement_frequency_in_years"]

    def init_bipv_results_dict(self):
        """
        Initialize the BIPV results
        """
        self.bipv_results_dict = deepcopy(empty_bipv_results_dict)

    def init_bipv_results_sub_dict(self, roof_or_facades):
        """
        Initialize the BIPV results
        """
        if roof_or_facades == "roof":
            self.bipv_results_dict["roof"] = deepcopy(empty_sub_bipv_results_dict)
        else:
            self.bipv_results_dict["facades"] = deepcopy(empty_sub_bipv_results_dict)

    def to_json_dict(self):
        """
        Return the dictionary representation of that object to export it to json
        """
        json_dict = {
            "parameters": deepcopy(self.parameter_dict),
            "roof_sensorgrid": self.roof_sensorgrid_dict,
            "facades_sensorgrid": self.facades_sensorgrid_dict,
            "roof_annual_panel_irradiance_list": self.roof_annual_panel_irradiance_list,
            "facades_annual_panel_irradiance_list": self.facades_annual_panel_irradiance_list,
            "irradiance_simulation_duration": self.irradiance_simulation_duration,
            "roof_panel_mesh_index_list": None,
            "facades_panel_mesh_index_list": None,
            "roof_result_dict": self.bipv_results_dict["roof"],
            "facades_result_dict": self.bipv_results_dict["facades"],
            "total_result_dict": self.bipv_results_dict["total"]
        }
        # Add the mesh index list to plot on GH the location of the kept panels
        if self.roof_panel_list is not None:
            json_dict["roof_panel_mesh_index_list"] = [panel.index for panel in self.roof_panel_list]
        if self.facades_panel_list is not None:
            json_dict["facades_panel_mesh_index_list"] = [panel.index for panel in self.facades_panel_list]
        # Adjust the parameter dict to make it json serializable
        json_dict["parameters"]["roof"]["panel_technology"] = json_dict["parameters"]["roof"]["panel_technology"].identifier if json_dict["parameters"]["roof"]["panel_technology"] is not None else None
        json_dict["parameters"]["roof"]["inverter"]["technology"] = json_dict["parameters"]["roof"]["inverter"]["technology"].identifier if json_dict["parameters"]["roof"]["inverter"]["technology"] is not None else None

        json_dict["parameters"]["facades"]["panel_technology"] = json_dict["parameters"]["facades"]["panel_technology"].identifier if json_dict["parameters"]["facades"]["panel_technology"] is not None else None
        json_dict["parameters"]["facades"]["inverter"]["technology"] = json_dict["parameters"]["facades"]["inverter"]["technology"].identifier if json_dict["parameters"]["facades"]["inverter"]["technology"] is not None else None


        return json_dict

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
        # if overwrite, delete the existing sensor grid and the solar irradiance results
        if not bipv_on_roof and overwrite:
            self.roof_sensorgrid_dict = None
            self.roof_annual_panel_irradiance_list = None
        if not bipv_on_facades and overwrite:
            self.facades_sensorgrid_dict = None
            self.facades_annual_panel_irradiance_list = None

        if not bipv_on_roof and not bipv_on_facades and not overwrite:
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
                                     grid_size_x=roof_grid_size_x, grid_size_y=roof_grid_size_y,
                                     offset_dist=offset_dist)
        if bipv_on_facades and (self.facades_sensorgrid_dict is None or overwrite):
            self.facades_sensorgrid_dict = generate_sensor_grid_for_hb_model(hb_model_obj,
                                                                             facades_grid_size_x,
                                                                             facades_grid_size_y, offset_dist,
                                                                             "facades")
            self.set_mesh_parameters(roof_or_facades="facades", on_roof_or_facades=bipv_on_facades,
                                     grid_size_x=facades_grid_size_x,
                                     grid_size_y=facades_grid_size_y,
                                     offset_dist=offset_dist)

    def run_annual_solar_irradiance_simulation(self, path_simulation_folder, hb_model_obj,
                                               context_shading_hb_shade_list, path_weather_file,
                                               overwrite=False,
                                               north_angle=0, silent=False):
        """
        Run the annual solar radiation simulation for the roof and/or the facades
        :param path_simulation_folder: str : the path to the simulation folder
        :param hb_model_obj: Honeybee Model object
        :param context_shading_hb_shade_list: list of Honeybee Shades objects for the context shading
        :param path_weather_file: str : the path to the epw file
        :param overwrite: bool : whether to overwrite the existing results
        :param north_angle: float : the north angle of the building
        :param silent: bool : whether to print the logs or not
        """
        path_folder_run_radiation_temp = os.path.join(path_simulation_folder, name_temporary_files_folder,
                                                      str(self.building_id))
        path_result_folder = os.path.join(path_simulation_folder, name_radiation_simulation_folder,
                                          str(self.building_id))

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
                duration = time()
                self.roof_annual_panel_irradiance_list = run_hb_model_annual_irradiance_simulation(
                    hb_model_obj=hb_model_copy_roof,
                    path_folder_run=path_folder_run_radiation_temp_roof,
                    path_weather_file=path_weather_file,
                    timestep=1,
                    visible=False, north=north_angle,
                    radiance_parameters='-ab 2 -ad 5000 -lw 2e-05',
                    silent=silent)
                duration = time() - duration
                self.irradiance_simulation_duration["roof"] = duration
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
                duration = time()
                self.facades_annual_panel_irradiance_list = run_hb_model_annual_irradiance_simulation(
                    hb_model_obj=hb_model_copy_facades,
                    path_folder_run=path_folder_run_radiation_temp_facades,
                    path_weather_file=path_weather_file,
                    timestep=1,
                    visible=False, north=north_angle,
                    radiance_parameters='-ab 2 -ad 5000 -lw 2e-05',
                    silent=silent)
                duration = time() - duration
                self.irradiance_simulation_duration["facades"] = duration
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

    def run_bipv_panel_simulation(self, path_simulation_folder, roof_pv_tech_obj,
                                  facades_pv_tech_obj,
                                  roof_inverter_tech_obj, facades_inverter_tech_obj, roof_inverter_sizing_ratio,
                                  facades_inverter_sizing_ratio, roof_transport_obj, facades_transport_obj,
                                  uc_end_year, uc_start_year, uc_current_year,
                                  efficiency_computation_method="yearly",
                                  minimum_panel_eroi=1.2,
                                  replacement_scenario="replace_failed_panels_every_X_years",
                                  continue_simulation=False, **kwargs):
        """

        """

        run_bipv_on_roof = self.run_bipv_panel_simulation_on_roof_or_facades(roof_or_facades="roof",
                                                                             on_roof_or_facades=self.on_roof,
                                                                             sensorgrid_dict=self.roof_sensorgrid_dict,
                                                                             annual_panel_irradiance_list=self.roof_annual_panel_irradiance_list,
                                                                             panel_list=self.roof_panel_list,
                                                                             path_simulation_folder=path_simulation_folder,
                                                                             pv_tech_obj=roof_pv_tech_obj,
                                                                             inverter_tech_obj=roof_inverter_tech_obj,
                                                                             inverter_sizing_ratio=roof_inverter_sizing_ratio,
                                                                             transport_obj=roof_transport_obj,
                                                                             uc_end_year=uc_end_year,
                                                                             uc_start_year=uc_start_year,
                                                                             uc_current_year=uc_current_year,
                                                                             efficiency_computation_method=efficiency_computation_method,
                                                                             minimum_panel_eroi=minimum_panel_eroi,
                                                                             replacement_scenario=replacement_scenario,
                                                                             continue_simulation=continue_simulation,
                                                                             **kwargs)

        run_bipv_on_facades = self.run_bipv_panel_simulation_on_roof_or_facades(roof_or_facades="facades",
                                                                                on_roof_or_facades=self.on_facades,
                                                                                sensorgrid_dict=self.facades_sensorgrid_dict,
                                                                                annual_panel_irradiance_list=self.facades_annual_panel_irradiance_list,
                                                                                panel_list=self.facades_panel_list,
                                                                                path_simulation_folder=path_simulation_folder,
                                                                                pv_tech_obj=facades_pv_tech_obj,
                                                                                inverter_tech_obj=facades_inverter_tech_obj,
                                                                                inverter_sizing_ratio=facades_inverter_sizing_ratio,
                                                                                transport_obj=facades_transport_obj,
                                                                                uc_end_year=uc_end_year,
                                                                                uc_start_year=uc_start_year,
                                                                                uc_current_year=uc_current_year,
                                                                                efficiency_computation_method=efficiency_computation_method,
                                                                                minimum_panel_eroi=minimum_panel_eroi,
                                                                                replacement_scenario=replacement_scenario,
                                                                                continue_simulation=continue_simulation,
                                                                                **kwargs)

        # Total results
        if run_bipv_on_roof and run_bipv_on_facades:
            earliest_year = min(
                [self.parameter_dict["roof"]["start_year"], self.parameter_dict["facades"]["start_year"]])
            latest_year = max(
                [self.parameter_dict["roof"]["start_year"] + self.parameter_dict["roof"][
                    "study_duration_in_years"],
                 self.parameter_dict["facades"]["start_year"] + self.parameter_dict["facades"][
                     "study_duration_in_years"]])

            self.bipv_results_dict["total"] = sum_bipv_results_dicts_with_different_years(
                dict_1=self.bipv_results_dict["roof"], dict_2=self.bipv_results_dict["facades"],
                start_year_1=self.parameter_dict["roof"]["start_year"],
                start_year_2=self.parameter_dict["facades"]["start_year"], earliest_year=earliest_year,
                latest_year=latest_year)

        elif run_bipv_on_roof:
            self.bipv_results_dict["total"] = self.bipv_results_dict["roof"]
        elif run_bipv_on_facades:
            self.bipv_results_dict["total"] = self.bipv_results_dict["facades"]

    def run_bipv_panel_simulation_on_roof_or_facades(self, roof_or_facades, on_roof_or_facades,
                                                     sensorgrid_dict,
                                                     annual_panel_irradiance_list, panel_list,
                                                     path_simulation_folder,
                                                     pv_tech_obj, inverter_tech_obj,
                                                     inverter_sizing_ratio,
                                                     transport_obj,
                                                     uc_end_year, uc_start_year,
                                                     uc_current_year, efficiency_computation_method,
                                                     minimum_panel_eroi,
                                                     replacement_scenario, continue_simulation=False,
                                                     **kwargs):
        """

        """
        # Condition to run the simulation
        if on_roof_or_facades and sensorgrid_dict is not None and annual_panel_irradiance_list is not None:
            simulation_has_run = True  # run flag

            # Init the BIPV panels if necessary
            if not continue_simulation or panel_list is None:
                """ If there is no panel list, we init the panels, but if we want to continue the simulation and there 
                are already panels, we do not init them again """

                self.init_bipv_results_sub_dict(roof_or_facades=roof_or_facades)

                self.set_bipv_parameters(roof_or_facades=roof_or_facades, pv_tech_obj=pv_tech_obj,
                                         efficiency_computation_method=efficiency_computation_method,
                                         minimum_panel_eroi=minimum_panel_eroi,
                                         start_year=uc_current_year,
                                         replacement_scenario=replacement_scenario, **kwargs)
                # todo: add the additional transport and inverter parameters

                panel_list = init_bipv_on_sensor_grid(sensor_grid=SensorGrid.from_dict(sensorgrid_dict),
                                                      pv_technology_obj=pv_tech_obj,
                                                      bipv_transportation_obj=transport_obj,
                                                      annual_panel_irradiance_list=annual_panel_irradiance_list,
                                                      minimum_panel_eroi=minimum_panel_eroi)

                # Size the inverters capacity
                peak_power = pv_tech_obj.max_power_output * len(panel_list)
                total_capacity, sub_capacities_list = inverter_tech_obj.size_inverter(peak_power=peak_power,
                                                                                      sizing_ratio=inverter_sizing_ratio)
                self.parameter_dict[roof_or_facades]["inverter"]["technology"] = inverter_tech_obj
                self.parameter_dict[roof_or_facades]["inverter"]["sizing_ratio"] = inverter_sizing_ratio
                self.parameter_dict[roof_or_facades]["inverter"]["capacity"] = total_capacity
                self.parameter_dict[roof_or_facades]["inverter"]["sub_capacities"] = sub_capacities_list


            # If the simulation continue we keep the existing panels and the parameters
            else:
                simulation_continued = True

                # Check if the simulation has already been run for the requested years, if so, we do not run it again
                if self.parameter_dict[roof_or_facades]["start_year"] + self.parameter_dict[roof_or_facades][
                    "study_duration_in_years"] >= uc_end_year:
                    user_logger.info(
                        f"The bipv simulation was already run for building {self.building_id} during the input time"
                        f" period, the simulation was not run for this building")

                    simulation_has_run = False  # run flag
                    return simulation_has_run

                    # Update the panel technology,
                """ The new panel that will be installed will have the new technology, it will affect their efficiency 
                and the LCA and DMFA results. It will not affect the existing panels as the computation of LCA and DMFA
                is done at the moment of the installation of the panels and the panel know which panel technology they
                belong to."""
                if kwargs["update_panel_technology"]:
                    self.parameter_dict[roof_or_facades]["panel_technology"] = pv_tech_obj
                else:
                    pv_tech_obj = self.parameter_dict[roof_or_facades]["panel_technology"]
                # Keep all the other parameters
                efficiency_computation_method = \
                    self.parameter_dict[roof_or_facades]["efficiency_computation_method"][
                        "id"]  # todo add the parameters if the efficiency computation method id needed
                replacement_scenario = self.parameter_dict[roof_or_facades]["replacement_scenario"]["id"]
                # todo with the kwarg as well and put it ion a function eventually
                if self.parameter_dict[roof_or_facades]["replacement_scenario"][
                    "replacement_frequency_in_years"] is not None:
                    kwargs["replacement_frequency_in_years"] = \
                        self.parameter_dict[roof_or_facades]["replacement_scenario"][
                            "replacement_frequency_in_years"]

            # Run the simulation
            path_result_folder = os.path.join(path_simulation_folder, name_radiation_simulation_folder,
                                              str(self.building_id))
            if roof_or_facades == "roof":
                path_ill_file = os.path.join(path_result_folder, name_roof_ill_file)
                path_sun_up_hours_file = os.path.join(path_result_folder, name_roof_sun_up_hours_file)
            else:
                path_ill_file = os.path.join(path_result_folder, name_facades_ill_file)
                path_sun_up_hours_file = os.path.join(path_result_folder, name_facades_sun_up_hours_file)

            # Get the hourly irradiance table
            hourly_irradiance_table = get_hourly_irradiance_table(path_ill_file)

            energy_harvested_yearly_list, nb_of_panels_installed_yearly_list = simulate_bipv_yearly_energy_harvesting(
                pv_panel_obj_list=panel_list,
                hourly_solar_irradiance_table=hourly_irradiance_table,
                inverter_capacity=self.parameter_dict[roof_or_facades]["inverter"]["capacity"],
                start_year=self.parameter_dict[roof_or_facades]["start_year"],
                current_study_duration_in_years=self.parameter_dict[roof_or_facades][
                    "study_duration_in_years"],
                uc_start_year=uc_start_year, uc_end_year=uc_end_year,
                replacement_scenario=replacement_scenario,
                pv_tech_obj=pv_tech_obj, **kwargs)

            # LCA and economic for the gate to gate processes for the panels except transportation
            gtg_result_dict = compute_lca_and_cost_for_gtg(
                nb_of_panels_installed_yearly_list=nb_of_panels_installed_yearly_list,
                pv_tech_obj=pv_tech_obj,
                roof_or_facades=roof_or_facades)
            # LCA and economic for transportation
            transport_result_dict = compute_lca_and_cost_for_transportation(
                nb_of_panels_installed_yearly_list=nb_of_panels_installed_yearly_list,
                pv_tech_obj=pv_tech_obj,
                transportation_obj=transport_obj)
            # LCA and economic for maintenance
            maintenance_result_dict = compute_lca_and_cost_for_maintenance(
                panel_list=panel_list,
                start_year=self.parameter_dict[roof_or_facades]["start_year"],
                current_study_duration_in_years=self.parameter_dict[roof_or_facades][
                    "study_duration_in_years"],
                uc_end_year=uc_end_year)
            # LCA and economic for recycling
            recycling_result_dict = compute_lca_cost_and_dmfa_for_recycling(
                nb_of_panels_installed_yearly_list=nb_of_panels_installed_yearly_list,
                pv_tech_obj=pv_tech_obj)
            # LCA and economic for the inverter
            inverter_result_dict = compute_lca_and_cost_for_inverter(
                inverter_obj=self.parameter_dict[roof_or_facades]["inverter"]["technology"],
                inverter_sub_capacities=self.parameter_dict[roof_or_facades]["inverter"]["sub_capacities"],
                start_year=self.parameter_dict[roof_or_facades]["start_year"],
                current_study_duration_in_years=self.parameter_dict[roof_or_facades][
                    "study_duration_in_years"],
                uc_end_year=uc_end_year)
            # Add results to the global results dictionary
            self.bipv_results_dict[roof_or_facades] = self.add_results_to_global_results_dict(
                bipv_results_dict=self.bipv_results_dict[roof_or_facades],
                energy_harvested_yearly_list=energy_harvested_yearly_list,
                gtg_result_dict=gtg_result_dict,
                transport_result_dict=transport_result_dict,
                maintenance_result_dict=maintenance_result_dict,
                recycling_result_dict=recycling_result_dict,
                inverter_result_dict=inverter_result_dict)

            # Update the duration in year of the simulation
            self.parameter_dict[roof_or_facades]["study_duration_in_years"] = uc_end_year - \
                                                                              self.parameter_dict[
                                                                                  roof_or_facades][
                                                                                  "start_year"]
            # Update the panel lists
            if roof_or_facades == "roof":
                self.roof_panel_list = panel_list
            else:
                self.facades_panel_list = panel_list

        else:
            simulation_has_run = False

        return simulation_has_run

    @staticmethod
    def add_results_to_global_results_dict(bipv_results_dict, energy_harvested_yearly_list, gtg_result_dict,
                                           transport_result_dict, maintenance_result_dict,
                                           recycling_result_dict,
                                           inverter_result_dict):
        """
        Convert the results to a dict
        :param bipv_results_dict: dict of the results
        :param energy_harvested_yearly_list: list of the results
        :param gtg_result_dict: dict of the results
        :param transport_result_dict: dict of the results
        :param maintenance_result_dict: dict of the results
        :param recycling_result_dict: dict of the results
        :param inverter_result_dict: dict of the results
        :return: dict of the results
        """

        # Energy harvested
        bipv_results_dict["energy_harvested"]["yearly"] += energy_harvested_yearly_list
        # LCA Primary energy
        bipv_results_dict["primary_energy"]["gate_to_gate"]["yearly"] += gtg_result_dict["primary_energy"]
        bipv_results_dict["primary_energy"]["transportation"]["gate_to_gate"]["yearly"] += \
            transport_result_dict[
                "primary_energy"]["gtg"]
        bipv_results_dict["primary_energy"]["transportation"]["recycling"]["yearly"] += transport_result_dict[
            "primary_energy"]["recycling"]
        bipv_results_dict["primary_energy"]["transportation"]["total"]["yearly"] += [sum(i) for i in zip(
            transport_result_dict["primary_energy"]["gtg"],
            transport_result_dict["primary_energy"]["recycling"])]
        bipv_results_dict["primary_energy"]["maintenance"]["yearly"] += maintenance_result_dict[
            "primary_energy"]
        bipv_results_dict["primary_energy"]["inverter"]["yearly"] += inverter_result_dict["primary_energy"]
        bipv_results_dict["primary_energy"]["recycling"]["yearly"] += recycling_result_dict["primary_energy"]
        bipv_results_dict["primary_energy"]["total"]["yearly"] += [sum(i) for i in zip(
            gtg_result_dict["primary_energy"], transport_result_dict["primary_energy"]["gtg"],
            transport_result_dict["primary_energy"]["recycling"], maintenance_result_dict["primary_energy"],
            inverter_result_dict["primary_energy"], recycling_result_dict["primary_energy"])]
        # LCA greenhouse gas emissions (ghg)
        bipv_results_dict["ghg"]["gate_to_gate"]["yearly"] += gtg_result_dict["ghg"]
        bipv_results_dict["ghg"]["transportation"]["gate_to_gate"]["yearly"] += transport_result_dict["ghg"][
            "gtg"]
        bipv_results_dict["ghg"]["transportation"]["recycling"]["yearly"] += transport_result_dict["ghg"][
            "recycling"]
        bipv_results_dict["ghg"]["transportation"]["total"]["yearly"] += [sum(i) for i in zip(
            transport_result_dict["ghg"]["gtg"], transport_result_dict["ghg"]["recycling"])]
        bipv_results_dict["ghg"]["maintenance"]["yearly"] += maintenance_result_dict["ghg"]
        bipv_results_dict["ghg"]["inverter"]["yearly"] += inverter_result_dict["ghg"]
        bipv_results_dict["ghg"]["recycling"]["yearly"] += recycling_result_dict["ghg"]
        bipv_results_dict["ghg"]["total"]["yearly"] += [sum(i) for i in zip(
            gtg_result_dict["ghg"], transport_result_dict["ghg"]["gtg"],
            transport_result_dict["ghg"]["recycling"],
            maintenance_result_dict["ghg"], inverter_result_dict["ghg"], recycling_result_dict["ghg"])]
        # DMFA
        bipv_results_dict["dmfa"]["yearly"] += recycling_result_dict["dmfa"]
        # Economical investment
        bipv_results_dict["cost"]["investment"]["gate_to_gate"]["yearly"] += gtg_result_dict["cost"][
            "investment"]
        bipv_results_dict["cost"]["investment"]["transportation"]["gate_to_gate"]["yearly"] += \
            transport_result_dict[
                "cost"]["gtg"]
        bipv_results_dict["cost"]["investment"]["transportation"]["recycling"]["yearly"] += \
            transport_result_dict[
                "cost"]["recycling"]
        bipv_results_dict["cost"]["investment"]["transportation"]["total"]["yearly"] += [sum(i) for i in zip(
            transport_result_dict["cost"]["gtg"],
            transport_result_dict["cost"]["recycling"])]
        bipv_results_dict["cost"]["investment"]["maintenance"]["yearly"] += maintenance_result_dict["cost"]
        bipv_results_dict["cost"]["investment"]["inverter"]["yearly"] += inverter_result_dict["cost"]
        bipv_results_dict["cost"]["investment"]["recycling"]["yearly"] += recycling_result_dict["cost"][
            "investment"]
        bipv_results_dict["cost"]["investment"]["total"]["yearly"] += [sum(i) for i in zip(
            gtg_result_dict["cost"]["investment"], transport_result_dict["cost"]["gtg"],
            transport_result_dict["cost"]["recycling"],
            maintenance_result_dict["cost"],
            inverter_result_dict["cost"], recycling_result_dict["cost"]["investment"])]
        # Economical revenue
        bipv_results_dict["cost"]["revenue"]["substituted_construction_material"]["yearly"] += \
            gtg_result_dict["cost"]["revenue"]["substituted_construction_material"]
        bipv_results_dict["cost"]["revenue"]["material_recovery"]["yearly"] += \
            recycling_result_dict["cost"]["revenue"]["material_recovery"]
        bipv_results_dict["cost"]["revenue"]["total"]["yearly"] += [sum(i) for i in zip(
            gtg_result_dict["cost"]["revenue"]["substituted_construction_material"],
            recycling_result_dict["cost"]["revenue"]["material_recovery"])]
        # Economical net cost
        bipv_results_dict["cost"]["net_profit"]["yearly"] = [investment - revenue for [investment, revenue] in
                                                             zip(
                                                                 bipv_results_dict["cost"]["investment"][
                                                                     "total"]["yearly"],
                                                                 bipv_results_dict["cost"]["revenue"]["total"][
                                                                     "yearly"])]

        # Compute cumulative and total values
        bipv_results_dict = compute_cumulative_and_total_value_bipv_result_dict(bipv_results_dict)
        # todo: check it works for the new results

        return bipv_results_dict

    def write_building_bipv_results_to_csv(self, path_radiation_and_bipv_result_folder):
        """
        Write the BIPV results to a csv file
        :param path_radiation_and_bipv_result_folder: path to the simulation folder
        """
        # Find the earliest and latest years across all dictionaries
        earliest_year = min(
            [self.parameter_dict["roof"]["start_year"], self.parameter_dict["facades"]["start_year"]])
        latest_year = max(
            [self.parameter_dict["roof"]["start_year"] + self.parameter_dict["roof"][
                "study_duration_in_years"],
             self.parameter_dict["facades"]["start_year"] + self.parameter_dict["facades"][
                 "study_duration_in_years"]])
        # adjust the dictionaries to have the same size
        result_dict_adjusted = deepcopy(self.bipv_results_dict)
        # Sum with an empty dict and force the proper boundaries for the years
        result_dict_adjusted["roof"] = sum_bipv_results_dicts_with_different_years(
            dict_1=empty_sub_bipv_results_dict,
            dict_2=result_dict_adjusted["roof"],
            start_year_1=earliest_year,
            start_year_2=self.parameter_dict["roof"]["start_year"],
            earliest_year=earliest_year,
            latest_year=latest_year)
        # sum the results for the facades
        result_dict_adjusted["facades"] = sum_bipv_results_dicts_with_different_years(
            dict_1=empty_sub_bipv_results_dict,
            dict_2=result_dict_adjusted["facades"],
            start_year_1=earliest_year,
            start_year_2=self.parameter_dict["facades"]["start_year"],
            earliest_year=earliest_year,
            latest_year=latest_year)

        # empty dict with proper size
        bipv_results_to_csv(path_radiation_and_bipv_result_folder=path_radiation_and_bipv_result_folder,
                            building_id_or_uc_scenario_name=self.building_id,
                            bipv_results_dict=result_dict_adjusted, start_year=earliest_year,
                            study_duration_in_years=latest_year - earliest_year)

    def get_selected_panel_lb_face3d(self):
        """
        Get the selected panel lb_face3d
        :return panel_lb_face_list: list of lb_face3d
        """
        panel_lb_face_list = []
        if self.roof_panel_list is not None and self.roof_panel_list != []:
            roof_sensorgrid = SensorGrid.from_dict(self.roof_sensorgrid_dict)
            panel_lb_face_list += [
                from_sensorgrid_face_index_to_lb_face3d(sensorgrid_face_index=panel.id, sensorgrid=roof_sensorgrid) for
                panel in self.roof_panel_list]
        if self.facades_panel_list is not None and self.facades_panel_list != []:
            facades_sensorgrid = SensorGrid.from_dict(self.facades_sensorgrid_dict)
            panel_lb_face_list += [
                from_sensorgrid_face_index_to_lb_face3d(sensorgrid_face_index=panel.id, sensorgrid=facades_sensorgrid)
                for panel in self.facades_panel_list]

        return panel_lb_face_list


def bipv_results_to_csv(path_radiation_and_bipv_result_folder, building_id_or_uc_scenario_name, bipv_results_dict,
                        start_year,
                        study_duration_in_years):
    """
    Save bipv simulation results in a csv file
    :param: path_simulation_folder: path to the simulation folder
    :param: building_id_or_uc_scenario_name: building id or urban canopy scenario name
    """
    path_result_folder = os.path.join(path_radiation_and_bipv_result_folder, str(building_id_or_uc_scenario_name))
    # create the folder if it does not exist, especially for the urban canopy
    if not os.path.isdir(path_result_folder):
        os.makedirs(path_result_folder)
    path_csv_file = os.path.join(path_result_folder,
                                 building_id_or_uc_scenario_name + "_" + name_results_file_csv)
    with open(path_csv_file, mode='w', newline='') as file:
        # flatten the dict to read and write the data easily
        flattened_dict = flatten_dict(bipv_results_dict)
        fieldnames = ["years"]
        for k in flattened_dict.keys():
            if not k.endswith("_total"):
                fieldnames.append(k)

        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

        for i in range(study_duration_in_years):
            row_data = {"years": f"{start_year + i}"}
            for k, v in flattened_dict.items():
                # do not include the total values
                if not k.endswith("_total"):
                    row_data[k] = v[i]
            writer.writerow(row_data)


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


def sum_bipv_results_dicts_with_different_years(dict_1, dict_2, start_year_1, start_year_2,
                                                earliest_year, latest_year):
    """
        Sum the values dictionnaries
        :param dict_1: dict of the results
        :param dict_2: dict of the results
        :param start_year_1: starting year of the first simulation
        :param start_year_2: starting year of the second simulation
        :param earliest_year: the earliest year of the simulations
        :param latest_year: latest year of the simulations
        :return: dict of the results
    """

    result_dict = {}
    for key in dict_1:
        if isinstance(dict_1[key], dict):
            result_dict[key] = sum_bipv_results_dicts_with_different_years(dict_1[key], dict_2[key],
                                                                           start_year_1,
                                                                           start_year_2, earliest_year,
                                                                           latest_year)
        elif isinstance(dict_1[key], list):
            list_1 = [0.0] * (latest_year - earliest_year)
            list_1[
            start_year_1 - earliest_year:start_year_1 - earliest_year + len(
                dict_1[key])] = \
                dict_1[key]
            list_2 = [0.0] * (latest_year - earliest_year)
            list_2[
            start_year_2 - earliest_year:start_year_2 - earliest_year + len(
                dict_2[key])] = \
                dict_2[key]
            result_dict[key] = [x + y for x, y in zip(list_1, list_2)]
        else:  # assuming ints or floats
            result_dict[key] = dict_1[key] + dict_2[key]

    return result_dict


def compute_cumulative_and_total_value_bipv_result_dict(bipv_results_dict):
    """
    Sum the values dictionnaries
    """

    for key in bipv_results_dict:
        if isinstance(bipv_results_dict[key], dict):
            bipv_results_dict[key] = compute_cumulative_and_total_value_bipv_result_dict(
                bipv_results_dict[key])
        elif isinstance(bipv_results_dict[key], list) and key == "yearly" and bipv_results_dict["yearly"] != []:
            if "cumulative" in bipv_results_dict:
                bipv_results_dict["cumulative"] = [sum(bipv_results_dict["yearly"][0:i]) for i in
                                                   range(1, len(bipv_results_dict["yearly"]) + 1)]
            if "total" in bipv_results_dict:
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


def from_sensorgrid_face_index_to_lb_face3d(sensorgrid_face_index, sensorgrid):
    """
    Convert the face index of a sensorgrid to the face index of a lb_face3d
    """
    face = sensorgrid.faces[sensorgrid_face_index]
    lb_point3d_list = [sensorgrid.vertices[i] for i in face]

    return Face3D(lb_point3d_list)
