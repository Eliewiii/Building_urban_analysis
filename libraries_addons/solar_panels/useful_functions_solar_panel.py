from solar_panel.panel import Panel
from solar_panel.pvmaterial import PanelTechnology
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
