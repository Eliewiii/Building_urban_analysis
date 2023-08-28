"""
Functions used to load bipvs and to perfom  the simulation of the energy harvested
"""

import logging

from bipv.bipv_panel import BipvPanel

user_logger = logging.getLogger("user")
dev_logger = logging.getLogger("dev")



def init_bipv_on_sensor_grid(sensor_grid, pv_technology_obj, annual_panel_irradiance_list,
                               minimum_panel_eroi, panel_performance_ratio):
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
    weibull_lifetime = pv_technology_obj.weibull_law_failure_parameters["lifetime"]
    # Initialize the flags
    area_flag_warning = False
    eroi_flag_warning = False

    for face_index, face in enumerate(lb_mesh_obj.faces):
        # Calculate the eroi of the panel
        energy_harvested = sum([efficiency_loss_function(pv_initial_efficiency, i) * annual_panel_irradiance_list[
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
        user_logger.warning("Some faces of the sensor grid are too small to contain a PV panel, no panel will be initialized in those faces")
        dev_logger.warning("Some faces of the sensor grid are too small to contain a PV panel, no panel will be initialized in those faces")
    if eroi_flag_warning:
        user_logger.warning("Some PV panels have an eroi below the threshold, no panel will be initialized in those faces")
        dev_logger.warning("Some PV panels have an eroi below the threshold, no panel will be initialized in those faces")

    return panel_obj_list