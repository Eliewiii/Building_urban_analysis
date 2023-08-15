# Import the load function (load_fmu)
from pyfmi import load_fmu
from pyfmi.master import Master


from honeybee.model import Model
from honeybee.boundarycondition import Outdoors

def get_name_of_outdoor_bc_faces(path_hbjson_file):
    """ """
    hb_model_obj = Model.from_hbjson(path_hbjson_file)

    face_name_list=[]

    for room in hb_model_obj.rooms:
        for face in room.faces:
            if isinstance(face.boundary_condition,Outdoors):
                face_name_list.append(face.identifier)
    
    return face_name_list


model1_path = 'C:\\Users\\alejandro.s\\Documents\\two_building_eplus_fmus\\model_1\\fmu_creation\\in.fmu'
model2_path = 'C:\\Users\\alejandro.s\\Documents\\two_building_eplus_fmus\\model_2\\fmu_creation\\in.fmu'

#Load the FMU
model1 = load_fmu(model1_path)
model2 = load_fmu(model2_path)

with open('C:\\Users\\alejandro.s\\Documents\\two_building_eplus_fmus\\model_1\\idf_creation\\face_names.txt', 'r') as file:
    surfaces_model1 = file.readlines()[0].split('_____')
with open('C:\\Users\\alejandro.s\\Documents\\two_building_eplus_fmus\\model_2\\idf_creation\\face_names.txt', 'r') as file:
    surfaces_model2 = file.readlines()[0].split('_____')

# res = model1.simulate(final_time=86400*1)
# print(res)

models = [model1, model2]

for m in models:
    print(m.get_output_list(), len(m.get_output_list()))
    print(m.get_input_list(), len(m.get_input_list()))
    print('*'*300)

connections = []
for m1_surf, m2_surf in zip(surfaces_model1, surfaces_model2):
    connections.append((model1, m1_surf + ' Surface Outside Face Temperature', model2, m2_surf + ' Surface Outside Face Temperature'))
    connections.append((model2, m2_surf + ' Surface Outside Face Temperature', model1, m1_surf + ' Surface Outside Face Temperature'))

# connections = [
#     (model1, f'Surface Outside Face Temperature', model2, f'Surface Outside Face Temperature'),
#     (model2, f'Surface Outside Face Temperature', model1, f'Surface Outside Face Temperature')
# ]

coupled_simulation = Master(models, connections)

res = coupled_simulation.simulate()


print('Finished')



