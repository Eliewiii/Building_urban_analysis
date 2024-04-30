# Import the load function (load_fmu)
import pandas as pd
from pyfmi import load_fmu
from pyfmi.master import Master

from honeybee.model import Model
from honeybee.boundarycondition import Outdoors
from numpy.random import normal
from utils.utils_file_folder_functions import clean_directory


# from pyfmi.fmi_algorithm_drivers import FMICSAlgOptions


# final_time = int(86400 * 5)
# FMICSAlgOptions(ncp=final_time / (10 * 60))


def get_name_of_outdoor_bc_faces(path_hbjson_file):
    """ """
    hb_model_obj = Model.from_hbjson(path_hbjson_file)

    face_name_list = []

    for room in hb_model_obj.rooms:
        for face in room.faces:
            if isinstance(face.boundary_condition, Outdoors):
                face_name_list.append(face.identifier)

    return face_name_list


# Final time of the simulation, needs to be in seconds (and a multiple of EP possible time step a priori but not sure)
final_time = int(86400 * 30)

model1_path = "C:\\Users\\alejandro\\Documents\\fmus\\building_1\\fmu_creation\\in.fmu"
model2_path = "C:\\Users\\alejandro\\Documents\\fmus\\building_2\\fmu_creation\\in.fmu"
model3_path = "C:\\Users\\alejandro\\Documents\\fmus\\building_3\\fmu_creation\\in.fmu"

def load_models(model_path_list):
    return {mp: load_fmu(mp) for mp in model_path_list}

def create_full_connections(models_dict):
    # {k: set([l[0] for l in v.get_input_list().items()]) for k, v in models_dict.items()}
    res = []
    conns = []
    for k, v in models_dict.items():
        res = res + [{'model': k, 'I/O Name': l[0], 'I/O type': 'output'} for l in v.get_output_list().items()]
        res = res + [{'model': k, 'I/O Name': l[0], 'I/O type': 'input'} for l in v.get_input_list().items()]
        conns.extend([(i[1], i[0], o[1], o[0]) for i, o in zip(v.get_input_list().items(), v.get_output_list().items())])
        # res.append({'model': k, 'I/O Name': l[0], 'I/O type': 'input'} for l in v.get_input_list().items())
    return pd.DataFrame(res), conns


def connection_tuples(df, models_dict):
    # for m_name in df.model.unique():
    connections = []
    for var_name in df['I/O Name'].unique():
        connections.append((
            models_dict[df.loc[((df['I/O Name'] == var_name) & (df['I/O type'] == 'output')), 'model'].iloc[0]],
            var_name,
            models_dict[df.loc[((df['I/O Name'] == var_name) & (df['I/O type'] == 'input')), 'model'].iloc[0]],
            var_name
        ))
        # df[((df.model == m_name) & (df['I/O type'] == 'input')), 'I/O name']
        # (df[((df['I/O name'] == m_input) & (df['I/O type'] == 'output')), 'model'], m_input)

        # connections.append((model1, m1_surf.replace('.', '_') + '_Surface_Outside_Face_Temperature', model2,
        #                     m1_surf.replace('.', '__') + '_Surface_Outside_Face_Temperature'))

    return connections

# # Load the FMU
# model1 = load_fmu(model1_path)
# model2 = load_fmu(model2_path)

import os

models_dict = load_models([model1_path, model2_path, model3_path])
connections_df, connections = create_full_connections(models_dict)
# connections = connection_tuples(connections_df, models_dict)
models = list(models_dict.values())

""" Code that needs using EnergyPlus """
# Print Inputs and Outputs an initialize the models
for i, m in enumerate(models):
    # Create a temporary directory to run the FMU in the directory of the FMU
    path_to_run_temp_fmu = os.path.join(r'C:\Users\alejandro\AppData\Local\Building_urban_analysis\Scripts\long_wave_radiation_coupling\Ale\outputs_cosim', f"fmu_{i}")
    clean_directory(path_to_run_temp_fmu)
    # Change the working directory to the temporary directory
    """ The change of directory is necessary because otherwise it will write the resulst file in the current
     directory, it is not possible to simulate 2 FMUs in the same directory at the same time as the results files
      have the same name and it will generate an error."""
    os.chdir(path_to_run_temp_fmu)

    # Collect the inputs and outputs of the FMU, todo: @Elie, just to check.
    outputs = m.get_output_list()
    inputs = m.get_input_list()
    print('*' * 300)
    m.instantiate(visible=True)
    # m.setup_experiment(start_time=start_time,
    #                    stop_time=end_time)

    # m.initialize()

""" Seems like the programs stops after initialization if there is nothing that comes after, it creates an error """
os.chdir(r'C:\Users\alejandro\AppData\Local\Building_urban_analysis\Scripts\long_wave_radiation_coupling\Ale')

coupled_simulation = Master(models, connections)

# path_ep_folder = r"C:\EnergyPlusV23-2-0"
# # Get the current PATH variable and make a copy
# original_path = os.environ.get('PATH', '')
# original_path_copy = original_path
# # Remove existing energyplus directories from PATH if present
# existing_energyplus_dirs = [dir_path for dir_path in original_path.split(os.pathsep) if
#                             'energyplus' in dir_path.lower()]
# for existing_dir in existing_energyplus_dirs:
#     original_path_copy = original_path_copy.replace(existing_dir + os.pathsep, '')  # Remove directory and separator
#
#     # Append the EnergyPlus directory to the PATH using os.pathsep
#     os.environ['PATH'] = f'{original_path}{os.pathsep}{path_ep_folder}'

os.environ['PATH'] = f"{os.environ['PATH']};C:\EnergyPlusV23-2-0"
# SET ENERGYPLUS TO THE PATH VARIABLE!!!! reg add "HKCU\Environment" /v Path /t REG_EXPAND_SZ /d "%PATH%;C:\EnergyPlusV23-1-0" /f
for m in models:
    m.simulate_options()['ncp'] = final_time / (10 * 60)
    # m.simulate_options()['CommunicationStepSize'] = final_time / (10 * 60)

opts = coupled_simulation.simulate_options()
# opts['ncp'] = final_time / (10 * 60)
# opts['step_size'] = 0.01
# opts['linear_correction'] = False
# opts['final_time'] =
opts['step_size'] = 10*60

res = coupled_simulation.simulate(final_time=final_time, options=opts)

print('Finished')


import sqlite3
import pandas as pd


db = sqlite3.connect(r"C:\Users\alejandro\AppData\Local\Building_urban_analysis\Scripts\long_wave_radiation_coupling\Ale\outputs_cosim\fmu_2\Output_EPExport_Model\in.sql")

rrr = pd.read_sql("select name, tbl_name from sqlite_master where type='table';", db)

print(rrr)

print(pd.read_sql("select * from ReportVariableDataDictionary;", db))

print(pd.read_sql("select distinct VariableValue from ReportVariableData where ReportVariableDataDictionaryIndex >= 203 and ReportVariableDataDictionaryIndex <= 212;", db))

print(pd.read_sql("select distinct Value from ReportData where ReportDataDictionaryIndex >= 203 and ReportDataDictionaryIndex <= 212;", db))

exit()
