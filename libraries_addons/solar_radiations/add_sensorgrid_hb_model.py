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


def is_facade(face):
    """Check if the face is an exterior wall"""
    return (isinstance(face.type, Wall) and isinstance(face.boundary_condition, Outdoors))


def is_roof(face):
    """Check if the face is a roof"""
    return (isinstance(face.type, RoofCeiling) and isinstance(face.boundary_condition, Outdoors))


def get_hb_faces_facades(model):
    """Get the HB faces of the facades of our HB model"""
    faces_facades = []
    for face in model.faces:
        if is_facade(face):
            faces_facades.append(face.punched_geometry)
    return faces_facades


def get_hb_faces_roof(model):
    """Get the HB faces of the roof of our HB model"""
    faces_roof = []
    for face in model.faces:
        if is_roof(face):
            faces_roof.append(face.punched_geometry)
    return faces_roof


def get_hb_faces(model):
    """Get the HB faces of the roof and the facades of our HB model"""
    faces = []
    for face in model.faces:
        if is_roof(face) or is_facade(face):
            faces.append(face.punched_geometry)
    return faces


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
    else:  # which means : len(lb_meshes) > 1:
        lb_mesh = Mesh3D.join_meshes(lb_meshes)
    return lb_mesh


def create_sensor_grid_from_mesh(mesh, name=None):
    """Create a HB SensorGrid and add it to a HB model"""
    name = clean_and_id_rad_string('SensorGrid') if name is None else name
    id = clean_rad_string(name) if '/' not in name else clean_rad_string(name.split('/')[0])
    sensor_grid = SensorGrid.from_mesh3d(id, mesh)
    return sensor_grid
