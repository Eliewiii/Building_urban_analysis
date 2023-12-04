from sys import path
import os
from pyfmi import load_fmu

# from pyfmi.master import Master

path_to_script_folder = r"C:\Users\eliem\AppData\Local\Building_urban_analysis\Scripts"  # Elie

path.append(path_to_script_folder)

from paths_to_files import path_to_run_temp_fmus
from main_convert_hbjson_to_fmu_elie import clean_directory

from honeybee.model import Model
from honeybee.boundarycondition import Outdoors
from numpy.random import normal

# Path to the FMU
model1_path = r"C:\Users\eliem\Documents\Technion\Temp\fmus\building_1\fmu_creation\in.fmu"
model2_path = r"C:\Users\eliem\Documents\Technion\Temp\fmus\building_2\fmu_creation\in.fmu"

# Load the FMU
model1 = load_fmu(model1_path)
model2 = load_fmu(model2_path)

models = [model1, model2]

# Final time of the simulatio, needs to be in seconds (and a multiple of EP possible time step a priori but not sure)
final_time = int(86400 * 5)

step_size = 10 * 60
start_time = 0
end_time = final_time

clean_directory(path_to_run_temp_fmus)

# Print Inputs and Outputs
for i, m in enumerate(models):
    path_to_run_temp_fmu = os.path.join(path_to_run_temp_fmus, f"fmu_{i}")
    clean_directory(path_to_run_temp_fmu)
    os.chdir(path_to_run_temp_fmu)
    
    outputs = m.get_output_list()
    inputs = m.get_input_list()
    # print(m.get_output_list(), len(m.get_output_list()))
    # print(m.get_input_list(), len(m.get_input_list()))
    print('*' * 300)
    m.instantiate()  # ncp=final_time / (10 * 60)
    m.setup_experiment(start_time=start_time, stop_time=end_time)  # todo : @Ale what is the difference between the 2 ?
    m.initialize(start_time, end_time)
