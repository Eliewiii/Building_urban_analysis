try:
    from ladybug_geometry.geometry3d.plane import Plane
    from ladybug_geometry.geometry3d.face import Face3D
    from ladybug_geometry.geometry3d.mesh import Mesh3D
    from ladybug_geometry.geometry2d.mesh import Mesh2D
    from ladybug_geometry.geometry2d.polygon import Polygon2D
    from ladybug_geometry.geometry2d.pointvector import Vector2D
    from ladybug_geometry.geometry2d.ray import Ray2D
    from ladybug_geometry.intersection2d import does_intersection_exist_line2d
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

from honeybee.boundarycondition import Outdoors
from honeybee.facetype import Wall, RoofCeiling
from honeybee.aperture import Aperture

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


def check_number_mesh_grid_BUA(input, name):
    assert isinstance(input, (float, int)), '{} for Face3D.get_mesh_grid' \
                                            ' must be a number. Got {}.'.format(name, type(input))


def is_point_inside_BUA(polygon_face, point, test_vector=Vector2D(1, 0.00001)):
    """Test whether a Point2D lies inside or outside the polygon.


    Args:
        point: A Point2D for which the inside/outside relationship will be tested.
        test_vector: Optional vector to set the direction in which intersections
            with the polygon edges will be evaluated to determine if the
            point is inside. Default is a slight variation of the X-unit
            vector with a low probability of encountering the unsupported
            fringe cases.

    Returns:
        A boolean denoting whether the point lies inside (True) or outside (False).
    """
    test_ray = Ray2D(point, test_vector)
    n_int = 0
    for _s in polygon_face.segments:
        if does_intersection_exist_line2d(_s, test_ray):
            n_int += 1
    if n_int % 2 == 0:
        return False
    return True


def add_bools(a, b):
    if a and b:
        return True
    elif (a and not b) or (b and not a):
        return False
    else:
        return False


def add_list_bools(list_a, list_b):
    if list_a == []:
        return list_b
    elif list_b == []:
        return list_a
    else:
        list = []
        for i in range(0, len(list_a)):
            list.append(add_bools(list_a[i], list_b[i]))
        return list


def from_polygon_grid_BUA(face, x_dim, y_dim, generate_centroids=True):
    """Initialize a gridded Mesh2D from a Polygon2D.

    Note that this gridded mesh will usually not completely fill the polygon.
    Essentially, this method generates a grid over the domain of the polygon
    and then removes any points that do not lie within the polygon.

    Args:
        polygon: A Polygon2D object.
        x_dim: The x dimension of the grid cells as a number.
        y_dim: The y dimension of the grid cells as a number.
        generate_centroids: Set to True to have the face centroids generated
            alongside the grid of vertices, which is much faster than having
            them generated upon request as they typically are. However, if you
            have no need for the face centroids, you would save memory by setting
            this to False. Default is True.
    """

    polygon_face = face.polygon2d

    assert isinstance(polygon_face, Polygon2D), 'Expected Polygon2D for' \
                                                ' Mesh2D.from_polygon_grid. Got {}'.format(type(polygon_face))

    # figure out how many x and y cells to make
    _x_dim, _num_x = Mesh2D._domain_dimensions(polygon_face.max.x - polygon_face.min.x, x_dim)
    _y_dim, _num_y = Mesh2D._domain_dimensions(polygon_face.max.y - polygon_face.min.y, y_dim)
    _poly_min = polygon_face.min

    # generate the gid of points and faces
    _verts = Mesh2D._grid_vertices(_poly_min, _num_x, _num_y, _x_dim, _y_dim)
    _faces = Mesh2D._grid_faces(_num_x, _num_y)
    _centroids = None
    if generate_centroids is True:  # calculate centroids if requested
        _centroids = Mesh2D._grid_centroids(
            _poly_min, _num_x, _num_y, _x_dim, _y_dim)

    # figure out which vertices lie inside the polygon
    # for tolerance reasons, we scale the polygon by a very small amount
    # this avoids the fringe cases noted in the Polygon2d.is_point_inside description
    tol_pt = Vector2D(0.0000001, 0.0000001)

    scaled_poly = Polygon2D(
        tuple(pt.scale(1.000001, _poly_min) - tol_pt for pt in polygon_face.vertices))

    _pattern = [scaled_poly.is_point_inside(_v) for _v in _verts]
    print(_pattern)

    if face.has_holes:
        for polygon_hole in face.hole_polygon2d:
            # figure out how many x and y cells to make
            for vert in _verts:
                if polygon_hole.is_point_inside(vert) or polygon_hole.is_point_on_edge(vert, 0.5):
                    _pattern[_verts.index(vert)] = False

    print(_pattern)
    # build the mesh
    _mesh_init = Mesh2D(_verts, _faces)
    _mesh_init._face_centroids = _centroids
    _new_mesh, _face_pattern = _mesh_init.remove_vertices(_pattern)
    _new_mesh._face_areas = x_dim * y_dim
    return _new_mesh


def mesh_grid_BUA(face, x_dim, y_dim=None, offset=None, flip=False, generate_centroids=True):
    """Get a gridded Mesh3D over this face.

    This method generates a mesh grid over the domain of the face
    and then removes any vertices that do not lie within it.

    Note that the x_dim and y_dim refer to dimensions within the X and Y
    coordinate system of this faces's plane. So rotating this plane will
    result in rotated grid cells.

    Args:
        x_dim: The x dimension of the grid cells as a number.
        y_dim: The y dimension of the grid cells as a number. Default is None,
            which will assume the same cell dimension for y as is set for x.
        offset: A number for how far to offset the grid from the base face.
                Default is None, which will not offset the grid at all.
        flip: Set to True to have the mesh normals reversed from the direction
                of this face and to have the offset input move the mesh in the
                opposite direction from this face's normal.
         generate_centroids: Set to True to have the face centroids generated
                alongside the grid of vertices, which is much faster than having
                them generated upon request as they typically are. However, if you
                have no need for the face centroids, you would save time and memory
                by setting this to False. Default is True.
        """
    # check the inputs and set defaults
    check_number_mesh_grid_BUA(x_dim, 'x_dim')
    if y_dim is not None:
        check_number_mesh_grid_BUA(y_dim, 'y_dim')
    else:
        y_dim = x_dim
    if offset is not None:
        check_number_mesh_grid_BUA(offset, 'offset')

    # generate the mesh grid and convert it to a 3D mesh
    grid_mesh2d = from_polygon_grid_BUA(
        face, x_dim, y_dim, generate_centroids)
    if offset is None or offset == 0:
        vert_3d = tuple(face.plane.xy_to_xyz(pt)
                        for pt in grid_mesh2d.vertices)
    else:
        _off_num = -1 * offset if flip is True else offset
        _off_plane = face.plane.move(face.plane.n * _off_num)
        vert_3d = tuple(_off_plane.xy_to_xyz(pt)
                        for pt in grid_mesh2d.vertices)
    grid_mesh3d = Mesh3D(vert_3d, grid_mesh2d.faces)
    grid_mesh3d._face_areas = grid_mesh2d.face_areas

    # assign the face plane normal to the mesh normals
    if flip is True:
        grid_mesh3d._face_normals = face.plane.n.reverse()
        grid_mesh3d._vertex_normals = face.plane.n.reverse()
        grid_mesh3d._faces = tuple(
            tuple(reversed(face)) for face in grid_mesh3d.faces)  # right-hand rule
    else:
        grid_mesh3d._face_normals = face.plane.n
        grid_mesh3d._vertex_normals = face.plane.n

    # transform the centroids to 3D space if they were generated
    if generate_centroids is True:
        _conv_plane = face.plane if offset is None or offset == 0 else _off_plane
        grid_mesh3d._face_centroids = tuple(_conv_plane.xy_to_xyz(pt)
                                            for pt in grid_mesh2d.face_centroids)

    return grid_mesh3d


def get_lb_mesh(faces, grid_size, offset_dist):
    """Create a Mesh3D from a list of HB faces"""
    lb_meshes = []
    for face in faces:
        try:
            lb_meshes.append(mesh_grid_BUA(face, grid_size, offset=offset_dist))
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
