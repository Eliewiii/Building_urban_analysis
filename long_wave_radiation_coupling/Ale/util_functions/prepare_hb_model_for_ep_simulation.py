import os
import json

from honeybee_energy import run
from honeybee_energy.simulation.parameter import SimulationParameter

from ladybug.epw import EPW

def from_hbjson_to_idf(dir_to_write_idf_in, path_hbjson_file, path_file_epw, path_simulation_parameter):
    """
    Convert a hbjson file to an idf file (input for EnergyPlus)
    """
    # add design days to the simulation paramters
    add_design_days_timestep_and_terrain_to_simulation_parameters(path_simulation_parameter, path_file_epw, terrain_type_in="City",
                                             timestep_in=6)
    # pass the hbjson file to Openstudio to convert it to idf
    osw = run.to_openstudio_osw(osw_directory=dir_to_write_idf_in,
                                model_path=path_hbjson_file,
                                sim_par_json_path=path_simulation_parameter,
                                epw_file=path_file_epw)
    ## Run simulation in OpenStudio to generate IDF ##
    return run.run_osw(osw, silent=False)


def add_design_days_timestep_and_terrain_to_simulation_parameters(path_simulation_parameter, path_file_epw, terrain_type_in="City",
                                             timestep_in=6):
    """ Add the design days, necessary for EnergyPlus to simulate, to the simulation parameters """
    # sim_parameter_obj = None
    with open(path_simulation_parameter, 'r') as f:
        json_dic = json.load(f)
        sim_parameter_obj = SimulationParameter.from_dict(json_dic)
    epw_obj = EPW(path_file_epw)
    des_days = [epw_obj.approximate_design_day('WinterDesignDay'),
                epw_obj.approximate_design_day('SummerDesignDay')]
    sim_parameter_obj.sizing_parameter.design_days = des_days

    sim_parameter_obj.terrain_type = terrain_type_in
    sim_parameter_obj.timestep = timestep_in
    # replace the simulatio_paramter.json by the updated one
    sim_parameter_dic = SimulationParameter.to_dict(sim_parameter_obj)
    with open(path_simulation_parameter, "w") as json_file:
        json.dump(sim_parameter_dic, json_file)