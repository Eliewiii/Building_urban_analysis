"""
Contains paths to files necessary for the simulation
"""
import os

from utils.utils_default_values_user_parameters import default_path_weather_file

# EnergyPlus

# Elie

path_ep = r"C:\EnergyPlusV23-2-0\energyplus.exe"  # TODO @Ale, add the path to your version of EnergyPlus
path_simulation_parameter = r"C:\Users\eliem\AppData\Local\Building_urban_analysis\Scripts\long_wave_radiation_coupling\Ale\data\simulation_parameters.json"

path_hbjson_file_onebuildingonly = "C:\\Users\\alejandro.s\\AppData\\Local\\Building_urban_analysis\\Scripts\\long_wave_radiation_coupling\\Ale\\data\\model_no_shade_win_not_el.hbjson"
path_hbjson_file_twobuildingsfirst = r"C:\Users\eliem\OneDrive - Technion\BUA\LWR\Experiments\Samples\Cubes\building_1.hbjson"
path_hbjson_file_twobuildingssecond = r"C:\Users\eliem\OneDrive - Technion\BUA\LWR\Experiments\Samples\Cubes\building_2.hbjson"
path_hbjson_file_twobuildingsthird = r"C:\Users\eliem\OneDrive - Technion\BUA\LWR\Experiments\Samples\Cubes\building_3.hbjson"

path_fmu_conversion_dot_py = r"C:\Users\eliem\Documents\Technion\EnergyPlusToFMU-v3.1.0\Scripts\EnergyPlusToFMU.py"
path_idd = r"C:\EnergyPlusV23-2-0\Energy+.idd"
fmi_version = 2

path_temp_dir = r"C:\Users\eliem\Documents\Technion\Temp"

path_to_fmus = os.path.join(path_temp_dir, 'fmus')
path_to_run_temp_fmus = os.path.join(path_temp_dir, 'run_fmu')

# # Ale

# path_ep = "C:\\EnergyPlusV23-1-0\\energyplus.exe"  # TODO @Ale, add the path to your version of EnergyPlus

# Simulation parameters
# path_simulation_parameter = "C:\\Users\\alejandro.s\\AppData\\Local\\Building_urban_analysis\\Scripts\\long_wave_radiation_coupling\\Ale\\data\\simulation_parameters.json"

## hbjson model ##
# path_hbjson_file_onebuildingonly = "C:\\Users\\alejandro.s\\AppData\\Local\\Building_urban_analysis\\Scripts\\long_wave_radiation_coupling\\Ale\\data\\model_no_shade_win_not_el.hbjson"
# path_hbjson_file_twobuildingsfirst = "C:\\Users\\alejandro.s\\Documents\\Create_input_model\\models\\model_1.hbjson"
# path_hbjson_file_twobuildingssecond = "C:\\Users\\alejandro.s\\Documents\\Create_input_model\\models\\model_2.hbjson"


# epw file
path_epw_file = default_path_weather_file

"""  Values Elie
# EnergyPlus
path_ep = "C:\\EnergyPlusV22-2-0\\energyplus.exe"  # TODO @Ale, add the path to your version of EnergyPlus
# Simulation parameters
path_simulation_parameter = "D:\\Elie\\PhD\\Simulation\\Input_Data\\Simulation_parameters\\sim_par_basic.json"  # TODO @Ale, add the path to your simulation parameter file

# hbjson model
path_hbjson_file = "C:\\Users\\elie-medioni\\OneDrive\\OneDrive - Technion\\BUA\\Hilany\\Samples\\model_no_shade_win_not_el.hbjson"  # TODO @Ale, add the path to your hbjson model

# epw file
path_epw_file = default_path_weather_file

"""
