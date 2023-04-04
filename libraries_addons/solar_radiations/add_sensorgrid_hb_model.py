try:
    from ladybug_geometry.geometry3d.plane import Plane
    from ladybug_geometry.geometry3d.face import Face3D
    from ladybug_geometry.geometry3d.mesh import Mesh3D
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

from honeybee.boundarycondition import Outdoors
from honeybee.facetype import Wall, RoofCeiling

try:  # import the core honeybee dependencies
    from honeybee.typing import clean_and_id_rad_string, clean_rad_string
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the honeybee-radiance dependencies
    from honeybee_radiance.sensorgrid import SensorGrid
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_radiance:\n\t{}'.format(e))

try:  # import core honeybee dependencies
    from honeybee.model import Model
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))


def is_exterior_wall(face):
    """Check if the face is an exterior wall"""
    isinstance(face.type, Wall) and isinstance(face.boundary_condition, Outdoors)

def is_roof(face):
    """Check if the face is a roof"""
    isinstance(face.type, RoofCeiling) and isinstance(face.boundary_condition, Outdoors)

def get_hb_faces_facades(model):
    """Get the HB faces of the facades and the roof of our HB model"""
    faces_facades = []
    for face in model.faces:
        if is_exterior_wall(face):
            faces_facades.append(face.punched_geometry)
    return faces_facades

def get_hb_faces_roof(model):
    """Get the HB faces of the roof of our HB model"""
    faces_roof = []
    for face in model.faces:
        if is_roof(face):
            faces_roof.append(face.punched_geometry)
    return faces_roof

def get_lb_mesh(faces, grid_size, offset_dist):
    """Create a Mesh3D from a list of HB faces"""
    lb_meshes = []
    for face in faces:
        try:
            lb_meshes.append(face.mesh_grid(grid_size, offset=offset_dist))
        except AssertionError:  # tiny geometry not compatible with quad faces
            continue
    if len(lb_meshes) == 0:
        lb_mesh = None
    elif len(lb_meshes) == 1:
        lb_mesh = lb_meshes[0]
    elif len(lb_meshes) > 1:
        lb_mesh = Mesh3D.join_meshes(lb_meshes)
    return lb_mesh

def add_sensor_grid_to_hb_model(name, model, mesh):
    name = clean_and_id_rad_string('SensorGrid') if name is None else name
    id = clean_rad_string(name) if '/' not in name else clean_rad_string(name.split('/')[0])
    sensor_grid = SensorGrid.from_mesh3d(id, mesh model_sensor_grid = model.duplicate()
def add_sensorgrid_to_hb_model(_name_,_model,_grid_size,_offset_dist_,on_facades = True, on_roof = True):
    """Create a HoneyBee SensorGrid from a HoneyBe model and add it to the model"""

    assert isinstance(_model, Model), \
        'Expected Honeybee Model. Got {}.'.format(type(_model))

    if on_facades:
        faces_facades = get_hb_faces_facades(_model)
        mesh_facades = get_lb_mesh(faces_facades)
        id = clean_rad_string(name) if '/' not in name else clean_rad_string(name.split('/')[0])
        sensor_grid_facades = SensorGrid.from_mesh3d(id, mesh_facades)
        model_sensor_grid_facades = _model.duplicate()  # duplicate to avoid editing the input
        if len(sensor_grid_facades) != 0:
            model_sensor_grid_facades.properties.radiance.add_sensor_grid(sensor_grid_facades)

    if on_roof:
        faces_roof = get_hb_faces_roof(_model)
        mesh_roof = get_lb_mesh(faces_roof)
        id = clean_rad_string(name) if '/' not in name else clean_rad_string(name.split('/')[0])
        sensor_grid_roof = SensorGrid.from_mesh3d(id, mesh_roof)
        model_sensor_grid_roof = _model.duplicate()  # duplicate to avoid editing the input
        if len(sensor_grid_roof) != 0:
            model_sensor_grid_roof.properties.radiance.add_sensor_grid(sensor_grid_roof)





    return model_sensorgrid_facades

