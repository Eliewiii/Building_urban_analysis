try:
    from ladybug_geometry.geometry3d.plane import Plane
    from ladybug_geometry.geometry3d.face import Face3D
    from ladybug_geometry.geometry3d.mesh import Mesh3D
    from ladybug_geometry.geometry3d.pointvector import Vector3D
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

from honeybee.boundarycondition import Outdoors

try:  # import the core honeybee dependencies
    from honeybee.typing import clean_and_id_rad_string, clean_rad_string
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the honeybee-radiance dependencies
    from honeybee_radiance.sensorgrid import SensorGrid
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_radiance:\n\t{}'.format(e))

def hb_roof_to_hb_SensorGrid(_name_,_model,_grid_size,_offset_dist_,quad_only):
    " Creqte a HoneyBee SensorGrid from a HoneyBe model and add it to the model"

    name = clean_and_id_rad_string('SensorGrid') if _name_ is None else _name_

    geometry=[]
    for face in _model.faces:
        if isinstance(face.boundary_condition, Outdoors)  and face.normal == Vector3D(0,0,1):
            geometry.append(face.geometry)


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

    return sensorgrid

