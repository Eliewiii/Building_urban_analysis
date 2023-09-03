"""
todo
"""

import os
import logging
import shutil

from copy import deepcopy

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
    "minimum_panel_eroi": None,
    "study_duration_in_years": None,
    "replacement_scenario": {}
}
empty_sub_results_dict = {
    "energy_harvested": {"yearly": None, "total": None},
    "lca_primary_energy": {
        "material_extraction_and_manufacturing": {"yearly": None, "total": None},
        "transportation": {"yearly": None, "total": None},
        "recycling": {"yearly": None, "total": None},
        "total": {"yearly": None, "total": None}
    },
    "lca_carbon_footprint": {
        "material_extraction_and_manufacturing": {"yearly": None, "total": None},
        "transportation": {"yearly": None, "total": None},
        "recycling": {"yearly": None, "total": None},
        "total": {"yearly": None, "total": None}
    },
    "dmfa_waste": {"yearly": None, "total": None}
}

empty_results_dict = {
    "roof": {**deepcopy(empty_sub_results_dict), **{"annual_panel_irradiance_list": None}},
    "facades": {**deepcopy(empty_sub_results_dict), **{"annual_panel_irradiance_list": None}},
    "total": deepcopy(empty_sub_results_dict)
}

sun_up_hours_file_name = "sun-up-hours.txt"
name_roof_ill_file = "roof.ill"
name_facades_ill_file = "facades.ill"
name_roof_sun_up_hours_file = "roof_" + sun_up_hours_file_name
name_facades_sun_up_hours_file = "facades_" + sun_up_hours_file_name


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
        # results
        self.results_dict = empty_results_dict
        # parameters
        self.parameter_dict = empty_parameter_dict

    def set_mesh_parameters(self, bipv_on_roof, bipv_on_facades, roof_grid_size_x=1,
                            facades_grid_size_x=1, roof_grid_size_y=1, facades_grid_size_y=1, offset_dist=0.1):
        """
        Set the mesh parameters for the simulation
        :param bipv_on_roof: bool: default=True
        :param bipv_on_facades: bool: default=True
        :param roof_grid_size_x: Number for the size of the test grid
        :param facades_grid_size_x: Number for the size of the test grid
        :param roof_grid_size_y: Number for the size of the test grid
        :param facades_grid_size_y: Number for the size of the test grid
        :param offset_dist: Number for the distance to move points from the surfaces of the geometry of the model.
        """
        self.on_roof = bipv_on_roof
        self.on_facades = bipv_on_facades
        self.parameter_dict["roof"]["grid_x"] = roof_grid_size_x
        self.parameter_dict["roof"]["grid_y"] = roof_grid_size_y
        self.parameter_dict["facades"]["grid_x"] = facades_grid_size_x
        self.parameter_dict["facades"]["grid_y"] = facades_grid_size_y
        self.parameter_dict["roof"]["offset"] = offset_dist
        self.parameter_dict["facades"]["offset"] = offset_dist

    def set_bipv_parameters(self, roof_pv_tech_obj, facades_pv_tech_obj, minimum_panel_eroi,
                            study_duration_in_years, replacement_scenario, efficiency_computation_method,
                            **kwargs):
        """
        Set the BIPV parameters for the simulation
        :param roof_pv_tech_obj: PVTechnology object for the roof
        :param facades_pv_tech_obj: PVTechnology object for the facades
        :param minimum_panel_eroi: float : the minimum EROI of the panels
        :param study_duration_in_years: int : the duration of the study in years
        :param replacement_scenario: str : the replacement scenario of the panels
        :param efficiency_computation_method: str : the method to compute the efficiency of the panels
        :param kwargs: dict : other parameters
        todo: add the additional paameters
        """
        self.parameter_dict["roof"]["panel_technology"] = roof_pv_tech_obj
        self.parameter_dict["facades"]["panel_technology"] = facades_pv_tech_obj
        self.parameter_dict["minimum_panel_eroi"] = minimum_panel_eroi
        self.parameter_dict["study_duration_in_years"] = study_duration_in_years
        self.parameter_dict["replacement_scenario"] = replacement_scenario
        self.parameter_dict["efficiency_computation_method"] = efficiency_computation_method
        # todo: add the additional paameters

    def generate_sensor_grid(self, hb_model_obj, roof_grid_size_x=1, facades_grid_size_x=1, roof_grid_size_y=1,
                             facades_grid_size_y=1, offset_dist=0.1):
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
        if self.on_facades:
            self.facades_sensorgrid_dict = generate_sensor_grid_for_hb_model(hb_model_obj, facades_grid_size_x,
                                                                             facades_grid_size_y, offset_dist,
                                                                             "facades")
        else:
            user_logger.warning(f"You did not precise whether you want to run the simulation on the roof, "
                                f"the facades or both")
            dev_logger.warning(f"You did not precise whether you want to run the simulation on the roof, "
                               f"the facades or both")

    def run_annual_solar_radiation(self, building_id, hb_model_obj, context_shading_hb_aperture_list,
                                   path_simulation_folder, path_epw_file, overwrite=False,
                                   north_angle=0, silent=False):
        """

        """
        path_folder_run_radiation_temp = os.path.join(path_simulation_folder, name_temporary_files_folder,
                                                      str(building_id))
        path_result_folder = os.path.join(path_simulation_folder, name_radiation_simulation_folder,
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
                # Delete the useless results files and move the results to the right folder
                path_folder_result_run_radiation_temp_roof = os.path.join(path_folder_run_radiation_temp_roof,
                                                                          "annual_irradiance",
                                                                          "results", "total")
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
            if self.results_dict["facades"]["annual_panel_irradiance_list"] is None or overwrite:
                # Make a copy of the Honeybee Model and add the SensorGrid and context to it
                hb_model_copy_facades = hb_model_obj.duplicate()
                hb_model_copy_facades.properties.radiance.add_sensor_grid(
                    SensorGrid.from_dict(self.facades_sensorgrid_dict))
                hb_model_copy_facades.add_shades(context_shading_hb_aperture_list)
                # run in the temporary folder
                path_folder_run_radiation_temp_facades = os.path.join(path_folder_run_radiation_temp,
                                                                      "facades")
                self.results_dict["facades"][
                    "annual_panel_irradiance_list"] = run_hb_model_annual_irradiance_simulation(
                    hb_model_obj=hb_model_obj,
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
                                  facades_pv_tech_obj, efficiency_computation_method="yearly",
                                  minimum_panel_eroi=1.2,
                                  study_duration_in_years=50,
                                  replacement_scenario="replace_failed_panels_every_X_years", **kwargs):
        """
        Run the simulation of the energy harvested by the bipvs
        :param path_simulation_folder: path to the simulation folder
        :param building_id: str: id of the building
        :param roof_pv_tech_obj: BipvTechnology object of the roof BIPV panels
        :param facades_pv_tech_obj: BipvTechnology object of the facades BIPV panels
        :param efficiency_computation_method: str: method to compute the efficiency of the panels
        :param minimum_panel_eroi: float: minimum EROI of the PV panels
        :param study_duration_in_years: int: duration of the study in years
        :param replacement_scenario: dict: replacement scenario of the panels
        :param kwargs: todo
        """
        # Set BIPV parameters
        self.set_bipv_parameters(roof_pv_tech_obj=roof_pv_tech_obj, facades_pv_tech_obj=facades_pv_tech_obj,
                                 efficiency_computation_method=efficiency_computation_method,
                                 minimum_panel_eroi=minimum_panel_eroi,
                                 study_duration_in_years=study_duration_in_years,
                                 replacement_scenario=replacement_scenario, **kwargs)
        # Init flags
        run_bipv_on_roof = False
        run_bipv_on_facades = False
        # Roof
        if self.on_roof and self.roof_sensorgrid_dict is not None and self.results_dict["roof"][
            "annual_panel_irradiance_list"] is not None:
            run_bipv_on_roof = True
            # Init the BIPV panels on the roof
            self.roof_panel_list = init_bipv_on_sensor_grid(
                sensor_grid=SensorGrid.from_dict(self.roof_sensorgrid_dict),
                pv_technology_obj=roof_pv_tech_obj,
                annual_panel_irradiance_list=self.results_dict["roof"]["annual_panel_irradiance_list"],
                minimum_panel_eroi=minimum_panel_eroi)
            # Run the simulation roof
            if efficiency_computation_method == "yearly":
                roof_energy_harvested_yearly_list, roof_nb_of_panels_installed_yearly_list = bipv_energy_harvesting_simulation_yearly_annual_irradiance(
                    pv_panel_obj_list=self.roof_panel_list,
                    annual_solar_irradiance_value=self.results_dict["roof"]["annual_panel_irradiance_list"],
                    study_duration_in_years=study_duration_in_years,
                    replacement_scenario=replacement_scenario, **kwargs)
            elif efficiency_computation_method == "hourly":
                path_result_folder = os.path.join(path_simulation_folder, name_radiation_simulation_folder,
                                                  str(building_id))
                path_ill_file = os.path.join(path_result_folder, name_roof_ill_file)
                path_sun_up_hours_file = os.path.join(path_result_folder, name_roof_sun_up_hours_file)
                roof_energy_harvested_yearly_list, roof_nb_of_panels_installed_yearly_list = bipv_energy_harvesting_simulation_hourly_annual_irradiance(
                    pv_panel_obj_list=self.roof_panel_list,
                    path_ill_file=path_ill_file,
                    path_sun_up_hours_file=path_sun_up_hours_file,
                    study_duration_in_years=study_duration_in_years,
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
            roof_bipv_result_dict = convert_results_to_dict(
                energy_harvested_yearly_list=roof_energy_harvested_yearly_list,
                primary_energy_material_extraction_and_manufacturing_yearly_list=roof_primary_energy_material_extraction_and_manufacturing_yearly_list,
                primary_energy_transportation_yearly_list=roof_primary_energy_transportation_yearly_list,
                primary_energy_recycling_yearly_list=roof_primary_energy_recycling_yearly_list,
                carbon_material_extraction_and_manufacturing_yearly_list=roof_carbon_material_extraction_and_manufacturing_yearly_list,
                carbon_transportation_yearly_list=roof_carbon_transportation_yearly_list,
                carbon_recycling_yearly_list=roof_carbon_recycling_yearly_list,
                dmfa_waste_yearly_list=roof_dmfa_waste_yearly_lis)
            self.results_dict["roof"] = {**roof_bipv_result_dict,
                                         **{self.results_dict["roof"]["annual_panel_irradiance_list"]}}
            # Facade
        if self.on_facades and self.facades_sensorgrid_dict is not None and self.results_dict["facades"][
            "annual_panel_irradiance_list"] is not None:
            run_bipv_on_facades = True
            # Init the BIPV panels on the facades
            self.facades_panel_list = init_bipv_on_sensor_grid(
                sensor_grid=SensorGrid.from_dict(self.facades_sensorgrid_dict),
                pv_technology_obj=facades_pv_tech_obj,
                annual_panel_irradiance_list=self.results_dict["facades"]["annual_panel_irradiance_list"],
                minimum_panel_eroi=minimum_panel_eroi)
            # Run the simulation facades
            if efficiency_computation_method == "yearly":
                facades_energy_harvested_yearly_list, facades_nb_of_panels_installed_yearly_list = bipv_energy_harvesting_simulation_yearly_annual_irradiance(
                    pv_panel_obj_list=self.facades_panel_list,
                    annual_solar_irradiance_value=self.results_dict["facades"]["annual_panel_irradiance_list"],
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
                facades_bipv_result_dict = convert_results_to_dict(
                    energy_harvested_yearly_list=facades_energy_harvested_yearly_list,
                    primary_energy_material_extraction_and_manufacturing_yearly_list=facades_primary_energy_material_extraction_and_manufacturing_yearly_list,
                    primary_energy_transportation_yearly_list=facades_primary_energy_transportation_yearly_list,
                    primary_energy_recycling_yearly_list=facades_primary_energy_recycling_yearly_list,
                    carbon_material_extraction_and_manufacturing_yearly_list=facades_carbon_material_extraction_and_manufacturing_yearly_list,
                    carbon_transportation_yearly_list=facades_carbon_transportation_yearly_list,
                    carbon_recycling_yearly_list=facades_carbon_recycling_yearly_list,
                    dmfa_waste_yearly_list=facades_dmfa_waste_yearly_lis)
                self.results_dict["facades"] = {**facades_bipv_result_dict,
                                                **{self.results_dict["facades"]["annual_panel_irradiance_list"]}}

        # Total results
        if run_bipv_on_roof and run_bipv_on_facades:
            self.results_dict["total"] = sum_dicts(roof_bipv_result_dict, facades_bipv_result_dict)
        elif run_bipv_on_roof:
            self.results_dict["total"] = roof_bipv_result_dict
        elif run_bipv_on_facades:
            self.results_dict["total"] = facades_bipv_result_dict
        else:
            None



@staticmethod
def convert_results_to_dict(energy_harvested_yearly_list,
                            primary_energy_material_extraction_and_manufacturing_yearly_list,
                            primary_energy_transportation_yearly_list, primary_energy_recycling_yearly_list,
                            carbon_material_extraction_and_manufacturing_yearly_list,
                            carbon_transportation_yearly_list, carbon_recycling_yearly_list,
                            dmfa_waste_yearly_list):
    """
    Convert the results to a dict
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

    results_dict = deepcopy(empty_results_dict)
    # Energy harvested
    results_dict["energy_harvested"]["yearly"] = energy_harvested_yearly_list
    results_dict["energy_harvested"]["total"] = sum(energy_harvested_yearly_list)
    # LCA primary
    results_dict["lca_primary_energy"]["material_extraction_and_manufacturing"][
        "yearly"] = primary_energy_material_extraction_and_manufacturing_yearly_list
    results_dict["lca_primary_energy"]["material_extraction_and_manufacturing"][
        "total"] = sum(primary_energy_material_extraction_and_manufacturing_yearly_list)
    results_dict["lca_primary_energy"]["transportation"]["yearly"] = primary_energy_transportation_yearly_list
    results_dict["lca_primary_energy"]["transportation"]["total"] = sum(primary_energy_transportation_yearly_list)
    results_dict["lca_primary_energy"]["recycling"]["yearly"] = primary_energy_recycling_yearly_list
    results_dict["lca_primary_energy"]["recycling"]["total"] = sum(primary_energy_recycling_yearly_list)
    results_dict["lca_primary_energy"]["total"]["yearly"] = [sum(i) for i in zip(
        primary_energy_transportation_yearly_list, primary_energy_material_extraction_and_manufacturing_yearly_list,
        primary_energy_recycling_yearly_list)]
    results_dict["lca_primary_energy"]["total"]["total"] = sum(
        results_dict["lca_primary_energy"]["total"]["yearly"])
    # LCA carbon footprint
    results_dict["lca_carbon_footprint"]["material_extraction_and_manufacturing"][
        "yearly"] = carbon_material_extraction_and_manufacturing_yearly_list
    results_dict["lca_carbon_footprint"]["material_extraction_and_manufacturing"][
        "total"] = sum(carbon_material_extraction_and_manufacturing_yearly_list)
    results_dict["lca_carbon_footprint"]["transportation"]["yearly"] = carbon_transportation_yearly_list
    results_dict["lca_carbon_footprint"]["transportation"]["total"] = sum(carbon_transportation_yearly_list)
    results_dict["lca_carbon_footprint"]["recycling"]["yearly"] = carbon_recycling_yearly_list
    results_dict["lca_carbon_footprint"]["recycling"]["total"] = sum(carbon_recycling_yearly_list)
    results_dict["lca_carbon_footprint"]["total"]["yearly"] = [sum(i) for i in zip(
        carbon_transportation_yearly_list, carbon_material_extraction_and_manufacturing_yearly_list,
        carbon_recycling_yearly_list)]
    results_dict["lca_carbon_footprint"]["total"]["total"] = sum(
        results_dict["lca_carbon_footprint"]["total"]["yearly"])
    # DMFA
    results_dict["dmfa_waste"]["yearly"] = dmfa_waste_yearly_list
    results_dict["dmfa_waste"]["total"] = sum(dmfa_waste_yearly_list)

    return results_dict


def results_to_csv(self):
    """

    """


def results_to_figures(self):
    """

    """

def sum_dicts(*args):
    if not args:
        return {}

    result_dict = args[0].copy()

    for d in args[1:]:
        for key in d:
            if isinstance(d[key], dict):
                result_dict[key] = sum_dicts(result_dict[key], d[key])
            elif isinstance(d[key], list):
                result_dict[key] = [x + y for x, y in zip(result_dict[key], d[key])]
            else: # assuming ints or floats
                result_dict[key] += d[key]

    return result_dict

