from solar_panel.pv_panel import Panel
from solar_panel.pv_panel_technology import PanelTechnology
from building.utils_building import *


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
        panel_of_face.switch_on_panel()
        panels.append(panel_of_face)
    return panels


def add_year_to_panels_automatic_replacement(list_panels, pv_technology_object, carbon_footprint_manu, dmfa):
    for panel in list_panels:
        if panel.is_panel_working() and panel.panel_not_in_last_year():  # if the panel is working and its not in its
            # last year of functioning, we add one year to its age
            panel.add_year_to_panel()
        elif panel.is_panel_working():  # if the panel is working, and it's its last year of functioning, ie. age =
            # life expectancy
            panel.switch_off_panel()  # we switch off the panel
            panel.switch_on_panel()  # we switch it on back since we are in an automatic replace of panels scenario
            carbon_footprint_manu += pv_technology_object.carbon_footprint_manufacturing  # we add the carbon footprint
            # manufacturing the new panel caused to the total carbon footprint of manufacturing
            dmfa += pv_technology_object.DMFA  # same with the dmfa


def add_year_to_panels_other_scenarios(list_panels, pv_technology_object, carbon_footprint_manu, dmfa, time,
                                       replacement_cycle_time=5):
    """Args
    list_panels : list of Panel objects
    pv_technology_object : PanelTechnology object
    carbon_footprint_manu : carbon footprint due to the manufacturing of panels until now
    dmfa : dmfa due to the recycling of panel until now
    time : year we are in (civil or from 0 to year of end of study, 100 for example
    replacement_cycle_time : we replace panels only when this time has elapsed, every 5, 10... years for example"""
    for panel in list_panels:
        if panel.is_panel_working() and panel.panel_not_in_last_year():  # if the panel is working and its not in its
            # last year of functioning, we add one year to its age
            panel.add_year_to_panel()
        elif panel.is_panel_working():  # if the panel is working, and it's its last year of functioning, ie. age =
            # life expectancy
            panel.switch_off_panel()  # we switch off the panel
            dmfa += pv_technology_object.DMFA  # we add the dmfa of the old panel to the total dmfa
            if time % replacement_cycle_time == 0:  # if time is a multiple of replacement cycle time then we replace
                # automatically the panel
                panel.switch_on_panel()  # we switch it on back since we are in an automatic replace of panels scenario
                carbon_footprint_manu += pv_technology_object.carbon_footprint_manufacturing  # we add the carbon
                # footprint manufacturing the new panel caused to the total carbon footprint of manufacturing
        else:
            if time % replacement_cycle_time == 0:  # if time is a multiple of replacement cycle time then we replace
                # automatically the panel
                panel.switch_on_panel()  # we switch it on back since we are in an automatic replace of panels scenario
                carbon_footprint_manu += pv_technology_object.carbon_footprint_manufacturing  # we add the carbon
                # footprint manufacturing the new panel caused to the total carbon footprint of manufacturing


def loop_over_the_years_for_solar_panels(pv_panel_obj_list, study_duration_in_years=50, replacement_scenario="yearly",
                                         **kwargs):
    """

    """
    energy_production_per_year_list = []
    lca_carbon_footprint_generated_per_year_list = []
    dmfa_waste_generated_per_year_list = []

    for year in range(study_duration_in_years):
        # initialize
        energy_produced = 0.
        lca_carbon_footprint = 0.
        dmfa_waste = 0.
        # Initialize panels for year 0
        if year is 0:
            for panel_obj in pv_panel_obj_list:
                lca_carbon_footprint += panel_obj.replace_panel()
        # Increment of 1 year
        for panel_obj in pv_panel_obj_list:
            energy_produced_panel, dmfa_waste_panel = panel_obj.pass_year(year=year)
            energy_produced += energy_produced_panel
            dmfa_waste += dmfa_waste_panel
        # Replace according to replacement "scenarii" \(- -)/
        if replacement_scenario is "yearly":
            # the code inside each statement
            for panel_obj in pv_panel_obj_list:
                if not panel_obj.is_panel_working():
                    lca_carbon_footprint += panel_obj.replace_panel()
        elif replacement_scenario is "every_X_years":
            replacement_year = kwargs["replacement_year"]
            if year is not 0 and year%replacement_year is 0:
                if not panel_obj.is_panel_working():
                    lca_carbon_footprint += panel_obj.replace_panel()

        # other scenario, replace every thing every X years?






        energy_production_per_year_list.append(energy_produced)
        lca_carbon_footprint_generated_per_year_list.append(lca_carbon_footprint)
        dmfa_waste_generated_per_year_list.append(dmfa_waste)

















