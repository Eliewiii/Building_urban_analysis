"""
Utils functions for the generation of SensorGrids objects
"""

import logging

from ladybug_geometry.geometry3d.mesh import Mesh3D
from ladybug_geometry.geometry2d.mesh import Mesh2D
from ladybug_geometry.geometry2d.polygon import Polygon2D
from ladybug_geometry.geometry2d.pointvector import Vector2D, Point2D
from ladybug_geometry.geometry2d.ray import Ray2D
from ladybug_geometry.intersection2d import does_intersection_exist_line2d
from honeybee.model import Model
from honeybee.boundarycondition import Outdoors
from honeybee.facetype import Wall, RoofCeiling
from honeybee.typing import clean_and_id_rad_string, clean_rad_string
from honeybee_radiance.sensorgrid import SensorGrid

user_logger = logging.getLogger("user")
dev_logger = logging.getLogger("dev")


def generate_sensor_grid_for_hb_model(hb_model_obj, grid_size_x, grid_size_y, offset_dist, surface_type):
    """
    Generate SensorGrid object for a Honeybee Model object on either the roof or the facades
    :param hb_model_obj: Honeybee Model object
    :param grid_size_x: float : size of the grid in the x direction in meter
    :param grid_size_y: float : size of the grid in the y direction in meter
    :param offset_dist: float : offset distance on the border of the face to generate the mesh
    :param surface_type: str : Surface type to generate the Sensorgrid on, either "roof" or "facades"

    :return sensorgrid_dict:
    """
    # not sure if necessary
    assert isinstance(hb_model_obj, Model), 'Expected Honeybee Model. Got {}.'.format(type(hb_model_obj))

    if surface_type not in ["roof", "facades"]:
        dev_logger.critical(f"the surface_type is either not specified or incorrect, please check")
    elif surface_type == "roof":
        lb_punched_face3d_list = get_hb_faces_list_according_to_type(hb_model_obj, is_roof)
    else:
        lb_punched_face3d_list = get_hb_faces_list_according_to_type(hb_model_obj, is_facade)
    # Generate the SensorGrid object
    sensor_grid_obj = generate_sensorgrid_obj_on_lb_punched_face_list(lb_punched_face3d_list, grid_size_x, grid_size_y,
                                                                      offset_dist, surface_type)

    return sensor_grid_obj.to_dict()


def generate_sensorgrid_obj_on_lb_punched_face_list(lb_punched_face3d_list, grid_size_x, grid_size_y, offset_dist,
                                                    surface_type):
    """
    Generate a SensorGrid object for a list of Honeybee Faces
    :param hb_face_list: list of LB punched geometry
    :param grid_size_x: float : size of the grid in the x direction in meter
    :param grid_size_y: float : size of the grid in the y direction in meter
    :param offset_dist: float : offset distance on the border of the face to generate the mesh
    :param surface_type: str : Surface type to generate the Sensorgrid on, either "roof" or "facades"

    :return sensor_grid_obj: Honeybee SensorGrid object
    """
    # generate Ladybug Mesh on the Honeybee Face
    lb_mesh_obj = generate_lb_mesh_from_lb_punched_face_list(lb_punched_face3d_list, grid_size_x, grid_size_y,
                                                             offset_dist, surface_type)
    # Generate a SensorGrid object out of the mesh
    sensor_grid_obj = create_sensor_grid_from_mesh(lb_mesh_obj)

    return sensor_grid_obj


def get_hb_faces_list_according_to_type(model, face_type_function):
    """Get the HB faces of the roof and the facades of our HB model
    :param model: Honeybee Model object
    :param face_type_function: function to filter the faces
    :return lb_punched_face3d_list: list of Honeybee Face3D
    """
    lb_punched_face3d_list = []
    for face in model.faces:
        if face_type_function(face):
            lb_punched_face3d_list.append(face.punched_geometry)
    return lb_punched_face3d_list


def create_sensor_grid_from_mesh(mesh, name=None):
    """Create a HB SensorGrid and add it to a HB model"""
    name = clean_and_id_rad_string('SensorGrid') if name is None else name
    id = clean_rad_string(name) if '/' not in name else clean_rad_string(name.split('/')[0])
    sensor_grid = SensorGrid.from_mesh3d(id, mesh)
    return sensor_grid


def generate_lb_mesh_from_lb_punched_face_list(lb_punched_face3d_list, grid_size_x, grid_size_y, offset_dist,
                                               surface_type):
    """
    Create a Ladybug Mesh3D from a list of LB punched geometry
    :param lb_punched_face3d_list: list of LB punched geometry
    :param grid_size_x: float : size of the grid in the x direction in meter
    :param grid_size_y: float : size of the grid in the y direction in meter
    :param offset_dist: float : offset distance on the border of the face to generate the mesh
    :param surface_type: str : Surface type to generate the Sensorgrid on, either "roof" or "facades"
    """
    # Initialize the list of Ladybug Meshes
    lb_meshes = []
    for lb_face_obj in lb_punched_face3d_list:
        try:
            new_mesh = generate_lb_mesh3d_from_hb_face(lb_face_obj, grid_size_x, grid_size_y, offset=offset_dist)
            if new_mesh is not None:
                lb_meshes.append(new_mesh)
            # lb_meshes.append(generate_lb_mesh3d_from_hb_face(lb_face_obj, grid_size_x, grid_size_y, offset=offset_dist))
        except AssertionError:  # tiny geometry not compatible with quad faces
            continue
    if len(lb_meshes) == 0:
        # todo : Correct that to continue the simulation anyway, not generating the Sensorgrid and disabling the simulation
        #  for the roof/facade for that building
        lb_mesh = None
        dev_logger.warning("No mesh was generated for the Honeybee Model")
        raise AssertionError(
            f"No mesh could be generated. It is liokely that there is not enough room in the {surface_type} to generate a mesh")
    elif len(lb_meshes) == 1:
        lb_mesh = lb_meshes[0]
    else:  # join the meshes
        lb_mesh = Mesh3D.join_meshes(lb_meshes)
    return lb_mesh


def generate_lb_mesh3d_from_hb_face(lb_punched_face3d, x_dim, y_dim=None, offset=None, flip=False,
                                    generate_centroids=True):
    """
    Function highly inspired from the in the todo @Elie, add the name of the function
     function in the original Honeybee code, modified to fit the needs of the project.

    Get a gridded Mesh3D over this lb_punched_face3d.

    This method generates a mesh grid over the domain of the lb_punched_face3d
    and then removes any vertices that do not lie within it.

    Note that the x_dim and y_dim refer to dimensions within the X and Y
    coordinate system of this hb_face_objs's plane. So rotating this plane will
    result in rotated grid cells.

    :param lb_punched_face3d: A Honeybee Face object.
    :param x_dim: The x dimension of the grid cells as a number.
    :param y_dim: The y dimension of the grid cells as a number. Default is None,
        which will assume the same cell dimension for y as is set for x.
    :param offset: A number for how far to offset the grid from the base face.
        Default is None, which will not offset the grid at all.
    :param flip: Set to True to have the mesh normals reversed from the direction
        of this face and to have the offset input move the mesh in the
        opposite direction from this face's normal.
    :param generate_centroids: Set to True to have the face centroids generated
        alongside the grid of vertices, which is much faster than having
        them generated upon request as they typically are. However, if you
        have no need for the face centroids, you would save time and memory
        by setting this to False. Default is True.

    :returns: A Honeybee Mesh3D object.
    """
    # check the inputs and set defaults
    assert isinstance(x_dim, (float, int)), '{} for Face3D.get_mesh_grid' \
                                            ' must be a number. Got {}.'.format('x_dim', type(input))
    if y_dim is not None:
        assert isinstance(y_dim, (float, int)), '{} for Face3D.get_mesh_grid' \
                                                ' must be a number. Got {}.'.format('y_dim', type(input))
    else:
        y_dim = x_dim
    if offset is not None:
        assert isinstance(offset, (float, int)), '{} for Face3D.get_mesh_grid' \
                                                 ' must be a number. Got {}.'.format('offset', type(input))

    # generate the mesh grid and convert it to a 3D mesh
    grid_mesh2d = generate_lb_mesh2d_from_lb_polygon2d(
        lb_punched_face3d, x_dim, y_dim, generate_centroids)
    # if the grid mesh is None, return None
    if grid_mesh2d is None:
        return None

    if offset is None or offset == 0:
        vert_3d = tuple(lb_punched_face3d.plane.xy_to_xyz(pt)
                        for pt in grid_mesh2d.vertices)
    else:
        _off_num = -1 * offset if flip is True else offset
        _off_plane = lb_punched_face3d.plane.move(lb_punched_face3d.plane.n * _off_num)
        vert_3d = tuple(_off_plane.xy_to_xyz(pt)
                        for pt in grid_mesh2d.vertices)
    grid_mesh3d = Mesh3D(vert_3d, grid_mesh2d.faces)
    grid_mesh3d._face_areas = grid_mesh2d.face_areas

    # assign the face plane normal to the mesh normals
    if flip is True:
        grid_mesh3d._face_normals = lb_punched_face3d.plane.n.reverse()
        grid_mesh3d._vertex_normals = lb_punched_face3d.plane.n.reverse()
        grid_mesh3d._faces = tuple(
            tuple(reversed(face)) for face in grid_mesh3d.faces)  # right-hand rule
    else:
        grid_mesh3d._face_normals = lb_punched_face3d.plane.n
        grid_mesh3d._vertex_normals = lb_punched_face3d.plane.n

    # transform the centroids to 3D space if they were generated
    if generate_centroids is True:
        _conv_plane = lb_punched_face3d.plane if offset is None or offset == 0 else _off_plane
        grid_mesh3d._face_centroids = tuple(_conv_plane.xy_to_xyz(pt)
                                            for pt in grid_mesh2d.face_centroids)

    return grid_mesh3d


def generate_lb_mesh2d_from_lb_polygon2d(polygon, x_dim, y_dim, generate_centroids=True):
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
    todo @Elie, change the name of variables and put more comments
    todo @Elie, rework on the whole structure of the function, it works but it is unclear

    Credits, Highly inspired from ladybug_geometry.geometry2d.mesh.Mesh2D.from_polygon_grid, with adjusments
    not to overlap holes/apertures/windows
    """

    polygon_face = polygon.polygon2d

    assert isinstance(polygon_face, Polygon2D), 'Expected Polygon2D for' \
                                                ' Mesh2D.from_polygon_grid. Got {}'.format(type(polygon_face))

    # figure out how many x and y cells to make
    _x_dim, _num_x = Mesh2D._domain_dimensions(polygon_face.max.x - polygon_face.min.x, x_dim)
    _y_dim, _num_y = Mesh2D._domain_dimensions(polygon_face.max.y - polygon_face.min.y, y_dim)
    _poly_min = polygon_face.min

    # generate the gid of points and faces
    _verts = Mesh2D._grid_vertices(_poly_min, _num_x, _num_y, _x_dim, _y_dim)
    _faces = Mesh2D._grid_faces(_num_x, _num_y)
    _centroids = Mesh2D._grid_centroids(_poly_min, _num_x, _num_y, _x_dim, _y_dim)

    # figure out which vertices lie inside the polygon
    # for tolerance reasons, we scale the polygon by a very small amount
    # this avoids the fringe cases noted in the Polygon2d.is_point_inside description
    tol_pt = Vector2D(0.0000001, 0.0000001)

    scaled_poly = Polygon2D(
        tuple(pt.scale(1.000001, _poly_min) - tol_pt for pt in polygon_face.vertices))

    """
    The element of the mesh that overlap with windows/holes should be removed.
    The separation of vertices that and faces will be differentiated, as the functions to remove them 
    are different and cannot be used at the same time.
    """

    # Remove the vertices that are on the wholes/windows
    _pattern_vertices = [scaled_poly.is_point_inside(_v) for _v in _verts]
    if polygon.has_holes:
        for polygon_hole in polygon.hole_polygon2d:
            # figure out how many x and y cells to make
            for vert in _verts:
                if polygon_hole.is_point_inside(vert) or polygon_hole.is_point_on_edge(vert, 0.1):
                    _pattern_vertices[_verts.index(vert)] = False

    # build the mesh
    _mesh_init = Mesh2D(_verts, _faces)
    _mesh_init._face_centroids = _centroids
    # Remove the vertices that are not in the pattern
    _new_mesh, _face_pattern = _mesh_init.remove_vertices(_pattern_vertices)
    _new_mesh._face_areas = x_dim * y_dim
    # Get new value sof th enew_mesh
    mesh_faces = _new_mesh.faces
    mesh_verts = _new_mesh.vertices
    mesh_centroid = _new_mesh.face_centroids

    # Remove the faces that are on the wholes/windows
    _pattern_faces = []
    # Initialize the pattern of the faces
    for mesh_face in mesh_faces:
        if [scaled_poly.is_point_inside(mesh_verts[i]) for i in mesh_face] == [True, True, True, True]:
            _pattern_faces.append(True)
        else:
            _pattern_faces.append(False)

    if polygon.has_holes:
        for polygon_hole in polygon.hole_polygon2d:
            for index, mesh_face in enumerate(mesh_faces):
                # Check if the centroid is in the window
                if polygon_hole.is_point_inside(mesh_centroid[index]) or polygon_hole.is_point_on_edge(
                        mesh_centroid[index], 0.1):
                    _pattern_faces[index] = False
                # Check if the middle point of the polygon side is in the window
                else:
                    face_point2d_list = [mesh_verts[i] for i in mesh_face]
                    face_middle_point2_list = [middle_point2d(face_point2d_list[i], face_point2d_list[i + 1])
                                               for i in range(0, len(face_point2d_list) - 1)]
                    face_middle_point2_list.append(
                        middle_point2d(face_point2d_list[-1], face_point2d_list[0]))
                    for middle_point in face_middle_point2_list:
                        if polygon_hole.is_point_inside(middle_point) or polygon_hole.is_point_on_edge(
                                middle_point, 0.1):
                            _pattern_faces[index] = False
                            break
    # Remove the vertices that are not in the pattern
    if True not in _pattern_faces:
        return None
    _new_mesh, _face_pattern = _new_mesh.remove_faces(_pattern_faces)
    _new_mesh._face_areas = x_dim * y_dim

    return _new_mesh


def middle_point2d(point2d_1, point2d_2):
    """
    Return the middle point between two Ladybug Point2D objects
    :param point2d_1: tuple of float
    :param point2d_2: tuple of float
    """
    return (Point2D((point2d_1[0] + point2d_2[0]) / 2, (point2d_1[1] + point2d_2[1]) / 2))


def is_facade(hb_face):
    """
    Check if the hb_face is an exterior wall
    :param hb_face: Honeybee Face3D
    :return: True if the face is an exterior wall, False otherwise
    """
    return (isinstance(hb_face.type, Wall) and isinstance(hb_face.boundary_condition, Outdoors))


def is_roof(hb_face):
    """
    Check if the hb_face is a roof
    :param hb_face: Honeybee Face3D
    :return: True if the face is a roof, False otherwise
    """
    return (isinstance(hb_face.type, RoofCeiling) and isinstance(hb_face.boundary_condition, Outdoors))
