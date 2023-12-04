# Import the load function (load_fmu)
from pyfmi import load_fmu
from pyfmi.master import Master


from honeybee.model import Model
from honeybee.boundarycondition import Outdoors
from numpy.random import normal



# from pyfmi.fmi_algorithm_drivers import FMICSAlgOptions


# final_time = int(86400 * 5)
# FMICSAlgOptions(ncp=final_time / (10 * 60))


def get_name_of_outdoor_bc_faces(path_hbjson_file):
    """ """
    hb_model_obj = Model.from_hbjson(path_hbjson_file)

    face_name_list=[]

    for room in hb_model_obj.rooms:
        for face in room.faces:
            if isinstance(face.boundary_condition,Outdoors):
                face_name_list.append(face.identifier)
    
    return face_name_list


# Final time of the simulatio, needs to be in seconds (and a multiple of EP possible time step a priori but not sure)
final_time = int(86400 * 5)

model1_path = 'C:\\Users\\alejandro.s\\Documents\\two_building_eplus_fmus\\model_1\\fmu_creation\\in.fmu'
model2_path = 'C:\\Users\\alejandro.s\\Documents\\two_building_eplus_fmus\\model_2\\fmu_creation\\in.fmu'

#Load the FMU
model1 = load_fmu(model1_path)
model2 = load_fmu(model2_path)

with open('C:\\Users\\alejandro.s\\Documents\\two_building_eplus_fmus\\model_1\\idf_creation\\face_names.txt', 'r') as file:
    surfaces_model1 = file.readlines()[0].split('_____')
with open('C:\\Users\\alejandro.s\\Documents\\two_building_eplus_fmus\\model_2\\idf_creation\\face_names.txt', 'r') as file:
    surfaces_model2 = file.readlines()[0].split('_____')

# res = model1.simulate(final_time=86400*5)
# print(res)

models = [model1, model2]

step_size = 10 * 60
start_time = 0
end_time = final_time
for m in models:
    print(m.get_output_list(), len(m.get_output_list()))
    print(m.get_input_list(), len(m.get_input_list()))
    print('*'*300)
    # m.instantiate() # ncp=final_time / (10 * 60)
    m.setup_experiment(start_time=start_time, stop_time=end_time)  # todo : @Ale what is the difference between the 2 ?
    m.initialize(start_time, end_time)


time_values = []
output_values = {}  # Dictionary to store output variables

# todo @Ale : what is this part doing? compare to the other one below ?

# model1.instantiate()
c = start_time
m = model1
while c < final_time:
    # print(f'c == {c}')
    # for m in models:
    # opts = m.simulate_options()
    # opts['ncp'] = final_time / step_size
    status = m.do_step(current_t=c, step_size=step_size, new_step=True)
    # print(f'status is {status}') # Get time

    # time_values.append(c)

    try: # status == fmi_ok:
        act_t = {str(ov): m.get(str(ov))[0] for ov in m.get_output_list()}
        v_new = act_t.copy()

        for iv, vnewkey in zip(m.get_input_list(), v_new.keys()):
            m.set(iv, v_new[vnewkey]) # + normal(0, 5))
            # print(f'set {iv} to value {v_new[vnewkey] + normal(0, 5)}')
    except:
        print('error')
        print('fhdsjk')
        
    c += step_size
    # print('&'*10)


connections = []
for m1_surf, m2_surf in zip(surfaces_model1, surfaces_model2):
    connections.append((model1, m1_surf.replace('.', '_') + '_Surface_Outside_Face_Temperature', model2, m1_surf.replace('.', '__') + '_Surface_Outside_Face_Temperature'))
    connections.append((model2, m2_surf.replace('.', '_') + '_Surface_Outside_Face_Temperature', model1, m2_surf.replace('.', '__') + '_Surface_Outside_Face_Temperature'))

# connections = [
#     (model1, f'Surface Outside Face Temperature', model2, f'Surface Outside Face Temperature'),
#     (model2, f'Surface Outside Face Temperature', model1, f'Surface Outside Face Temperature')
# ]

coupled_simulation = Master(models, connections)

# SET ENERGYPLUS TO THE PATH VARIABLE!!!! reg add "HKCU\Environment" /v Path /t REG_EXPAND_SZ /d "%PATH%;C:\EnergyPlusV23-1-0" /f

for m in models:
    m.simulate_options()['ncp'] = final_time / (10 * 60)

opts = coupled_simulation.simulate_options()
# opts['ncp'] = final_time / (10 * 60)
# opts['step_size'] = 0.01
# opts['linear_correction'] = False
# opts['final_time'] = 

res = coupled_simulation.simulate(final_time=final_time, options=opts)


print('Finished')



