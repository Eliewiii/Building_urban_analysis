"""
todo @ Elie
"""
import logging

import numpy as np

from solar_panel.pv_panel import PvPanel

import csv
from libraries_addons.solar_panels.pv_efficiency_functions import get_efficiency_loss_function_from_string

user_logger = logging.getLogger("user")  # f"{__name__} user"
dev_logger = logging.getLogger("dev")  # f"{__name__} dev"

def load_panels_on_sensor_grid(sensor_grid, pv_technology_object, yearly_solar_radiation_values,
                               minimum_ratio_energy_harvested_on_primary_energy, performance_ratio):
    """
    Take a sensor grid and create a list of panels that correspond to each face of the mesh of the sensor grid
    The panels are initialized as switched on
    :param sensor_grid: sensor_grid of the face, roof, facade... we want to load the panels on
    :param pv_technology_object: PVPanelTechnology object
    :param yearly_solar_radiation_values: list of floats: list of the yearly cumulative solar radiation got by the solar
    radiation simulation in Wh/panel/year
    :param minimum_ratio_energy_harvested_on_primary_energy: float: minimum ratio between the energy harvested during the panel's
    lifetime and the energy necessary to produce, transport and recycle it. Default=1.2
    :param performance_ratio: float: performance ratio of the PV, Default=0.75
    :return panels
    """
    mesh = sensor_grid.mesh
    face_areas = mesh.face_areas
    panels = []

    efficiency_loss_function = get_efficiency_loss_function_from_string(pv_technology_object.efficiency_function)
    initial_efficiency = pv_technology_object.initial_efficiency
    area = pv_technology_object.panel_area
    weibull_lifetime = pv_technology_object.weibull_law_failure_parameters["lifetime"]

    for face in mesh.faces:
        energy_harvested = sum([efficiency_loss_function(initial_efficiency, i) * yearly_solar_radiation_values[
            mesh.faces.index(face)] * area * performance_ratio / 1000 for i in range(weibull_lifetime)])
        primary_energy = \
            pv_technology_object.primary_energy_manufacturing + pv_technology_object.primary_energy_recycling + \
            pv_technology_object.primary_energy_transport

        if face_areas[mesh.faces.index(face)] < pv_technology_object.panel_area:
            user_logger.warning("The area of the mesh's faces is not big enough to contain the PV panels. "
                            "Make a mesh with bigger faces")
            dev_logger.warning("The area of the mesh's faces is not big enough to contain the PV panels. "
                            "Make a mesh with bigger faces")
        elif (energy_harvested / primary_energy) <= minimum_ratio_energy_harvested_on_primary_energy:
            user_logger.warning("If a panel is put here, it won't produce enough energy to be profitable")
            dev_logger.warning("If a panel is put here, it won't produce enough energy to be profitable")
        else:
            panel_of_face = PvPanel(mesh.faces.index(face), pv_technology_object)
            panel_of_face.initialize_or_replace_panel()
            panels.append(panel_of_face)
    return panels


def loop_over_the_years_for_solar_panels(pv_panel_obj_list, yearly_solar_radiation_values, performance_ratio,
                                         study_duration_in_years, replacement_scenario="yearly", **kwargs):
    """
    Loop over every year of the study duration to get the energy harvested, the energy used and the dmfa waste harvested
    every year
    :param pv_panel_obj_list: list of panel objects
    :param yearly_solar_radiation_values: list of floats: list of the yearly cumulative solar radiation got by the solar
    radiation simulation in Wh/panel/year
    :param study_duration_in_years: int: duration of the study in years, Default=1.2
    :param performance_ratio: float: performance ratio of the PV, Default=0.75
    :param replacement_scenario: string: replacement scenario chosen
    :return energy_production_per_year_list: list of floats in kWh/year
    :return nb_of_panels_installed_list: list of int: list of the number of panels installed each year
    :return nb_of_failed_panels_list: list of int: list of the number of panels failing each year
    """
    energy_production_per_year_list = []
    nb_of_panels_installed_list = []
    nb_of_failed_panels_list = []

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
        nb_of_panels_installed_list.append(nb_of_new_panels)
        nb_of_failed_panels_list.append(nb_of_failed_panels)

    return energy_production_per_year_list, nb_of_panels_installed_list, nb_of_failed_panels_list


def write_to_csv_arr(header, arr, file_path):
    """
    write a list of int to a csv file
    :param header: list of str
    :param arr: list of lists of integers
    :param file_path: path to where the file should be written
    """
    with open(file_path, 'w') as f:
        writer = csv.writer(f, lineterminator='\n')
        writer.writerow(header)
        writer.writerows(arr)


def beginning_end_of_life_lca_results_in_lists(energy_production_per_year_list, nb_of_panels_installed_list,
                                               nb_of_failed_panels_list, pv_tech):
    """
    Take the results from function loop_over_the_years_for_solar_panels and use the pv_tech info to transform it to data
    :param energy_production_per_year_list: list of floats: describes the energy production each year
    :param nb_of_panels_installed_list: list of integers: describes how many panels are installed each year
    :param nb_of_failed_panels_list: list of integers: describes how many panels fail each year
    :param pv_tech: PVPanelTechnology object
    :return energy_production_per_year_list: list of floats
    :return lca_craddle_to_installation_primary_energy_list: list of floats: describes how much energy was used to manufacture the panels installed for
    each year
    :return lca_craddle_to_installation_carbon_list: list of floats: describes how much carbon was released to manufacture the panels installed,
    for each year
    :return dmfa_list: list of floats: describes the dmfa caused by the failed panels, for each year
    :return lca_recycling_primary_energy_list: list of float: describes how much energy was used to recycle the panels having failed
    """
    # todo: add comments
    panel_energy_craddle_to_installation = pv_tech.primary_energy_manufacturing + pv_tech.primary_energy_transport
    panel_carbon_craddle_to_installation = pv_tech.carbon_manufacturing + pv_tech.carbon_transport
    panel_dmfa = pv_tech.DMFA
    panel_primary_energy_recycling = pv_tech.primary_energy_recycling
    panel_carbon_recycling = pv_tech.carbon_recycling

    craddle_to_installation_primary_energy_list = [i * panel_energy_craddle_to_installation for i in
                                                   nb_of_panels_installed_list]
    craddle_to_installation_carbon_list = [i * panel_carbon_craddle_to_installation for i in
                                           nb_of_panels_installed_list]
    dmfa_list = [i * panel_dmfa for i in nb_of_failed_panels_list]
    lca_recycling_primary_energy_list = [i * panel_primary_energy_recycling for i in nb_of_panels_installed_list]
    lca_recycling_carbon_list = [i * panel_carbon_recycling for i in nb_of_panels_installed_list]

    return energy_production_per_year_list, craddle_to_installation_primary_energy_list, craddle_to_installation_carbon_list, \
        dmfa_list, lca_recycling_primary_energy_list, lca_recycling_carbon_list


def results_from_lists_to_dict(energy_production_per_year_list, craddle_to_installation_primary_energy_list,
                               craddle_to_installation_carbon_list, dmfa_list, lca_recycling_primary_energy_list,
                               lca_recycling_carbon_list):
    """
    Transform those results into a dictionary
    :param energy_production_per_year_list: list of floats describes the energy production each year
    :param craddle_to_installation_primary_energy_list: list of floats: describes how much energy was used to manufacture the panels
    installed for each year
    :param craddle_to_installation_carbon_list: list of floats: describes how much carbon was released to manufacture the panels
    installed for each year
    :param dmfa_list: list of floats: describes the dmfa caused by the failed panels, for each year
    :param lca_recycling_primary_energy_list: list of floats: describes how much energy is used to recycle the panels
    :return results_dict: dictionary containing all the data
    """
    # todo: add comments
    results_dict = {}
    energy_harvested_dict = {"list": energy_production_per_year_list, "total": sum(energy_production_per_year_list)}
    lca_craddle_to_installation_primary_energy_dict = {"list": craddle_to_installation_primary_energy_list,
                                                       "total": sum(craddle_to_installation_primary_energy_list)}
    lca_craddle_to_installation_carbon_dict = {"list": craddle_to_installation_carbon_list,
                                               "total": sum(craddle_to_installation_carbon_list)}
    dmfa_dict = {"list": dmfa_list, "total": sum(dmfa_list)}
    lca_recycling_primary_energy_dict = {"list": lca_recycling_primary_energy_list,
                                         "total": sum(lca_recycling_primary_energy_list)}
    lca_recycling_carbon_dict = {"list": lca_recycling_carbon_list, "total": sum(lca_recycling_carbon_list)}

    results_dict["energy_harvested"] = energy_harvested_dict
    results_dict["lca_craddle_to_installation_primary_energy"] = lca_craddle_to_installation_primary_energy_dict
    results_dict["lca_craddle_to_installation_carbon"] = lca_craddle_to_installation_carbon_dict
    results_dict["dmfa"] = dmfa_dict
    results_dict["lca_recycling_primary_energy"] = lca_recycling_primary_energy_dict
    results_dict["lca_recycling_carbon"] = lca_recycling_carbon_dict

    return results_dict


def get_cumul_values(list1):
    list_cumul = [sum(list1[0:i]) for i in range(1, len(list1) + 1)]
    return list_cumul


def add_elements_of_two_lists(list1, list2):
    if not list1:
        return list2
    elif not list2:
        return list1
    else:
        added_list = [sum(i) for i in zip(list1, list2)]
        return added_list


def transform_to_linear_function(x, y):
    """
    Transforms data into a linear function using linear regression.

    Arguments:
    x, y -- Arrays representing the x and y values of the data.

    Returns:
    slope -- Slope of the linear function.
    intercept -- Intercept of the linear function.
    """
    # Convert x and y to NumPy arrays
    x = np.array(x)
    y = np.array(y)

    # Calculate the slope and intercept
    mean_x = np.mean(x)
    mean_y = np.mean(y)
    slope = np.sum((x - mean_x) * (y - mean_y)) / np.sum((x - mean_x) ** 2)
    intercept = mean_y - slope * mean_x

    return slope, intercept


def generate_step_function(x_values, y_values):
    """
    Generates a step function from a set of x and y values.

    Arguments:
    x_values -- Array of x-values.
    y_values -- Array of y-values.

    Returns:
    step_function -- A function that represents the step function.
    """

    def step_function(x):
        # Find the index of the largest x-value that is less than or equal to the input x
        idx = np.searchsorted(x_values, x, side='right') - 1

        # Return the corresponding y-value
        return y_values[idx]

    return step_function


def find_intersection_functions(func1, func2, x_start, x_end, tol=1e-3, max_iter=500):
    """
    Finds the intersection of two functions using the bisection method.

    Arguments:
    func1, func2 -- Functions to find the intersection of.
    x_start, x_end -- Range of x-values to search for the intersection.
    tol -- Tolerance for the intersection value (default: 1e-6).
    max_iter -- Maximum number of iterations (default: 100).

    Returns:
    x_intersection -- Approximated x-value of the intersection.
    y_intersection -- Approximated y-value of the intersection.
    """
    x_left = x_start
    x_right = x_end

    for _ in range(max_iter):
        x_mid = (x_left + x_right) / 2
        y_mid1 = func1(x_mid)
        y_mid2 = func2(x_mid)

        if abs(y_mid1 - y_mid2) < tol:
            return x_mid, y_mid1

        if y_mid1 > y_mid2:
            x_right = x_mid
        else:
            x_left = x_mid

    # If no intersection is found within the maximum iterations
    raise RuntimeError("Intersection not found within the specified range and maximum iterations.")

