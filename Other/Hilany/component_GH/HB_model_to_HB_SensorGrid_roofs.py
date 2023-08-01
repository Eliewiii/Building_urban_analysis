try:
    from ladybug_geometry.geometry3d.plane import Plane
    from ladybug_geometry.geometry3d.face import Face3D
    from ladybug_geometry.geometry3d.mesh import Mesh3D
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

from honeybee.boundarycondition import Outdoors
from honeybee.facetype import RoofCeiling

try:  # import the core honeybee dependencies
    from honeybee.typing import clean_and_id_rad_string, clean_rad_string
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the honeybee-radiance dependencies
    from honeybee_radiance.sensorgrid import SensorGrid
    from honeybee_radiance.properties.model import ModelRadianceProperties
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_radiance:\n\t{}'.format(e))

try:  # import core honeybee dependencies
    from honeybee.model import Model
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

def hb_model_to_hb_SensorGrid_roofs(_name_,_model,_grid_size,_offset_dist_,quad_only_):
    " Create a HoneyBee SensorGrid from a HoneyBe model and add it to the model"

    assert isinstance(_model, Model), \
        'Expected Honeybee Model. Got {}.'.format(type(_model))

    name = clean_and_id_rad_string('SensorGrid') if _name_ is None else _name_

    geometry=[]
    for face in _model.faces:
        if isinstance(face.type,RoofCeiling) and isinstance(face.boundary_condition, Outdoors):
            geometry.append(face.punched_geometry)


    if quad_only_:  # use Ladybug's built-in meshing methods
        lb_meshes = []
        for geo in geometry:
            try:
                lb_meshes.append(geo.mesh_grid(_grid_size, offset=_offset_dist_))
            except AssertionError:  # tiny geometry not compatible with quad faces
                continue

    if len(lb_meshes) == 0:
        lb_mesh = None
    elif len(lb_meshes) == 1:
        lb_mesh = lb_meshes[0]
    elif len(lb_meshes) > 1:
        lb_mesh = Mesh3D.join_meshes(lb_meshes)

    # create the sensor grid object
    id = clean_rad_string(name) if '/' not in name else clean_rad_string(name.split('/')[0])
    sensorgrid = SensorGrid.from_mesh3d(id, lb_mesh)


    # create a duplicate of the model containing only the sensorgrid of the facades

    model_sensorgrid_roofs = _model.duplicate()  # duplicate to avoid editing the input
    if len(sensorgrid) != 0:
        model_sensorgrid_roofs.properties.radiance.add_sensor_grid(sensorgrid)

    return model_sensorgrid_roofs

