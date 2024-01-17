"""
Functions to check the simulation parameters
"""

import json
import os

from honeybee_energy.simulation.parameter import SimulationParameter
from ladybug.epw import EPW

required_outputs = ["Zone Electric Equipment Electricity Energy", "Zone Ideal Loads Supply Air Total Cooling Energy",
                    "Zone Ideal Loads Supply Air Total Heating Energy", "Zone Lights Electricity Energy"]


def check_simulation_parameters(path_hbjson_simulation_parameter_file, path_file_epw, ddy_file=None):
    """
    Check if the simulation parameter file is valid
    :param path_hbjson_simulation_parameter_file: str, path to the simulation parameter file
    :param path_file_epw: str, path to the epw file
    :param ddy_file: str, path to the ddy (design day) file
    :return hb_sim_parameter_obj: Honeybee SimulationParameter object, epw_obj: EPW object
    :return lb_epw_obj: Ladybug EPW object

    """

    # Check if the file exists
    if not os.path.isfile(path_hbjson_simulation_parameter_file):
        raise FileNotFoundError("The simulation parameter file does not exist.")
    elif not os.path.isfile(path_file_epw):
        raise FileNotFoundError("The epw file does not exist.")

    # Check if the file contains a valid simulation parameters
    try:
        with open(path_hbjson_simulation_parameter_file, 'r') as f:
            json_dic = json.load(f)
        hb_sim_parameter_obj = SimulationParameter.from_dict(json_dic)
    except:
        raise ValueError("The simulation parameter file is not valid, it cannot be loaded.")

    # Check if the epw file is valid
    try:
        lb_epw_obj = EPW(path_file_epw)
    except:
        raise ValueError("The epw file is not valid, it cannot be loaded.")

    # Check if there is a ddl to set the design days, otherwise approximate them from the epw file
    if ddy_file is not None and os.path.isfile(ddy_file):
        hb_sim_parameter_obj.sizing_parameter.add_from_ddy_996_004(ddy_file)
    else:
        des_days = [lb_epw_obj.approximate_design_day('WinterDesignDay'),
                    lb_epw_obj.approximate_design_day('SummerDesignDay')]
        hb_sim_parameter_obj.sizing_parameter.design_days = des_days

    # Check if the output frequency is not annual, the tool requires at least monthly outputs
    if hb_sim_parameter_obj.output.reporting_frequency == "annual":
        hb_sim_parameter_obj.output.reporting_frequency = "monthly"
    # Check if the simulation outputs contain heating, cooling, lighting and equipment and add them if needed
    for output in required_outputs:
        if output not in hb_sim_parameter_obj.output.outputs:
            hb_sim_parameter_obj.output.outputs.add_output(output)

    return hb_sim_parameter_obj, lb_epw_obj
