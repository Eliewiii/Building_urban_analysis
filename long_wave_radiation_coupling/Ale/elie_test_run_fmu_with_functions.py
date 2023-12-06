from sys import path
import os
from pyfmi import load_fmu
import shutil

# from pyfmi.master import Master

path_to_script_folder = r"C:\Users\eliem\AppData\Local\Building_urban_analysis\Scripts"  # Elie

path.append(path_to_script_folder)

from paths_to_files import path_to_run_temp_fmus, path_ep_folder, path_temp_dir

from long_wave_radiation_coupling.utils_run_co_sim import initialize_models

from utils.utils_file_folder_functions import clean_directory

# Create a folder to run the FMUs in, if it already exists, delete it and create a new one
clean_directory(path_to_run_temp_fmus)
# Change the working directory to the temporary directory
os.chdir(path_to_run_temp_fmus)
""" Some files are genereated in the working directory, it is necessary to change the working directory 
to a temporary one """

# Path to the FMU
model1_path = r"C:\Users\eliem\Documents\Technion\Temp\fmus\building_1\fmu_creation\in.fmu"
model2_path = r"C:\Users\eliem\Documents\Technion\Temp\fmus\building_2\fmu_creation\in.fmu"
model3_path = r"C:\Users\eliem\Documents\Technion\Temp\fmus\building_3\fmu_creation\in.fmu"

# Load the FMU
model1 = load_fmu(model1_path)
model2 = load_fmu(model2_path)
model3 = load_fmu(model3_path)

model_list = [model1, model2, model3]

# Final time of the simulatio, needs to be in seconds (and a multiple of EP possible time step a priori but not sure)
final_time = int(60 * 60 * 24 * 15)  # 5 days
step_size = 10 * 60  # 10 minutes
nb_step = int(final_time / step_size)
start_time = 0
end_time = final_time

# Add the directory of EnergyPlus to the PATH variable temporarily
"""
The following code adds the directory of EnergyPlus to the PATH variable temporarily, execute the code that needs
EnergyPlus and then remove the directory from the PATH variable.
"""
# Get the current PATH variable and make a copy
original_path = os.environ.get('PATH', '')
original_path_copy = original_path
# Remove existing energyplus directories from PATH if present
existing_energyplus_dirs = [dir_path for dir_path in original_path.split(os.pathsep) if
                            'energyplus' in dir_path.lower()]
for existing_dir in existing_energyplus_dirs:
    original_path_copy = original_path_copy.replace(existing_dir + os.pathsep, '')  # Remove directory and separator

try:
    # Append the EnergyPlus directory to the PATH using os.pathsep
    os.environ['PATH'] = f'{original_path}{os.pathsep}{path_ep_folder}'

    path_to_run_temp_fmu_list = [os.path.join(path_to_run_temp_fmus, f"run_fmu_{i}") for i, model in
                                 enumerate(model_list)]

    """ Code that needs using EnergyPlus """
    # Initialize models

    initialize_models(model_list=model_list, path_to_run_temp_fmu_list=path_to_run_temp_fmu_list, start_time=start_time,
                      end_time=end_time)

    """ Seems like the programs stops after initialization if there is nothing that comes after, it creates an error """
    os.chdir(path_to_run_temp_fmus)

    # Run the simulation
    for step_index in range(0, nb_step):
        time = step_index * step_size
        for i, m in enumerate(model_list):
            m.do_step(current_t=time, step_size=step_size)

    for count, model in enumerate(model_list):
        m.terminate()

    os.chdir(path_to_run_temp_fmus)

# shows the error if an error occurred
except Exception as e:
    # Handle exceptions if needed
    print(f"An error occurred: {e}")

# Execute this code regardless and change back the PATH variable to its original state
finally:
    # Revert the PATH to its original state, even if an error occurred
    os.environ['PATH'] = original_path
    print(os.environ['PATH'])
