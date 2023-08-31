"""
Functions used to load bipvs and to perfom  the simulation of the energy harvested
"""

import logging

from bipv.bipv_panel import BipvPanel

user_logger = logging.getLogger("user")
dev_logger = logging.getLogger("dev")


def init_bipv_on_sensor_grid(sensor_grid, pv_technology_obj, annual_panel_irradiance_list,
                             minimum_panel_eroi):
    """
    Initialize the bipvs on the sensor_grid and return a list of the bipvs.
    The function will check if the area of the faces of the sensor_grid is big enough to contain the bipvs
    and if the eroi of the bipvs is above the threshold set by the user.
    If the area is not big enough, it will raise a warning and the bipvs will not be initialized in those face of the mesh.
    :param sensor_grid: Honeybee SensorGrid object
    :param pv_technology_obj: PVPanelTechnology object
    :param annual_panel_irradiance_list: list of floats: annual irradiance on each face of the sensor_grid
    :param minimum_panel_eroi: float: minimum energy return on investment of the PV, (Default=1.2)
    :param panel_performance_ratio: float: performance ratio of the PV, Default=0.80  todo: should it be an attribute of pv_tech ? 
    :return panel_obj_list
    """
    # initialize the list of the panel objects
    panel_obj_list = []
    # Extract the parameters from the Sensorgrid qbd the pv_technology_obj
    lb_mesh_obj = sensor_grid.lb_mesh_obj
    mesh_face_area_list = lb_mesh_obj.mesh_face_area_list
    efficiency_loss_function = pv_technology_obj.efficiency_function
    pv_initial_efficiency = pv_technology_obj.initial_efficiency
    pv_area = pv_technology_obj.panel_area
    panel_performance_ratio = pv_technology_obj.initial_efficiency.panel_performance_ratio
    weibull_lifetime = pv_technology_obj.weibull_law_failure_parameters["lifetime"]
    # Initialize the flags
    area_flag_warning = False
    eroi_flag_warning = False

    for face_index, face in enumerate(lb_mesh_obj.faces):
        # Calculate the eroi of the panel
        energy_harvested = sum(
            [efficiency_loss_function(pv_initial_efficiency, i) * annual_panel_irradiance_list[
                face_index] * pv_area * panel_performance_ratio / 1000 for i in range(weibull_lifetime)])
        primary_energy = \
            pv_technology_obj.primary_energy_manufacturing + pv_technology_obj.primary_energy_recycling + \
            pv_technology_obj.primary_energy_transport
        panel_eroi = energy_harvested / primary_energy
        """
        Note that it is not exactly the reql eroi thqt is computed here, we assume that the panel will last for 
        the average lifetime of the weibull law.
        """
        # Check if the area is big enough and if the eroi is above the threshold
        if mesh_face_area_list[face_index] < pv_technology_obj.panel_area:
            area_flag_warning = True
        # Check if the eroi of teh panel is above the threshold
        elif panel_eroi <= minimum_panel_eroi:
            eroi_flag_warning = True
        else:
            new_panel = BipvPanel(face_index, pv_technology_obj)
            new_panel.initialize_or_replace_panel()
            panel_obj_list.append(new_panel)
    # raise flag if needed
    if area_flag_warning:
        user_logger.warning(
            "Some faces of the sensor grid are too small to contain a PV panel, no panel will be initialized in those faces")
        dev_logger.warning(
            "Some faces of the sensor grid are too small to contain a PV panel, no panel will be initialized in those faces")
    if eroi_flag_warning:
        user_logger.warning(
            "Some PV panels have an eroi below the threshold, no panel will be initialized in those faces")
        dev_logger.warning(
            "Some PV panels have an eroi below the threshold, no panel will be initialized in those faces")

    return panel_obj_list

def bipv_simulation_hourly_annual_irradiance(pv_panel_obj_list,path_time_step_illuminance_file):
    """

    """
def bipv_simulation_yearly_irradiance(pv_panel_obj_list,yearly_solar_radiation_values,study_duration_in_years, replacement_scenario="yearly", **kwargs):
    """

    """
def loop_over_the_years_for_solar_panels(pv_panel_obj_list, yearly_solar_radiation_values,
                                         study_duration_in_years, replacement_scenario="yearly", **kwargs):
    """
    Loop over every year of the study duration to get the energy harvested, the energy used and the dmfa waste harvested
    every year
    :param pv_panel_obj_list: list of panel objects
    :param yearly_solar_radiation_values: list of floats: list of the yearly cumulative solar radiation got by the solar
    radiation simulation in Wh/panel/year
    :param study_duration_in_years: int: duration of the study in years, Default=50
    :param replacement_scenario: string: replacement scenario chosen between
    "replace_failed_panels_every_X_year" and "replace_all_panels_every_X_year",
    Default="replace_failed_panels_every_X_year"
    :return energy_production_per_year_list: list of floats in kWh/year
    :return nb_of_panels_installed_list: list of int: list of the number of panels installed each year
    :return nb_of_failed_panels_list: list of int: list of the number of panels failing each year
    """
    energy_production_per_year_list = []
    nb_of_panels_installed_per_year_list = []
    nb_of_failed_panels_per_year_list = []

    for year in range(study_duration_in_years):
        # initialize
        energy_harvested = 0.
        nb_of_new_panels = 0
        nb_of_failed_panels = 0
        # Initialize panels for year 0
        if year == 0:
            for panel_obj in pv_panel_obj_list:
                panel_obj.initialize_or_replace_panel()
                nb_of_new_panels += 1

        # Replace according to replacement "scenario" \(- -)/
        if replacement_scenario == "yearly":
            # the code inside each statement
            for panel_obj in pv_panel_obj_list:
                if not panel_obj.is_panel_working():
                    panel_obj.initialize_or_replace_panel()
                    nb_of_new_panels += 1
        elif replacement_scenario == "every_X_years":
            replacement_year = kwargs["replacement_year"]
            if year != 0 and year % replacement_year == 0:
                for panel_obj in pv_panel_obj_list:
                    if not panel_obj.is_panel_working():
                        panel_obj.initialize_or_replace_panel()
                        nb_of_new_panels += 1

        # Increment of 1 year
        for panel_obj in pv_panel_obj_list:
            index_panel = pv_panel_obj_list.index(panel_obj)
            energy_harvested_panel, panel_failed = panel_obj.pass_year(yearly_solar_radiation_values[index_panel],
                                                                       performance_ratio)
            energy_harvested += energy_harvested_panel
            if panel_failed:
                nb_of_failed_panels += 1

        energy_production_per_year_list.append(energy_harvested)
        nb_of_panels_installed_per_year_list.append(nb_of_new_panels)
        nb_of_failed_panels_per_year_list.append(nb_of_failed_panels)

    return energy_production_per_year_list, nb_of_panels_installed_per_year_list, nb_of_failed_panels_per_year_list

