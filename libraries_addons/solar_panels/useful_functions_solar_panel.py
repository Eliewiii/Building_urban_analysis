from solar_panel.pv_panel import Panel
from solar_panel.pv_panel_technology import PanelTechnology
from building.utils_building import *
import csv


def load_panels_on_sensor_grid(sensor_grid, pv_technology_object):
    """ Take a sensor grid and create a list of panels that correspond to each face of the mesh of the sensor grid
    The panels are initialized as switched on."""
    mesh = sensor_grid.mesh
    panels = []
    for face in mesh.faces:
        if face.area < pv_technology_object.panel_area:
            logging.warning(f"The area of the mesh's faces is not big enough to contain the PV panels. "
                            f"Make a mesh with bigger faces")
        panel_of_face = Panel(mesh.faces.index(face), pv_technology_object)
        panel_of_face.initialize_or_replace_panel()
        panels.append(panel_of_face)
    return panels


def loop_over_the_years_for_solar_panels_2(pv_panel_obj_list, yearly_solar_radiation_values, study_duration_in_years,
                                           replacement_scenario="yearly", **kwargs):
    """
    Loop over every year of the study duration to get the energy produced, the energy used and the dmfa waste produced
    every year
    :param pv_panel_obj_list: list of panel objects
    :param yearly_solar_radiation_values: list of floats: list of the yearly cumulative solar radiation got by the solar
    radiation simulation in Wh/panel/year
    :param study_duration_in_years: int: duration of the study in years
    :param replacement_scenario: string: replacement scenario chosen
    :return energy_production_per_year_list: list of floats in kWh/panel/year
    :return lca_energy_used_per_year_list:
    :return lca_energy_used_per_year_list:
    """
    energy_production_per_year_list = []
    nb_of_panels_installed_list = []
    nb_of_failed_panels_list = []

    for year in range(study_duration_in_years):
        # initialize
        energy_produced = 0.
        nb_of_new_panels = 0
        nb_of_failed_panels = 0
        # Initialize panels for year 0
        if year is 0:
            for panel_obj in pv_panel_obj_list:
                panel_obj.initialize_or_replace_panel_2()
                nb_of_new_panels += 1
        # Increment of 1 year
        for panel_obj in pv_panel_obj_list:
            index_panel = pv_panel_obj_list.index(panel_obj)
            energy_produced_panel, panel_failed = panel_obj.pass_year(yearly_solar_radiation_values[index_panel],
                                                                      year=year)
            energy_produced += energy_produced_panel
            if panel_failed:
                nb_of_failed_panels += 1
        # Replace according to replacement "scenario" \(- -)/
        if replacement_scenario is "yearly":
            # the code inside each statement
            for panel_obj in pv_panel_obj_list:
                if not panel_obj.is_panel_working():
                    panel_obj.initialize_or_replace_panel_2()
                    nb_of_new_panels += 1
        elif replacement_scenario is "every_X_years":
            replacement_year = kwargs["replacement_year"]
            if year is not 0 and year % replacement_year is 0:
                if not panel_obj.is_panel_working():
                    panel_obj.initialize_or_replace_panel_2()
                    nb_of_new_panels += 1

        # other scenario, replace every thing every X years?
        energy_production_per_year_list.append(energy_produced)
        nb_of_panels_installed_list.append(nb_of_new_panels)
        nb_of_failed_panels_list.append(nb_of_failed_panels)

    return energy_production_per_year_list, nb_of_panels_installed_list, nb_of_failed_panels_list


def write_to_csv_list(list_of_int, file_path):
    with open(file_path, 'w') as f:
        writer = csv.writer(f)
        writer.writerows(list_of_int)


def regular_calculation_manufacturing_energy_dmfa(nb_of_panels_installed_list, nb_of_failed_panels_list, pv_tech):
    panel_energy_manufacturing = pv_tech.energy_manufacturing
    panel_dmfa = pv_tech.DMFA

    lca_energy_used_per_year_list = [i * panel_energy_manufacturing for i in nb_of_panels_installed_list]
    dmfa_waste_generated_per_year_list = [i * panel_dmfa for i in nb_of_failed_panels_list]

    return lca_energy_used_per_year_list, dmfa_waste_generated_per_year_list


'''
def loop_over_the_years_for_solar_panels(pv_panel_obj_list, yearly_solar_radiation_values, study_duration_in_years,
                                         replacement_scenario="yearly", **kwargs):
    """
    Loop over every year of the study duration to get the energy produced, the energy used and the dmfa waste produced
    every year
    :param pv_panel_obj_list: list of panel objects
    :param yearly_solar_radiation_values: list of floats: list of the yearly cumulative solar radiation got by the solar
    radiation simulation in Wh/panel/year
    :param study_duration_in_years: int: duration of the study in years
    :param replacement_scenario: string: replacement scenario chosen
    :return energy_production_per_year_list: list of floats in kWh/panel/year
    :return lca_energy_used_per_year_list:
    :return lca_energy_used_per_year_list:
    """
    energy_production_per_year_list = []
    lca_energy_used_per_year_list = []
    dmfa_waste_generated_per_year_list = []

    for year in range(study_duration_in_years):
        # initialize
        energy_produced = 0.
        lca_energy = 0.
        dmfa_waste = 0.
        # Initialize panels for year 0
        if year is 0:
            for panel_obj in pv_panel_obj_list:
                lca_energy += panel_obj.replace_panel()
        # Increment of 1 year
        for panel_obj in pv_panel_obj_list:
            index_panel = pv_panel_obj_list.index(panel_obj)
            energy_produced_panel, dmfa_waste_panel = panel_obj.pass_year(yearly_solar_radiation_values[index_panel],
                                                                          year=year)
            energy_produced += energy_produced_panel
            dmfa_waste += dmfa_waste_panel
        # Replace according to replacement "scenario" \(- -)/
        if replacement_scenario is "yearly":
            # the code inside each statement
            for panel_obj in pv_panel_obj_list:
                if not panel_obj.is_panel_working():
                    lca_energy += panel_obj.initialize_or_replace_panel()
        elif replacement_scenario is "every_X_years":
            replacement_year = kwargs["replacement_year"]
            if year is not 0 and year % replacement_year is 0:
                if not panel_obj.is_panel_working():
                    lca_energy += panel_obj.initialize_or_replace_panel()

        # other scenario, replace every thing every X years?
        energy_production_per_year_list.append(energy_produced)
        lca_energy_used_per_year_list.append(lca_energy)
        dmfa_waste_generated_per_year_list.append(dmfa_waste)

    return energy_production_per_year_list, lca_energy_used_per_year_list, dmfa_waste_generated_per_year_list

'''
