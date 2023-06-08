from building.utils_building import *
import csv


def load_panels_on_sensor_grid(sensor_grid, pv_technology_object):
    """ Take a sensor grid and create a list of panels that correspond to each face of the mesh of the sensor grid
    The panels are initialized as switched on."""
    mesh = sensor_grid.mesh
    face_areas = mesh.face_areas
    panels = []
    for face in mesh.faces:
        if face_areas[mesh.faces.index(face)] < pv_technology_object.panel_area:
            logging.warning(f"The area of the mesh's faces is not big enough to contain the PV panels. "
                            f"Make a mesh with bigger faces")
        panel_of_face = PvPanel(mesh.faces.index(face), pv_technology_object)
        panel_of_face.initialize_or_replace_panel()
        panels.append(panel_of_face)
    return panels


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
    nb_of_panels_installed_list = []
    nb_of_failed_panels_list = []

    for year in range(study_duration_in_years):
        # initialize
        energy_produced = 0.
        nb_of_new_panels = 0
        nb_of_failed_panels = 0
        # Initialize panels for year 0
        if year == 0:
            for panel_obj in pv_panel_obj_list:
                panel_obj.initialize_or_replace_panel()
                nb_of_new_panels += 1
        # Increment of 1 year
        for panel_obj in pv_panel_obj_list:
            index_panel = pv_panel_obj_list.index(panel_obj)
            energy_produced_panel, panel_failed = panel_obj.pass_year(yearly_solar_radiation_values[index_panel])
            energy_produced += energy_produced_panel
            if panel_failed:
                nb_of_failed_panels += 1
        # Replace according to replacement "scenario" \(- -)/
        if replacement_scenario == "yearly":
            # the code inside each statement
            for panel_obj in pv_panel_obj_list:
                if not panel_obj.is_panel_working():
                    panel_obj.initialize_or_replace_panel()
                    nb_of_new_panels += 1
        elif replacement_scenario == "every_X_years":
            replacement_year = kwargs["replacement_year"]
            if year != 0 and year % replacement_year != 0:
                if not panel_obj.is_panel_working():
                    panel_obj.initialize_or_replace_panel()
                    nb_of_new_panels += 1

        # other scenario, replace every thing every X years?
        energy_production_per_year_list.append(energy_produced)
        nb_of_panels_installed_list.append(nb_of_new_panels)
        nb_of_failed_panels_list.append(nb_of_failed_panels)

    return energy_production_per_year_list, nb_of_panels_installed_list, nb_of_failed_panels_list


def write_to_csv_arr(header, arr, file_path):
    """
    write a list of int to a csv file
    :param list_of_int: list of integers
    :param file_path: path to where the file should be written
    """
    with open(file_path, 'w') as f:
        writer = csv.writer(f)
        writer.writerows(header)
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
    :return lca_energy_list: list of floats: describes how much energy was used to manufacture the panels installed for
    each year
    :return lca_carbon_list: list of floats: describes how much carbon was released to manufacture the panels installed,
    for each year
    :return dmfa_list: list of floats: describes the dmfa caused by the failed panels, for each year
    """
    panel_energy_manufacturing = pv_tech.energy_manufacturing
    panel_carbon_manufacturing = pv_tech.carbon_manufacturing
    panel_dmfa = pv_tech.DMFA

    lca_energy_list = [i * panel_energy_manufacturing for i in nb_of_panels_installed_list]
    lca_carbon_list = [i * panel_carbon_manufacturing for i in nb_of_panels_installed_list]
    dmfa_list = [i * panel_dmfa for i in nb_of_failed_panels_list]

    return energy_production_per_year_list, lca_energy_list, lca_carbon_list, dmfa_list


def results_from_lists_to_dict(energy_production_per_year_list, lca_energy_list, lca_carbon_list, dmfa_list):
    """
    Transform those results into a dictionary
    :param energy_production_per_year_list: list of floats describes the energy production each year
    :param lca_energy_list: list of floats: describes how much energy was used to manufacture the panels installed for
    each year
    :param lca_carbon_list: list of floats: describes how much carbon was released to manufacture the panels installed,
    for each year
    :param dmfa_list: list of floats: describes the dmfa caused by the failed panels, for each year
    """

    results_dict = {}
    energy_produced_dict = {"list": energy_production_per_year_list, "total": sum(energy_production_per_year_list)}
    lca_energy_dict = {"list": lca_energy_list, "total": sum(lca_energy_list)}
    lca_carbon_dict = {"list": lca_carbon_list, "total": sum(lca_carbon_list)}
    dmfa_dict = {"list": dmfa_list, "total": sum(dmfa_list)}

    results_dict["energy_produced"] = energy_produced_dict
    results_dict["lca_energy"] = lca_energy_dict
    results_dict["lca_carbon"] = lca_carbon_dict
    results_dict["dmfa"] = dmfa_dict

    return results_dict
