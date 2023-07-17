import os
from honeybee_energy import run


def from_hbjson_to_idf(dir_to_write_idf_in, hbjson_file_path, epw_file_path, simulation_parameter_file_path):
    """

    """
    osw = run.to_openstudio_osw(osw_directory=dir_to_write_idf_in,
                                model_path=hbjson_file_path,
                                sim_par_json_path=simulation_parameter_file_path,
                                epw_file=epw_file_path)
    ## Run simulation in OpenStudio to generate IDF ##
    (path_osm, path_idf) = run.run_osw(osw, silent=False)
