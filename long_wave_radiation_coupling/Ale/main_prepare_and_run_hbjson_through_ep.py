"""
Simulation flow to run EnergyPlus simulation on a hbjson model
"""

from long_wave_radiation_coupling.Ale.util_functions.prepare_hb_model_for_ep_simulation import \
    from_hbjson_to_idf
from long_wave_radiation_coupling.Ale.paths_to_files import path_ep, path_simulation_parameter, \
    path_hbjson_file, path_epw_file
from long_wave_radiation_coupling.Ale.util_functions.simulaton_ep import run_idf_windows_modified

# dir_to_write_idf_in = "C:\\Users\\elie-medioni\\OneDrive\\OneDrive - Technion\\BUA\\test_elie"  # Elie

dir_to_write_idf_in = r"C:\Users\eliem\Documents\Technion\zob"

path_hbjson_file = r"C:\Users\eliem\OneDrive - Technion\Ministry of Energy Research\Papers\CheckContext\CheckContext_2023_LBT\HBJSON files\Residential\Res_10-flrs_NoContext-2.hbjson"
from utils.utils_default_values_user_parameters import default_path_weather_file

path_epw_file = default_path_weather_file
path_simulation_parameter= r"C:\Users\eliem\AppData\Local\Building_urban_analysis\Scripts\long_wave_radiation_coupling\Ale\data\simulation_pararameters.json"

(path_osm, path_idf) = from_hbjson_to_idf(dir_to_write_idf_in, path_hbjson_file, path_epw_file,
                                          path_simulation_parameter)

# directory = run_idf_windows_modified(path_idf, epw_file_path=path_epw_file, expand_objects=True,
#                              silent=False, path_energyplus_exe=path_ep)
