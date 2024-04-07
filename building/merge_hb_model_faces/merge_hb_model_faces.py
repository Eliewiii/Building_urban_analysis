import os
import numpy as np
from math import pi, cos, sin

from shapely.geometry import Polygon, MultiPolygon
from shapely import coverage_union_all, coverage_union, normalize
from ladybug_geometry.geometry3d.polyface import Polyface3D
from ladybug_geometry.geometry3d.face import Face3D
from ladybug_geometry.geometry3d.pointvector import Point3D, Vector3D
from ladybug_geometry.geometry3d.plane import Plane
from ladybug_geometry.bounding import bounding_rectangle_extents

from honeybee.room import Room
from honeybee.model import Model
from honeybee.boundarycondition import Outdoors, Ground
from honeybee.facetype import Wall, RoofCeiling

from utils.utils_constants import TOLERANCE_LBT


def merge_facades_and_roof_faces_in_hb_model(hb_model_obj, orient_roof_mesh_to_according_to_building_orientation=True,
                                             north_angle=0, name=None):
    """
    Merge the faces of the facades and roof of a HB model to have
    :param hb_model_obj: Honeybee Model to merge the faces
    :param orient_roof_mesh_to_according_to_building_orientation: bool: default=True, if True, the roof mesh
        will be oriented according to the orientation of the building
    :param north_angle: float: default=0, angle of the north in degree
    :param name: str: default=None
    :return:
    """
    # Collect all the LB Face3D of the HB model that are exterior walls
    lb_face3d_list = [face.geometry for face in hb_model_obj.faces if
                      (isinstance(face.boundary_condition, Outdoors) and (
                              isinstance(face.type, Wall) or isinstance(face.type,
                                                                        RoofCeiling)) or isinstance(
                          face.boundary_condition,
                          Ground))]

    """
    Shapely is a bit capricious with the union function, so we need round the coordinates of the vertices of the faces
    """
    # make a new face and round the coordinates of the vertices for each face of lb_face3d_list
    new_lb_face3d_list = []
    for face in lb_face3d_list:
        new_vertices = []
        for vertex in face.vertices:  # Round the coordinates
            new_vertices.append(Point3D(round(vertex.x, 2), round(vertex.y, 2), round(vertex.z, 2)))
        # Adjust the orientation of the mesh on the roof
        if face.normal.z > 0:
            # To orient it according to the orientation of the building
            if orient_roof_mesh_to_according_to_building_orientation:
                angle = get_orientation_of_lb_face3d(face)
            # To orient according to the north angle
            else:
                angle = north_angle + 90  # as the north angle is the y axis
            vect_x, vect_y = orientation_to_x_and_y_vector3d(angle)
            # Make the Plan in which the Face3D is
            new_plan = Plane(n=face.plane.n, o=face.plane.o, x=vect_x)
            # Make the new Ladybug Face3D and add it to new_lb_face3d_list
            new_lb_face3d_list.append(Face3D(new_vertices, plane=new_plan, enforce_right_hand=True))
        else:
            new_lb_face3d_list.append(Face3D(new_vertices, plane=face.plane, enforce_right_hand=True))

    # replace the old list by the new one
    lb_face3d_list = new_lb_face3d_list

    # Merge coplanar faces
    merged_multipolygon_and_matrix = []  # List of merged faces
    used_faces = []  # List of used faces

    # Loop through all the faces
    for index, face in enumerate(lb_face3d_list):
        # print(index)
        # Check if the face has been used already, and don't reuse it if so
        if index not in used_faces:
            plane = face.plane  # Get the plane of the face
            origin_new_coordinate_system = plane.o  # Get the origin of the new coordinate system
            # Make a rotation matrix from the plane to project the other faces on the plane
            rotation_matrix = make_rotation_matrix(plane)
            # Make a Polygon 2d from the face
            new_shapely_multipolygon_2d = make_shapely_2d_polygon_from_lb_face(face)  # Initialize the new multipolygon
            used_faces.append(index)
            for index_face_to_merge, face_to_merge in enumerate(lb_face3d_list):  # Loop through all the faces
                # Merge only if the face is not used and is coplanar to the first face
                if index_face_to_merge not in used_faces and face.plane.is_coplanar_tolerance(
                        face_to_merge.plane,
                        tolerance=0.01,
                        angle_tolerance=0.1):
                    # Convert the face into shapely polygon
                    shapely_polygon_2d_to_merge = make_shapely_2d_polygon_from_lb_face_in_plan(face_to_merge,
                                                                                               rotation_matrix,
                                                                                               origin_new_coordinate_system)
                    # Merge the new polygon with the previous one
                    new_shapely_multipolygon_2d = normalize(coverage_union(new_shapely_multipolygon_2d,
                                                                           shapely_polygon_2d_to_merge))
                    # Add the face to the list of used faces
                    used_faces.append(index_face_to_merge)
                else:
                    pass
            # Add the merged polygon to the list of merged polygons
            merged_multipolygon_and_matrix.append(
                (new_shapely_multipolygon_2d, rotation_matrix, origin_new_coordinate_system, plane))
        else:
            pass

    # Convert back to LB Face3D format
    new_lb_face3d_list = []  # Initialize the list of new LB Face3D
    for (obj, rotation_matrix, origin, plane) in merged_multipolygon_and_matrix:
        if isinstance(obj, Polygon):
            new_lb_face3d_list.append(
                make_lb_face_from_shapely_2d_polygon(obj, rotation_matrix, origin, plane))
        elif isinstance(obj, MultiPolygon):
            for polygon in obj.geoms:
                new_lb_face3d_list.append(
                    make_lb_face_from_shapely_2d_polygon(polygon, rotation_matrix, origin, plane))

    # Make Polyface3D from the merged polygons
    polyface_3d = Polyface3D.from_faces(new_lb_face3d_list, tolerance=TOLERANCE_LBT)
    # Make HB Room from Polyface 3D
    room_merged_facades = Room.from_polyface3d(identifier=hb_model_obj.identifier + "_merged_facades",
                                               polyface=polyface_3d)
    Room.solve_adjacency([room_merged_facades], tolerance=TOLERANCE_LBT)
    # Convert the HB Room to a HB Model
    if name is None:
        name = hb_model_obj.identifier + "_merged_faces"
    merged_faces_hb_model_obj = Model(identifier=name, rooms=[room_merged_facades])
    # add apertures to the Model
    add_apertures_to_merged_faces_hb_model(hb_model_obj=hb_model_obj,
                                           merged_faces_hb_model_obj=merged_faces_hb_model_obj)
    # Apply the construction set (of conditioned zone) to the model
    """ The properties of the materials are used for the shading computation. The program doesn't really matter here,
     it's not meant for energy simulation) """

    assign_construction_to_merged_faces_hb_model(hb_model_obj=hb_model_obj,
                                                 merged_faces_hb_model_obj=merged_faces_hb_model_obj)
    # todo @Elie: test if this part works

    return merged_faces_hb_model_obj


def make_shapely_2d_polygon_from_lb_face(lb_face_3D):
    """Convert a Ladybug Face to a Shapely Polygon."""
    # convert vertices into tuples
    list_tuple_vertices_2d = [(x, y) for [x, y] in lb_face_3D.polygon2d.vertices]
    return Polygon(list_tuple_vertices_2d)


def make_shapely_2d_polygon_from_lb_face_in_plan(lb_face_3D, rotation_matrix, origin_new_coordinate_system):
    """Convert a Ladybug Face to a Shapely Polygon."""
    # convert vertices into tuples
    list_tuple_vertices = lb_face_3D.vertices
    # Convert the list of tuples to a list of np.array
    list_vertices_np_array = []
    for vertex in list_tuple_vertices:
        list_vertices_np_array.append(np.array(vertex))
    # Transform the vertices to the new coordinate system
    list_vertices_np_array = [
        np.dot(np.transpose(vertex) - np.transpose(np.array(origin_new_coordinate_system)), rotation_matrix)
        for vertex
        in
        list_vertices_np_array]
    # Convert the list of np.array to a list of tuples
    list_tuple_vertices_2d = [(vertex[0], vertex[1]) for vertex in
                              list_vertices_np_array]  # We don't need the z coordinate as the polygon is supposed to be coplanar

    return Polygon(list_tuple_vertices_2d)


def make_rotation_matrix(plane):
    """Make a rotation matrix from a plane."""
    # make a rotation matrix from the plane
    x_axis = plane.x
    y_axis = plane.y
    z_axis = plane.n
    return np.array([[x_axis.x, y_axis.x, z_axis.x],
                     [x_axis.y, y_axis.y, z_axis.y],
                     [x_axis.z, y_axis.z, z_axis.z]])


def make_lb_face_from_shapely_2d_polygon(polygon, rotation_matrix, origin_new_coordinate_system, plane,
                                         tolerance=TOLERANCE_LBT):
    """Convert a Ladybug Face to a Shapely Polygon."""
    # convert vertices into tuples
    point_list_outline_2d = [list(point) for point in polygon.exterior.__geo_interface__['coordinates']]
    # convert the list of points to a list of Ladybug Point3D
    point_list_outline = [np.array([point[0], point[1], 0]) for point in point_list_outline_2d]
    # Transform back the vertices to the original coordinate system
    rotation_matrix_inverse = np.linalg.inv(rotation_matrix)
    point_list_outline_origin_coordinate_system = [
        np.dot(np.transpose(vertex), rotation_matrix_inverse) + np.transpose(
            np.array(origin_new_coordinate_system)) for
        vertex in point_list_outline]

    point_3d_list = [Point3D(vertex[0], vertex[1], vertex[2]) for vertex in
                     point_list_outline_origin_coordinate_system[:-1]]
    # Convert the list of points to a Ladybug Face3D
    lb_face_footprint = Face3D(boundary=point_3d_list, plane=plane, enforce_right_hand=True)
    # Remove collinear vertices
    lb_face_footprint = lb_face_footprint.remove_colinear_vertices(tolerance=0.001)

    return lb_face_footprint


def get_orientation_of_lb_face3d(LB_Face3D_footprint, n_step=360):
    """ Get the Face3D oriented bounding rectangle/box of a Face3D geometry
    :param LB_Face3D_footprint: Ladybug Face3D
    :param n_step: int : number of steps for the angle of rotation of the bounding box
    :return: LB_Face3D_bounding_rectangle: Ladybug Face3D : oriented bounding rectangle
    """
    # Initialization
    bounding_rectangle_area_list = []  # List of the area of the bounding rectangle for each angle at each step
    angle = 0  # Initial angle
    step = 2 * pi / n_step  # Step of the angle
    # Loop for all the angles
    for i in range(n_step):
        # Get the length and width of the bounding rectangle
        # Geometries accepts only a list of geometry, so we need to convert the Face3D to a list
        length, width = bounding_rectangle_extents(geometries=[LB_Face3D_footprint], axis_angle=angle)
        bounding_rectangle_area_list.append(length * width)
        angle += step
    # get the angle that minimize the area of the bounding rectangle
    angle = step * bounding_rectangle_area_list.index(min(bounding_rectangle_area_list))
    return angle


def orientation_to_x_and_y_vector3d(angle):
    """ Get the x and y vector of a Face3D oriented bounding rectangle/box
    :param angle: float : angle of rotation of the bounding box
    :return: x_vector3d: Vector3D : x vector of the bounding box
    :return: y_vector3d: Vector3D : y vector of the bounding box
    """
    x_vector3d = Vector3D(cos(angle), sin(angle), 0)
    y_vector3d = Vector3D(-sin(angle), cos(angle), 0)
    return x_vector3d, y_vector3d


def add_apertures_to_merged_faces_hb_model(hb_model_obj, merged_faces_hb_model_obj):
    """
    Add the apertures of the original model to the merged faces model
    :param hb_model_obj: Honeybee Model
    :param merged_faces_hb_model_obj: Honeybee Model
    """
    # add apertures to the Model
    hb_model_aperture_list = hb_model_obj.apertures
    for aperture_obj in hb_model_aperture_list:
        for room in merged_faces_hb_model_obj.rooms:
            for face in room.faces:
                if face.geometry.is_sub_face(aperture_obj.geometry, tolerance=TOLERANCE_LBT, angle_tolerance=0.1):
                    face.add_aperture(aperture_obj)


def get_hb_construction(hb_model):
    """
    Get the most common construction for each type of facade (wall, roof, window)
    :param hb_model: Honeybee Model
    :return wall_construction: Honeybee Construction
    :return roof_construction: Honeybee Construction
    :return window_construction: Honeybee Construction
    """
    wall_construction_dict = {}  # key: constrcution_id, , values :occurence (int) and construction (Honeybee Construction)
    roof_construction_dict = {}
    window_construction_dict = {}
    # Loop over all the rooms of the HB model
    for room in hb_model.rooms:
        # Loop over all the faces of the room
        for face in room.faces:
            # Check if the face is an outdoor face
            if isinstance(face.boundary_condition, Outdoors) and isinstance(face.type, Wall):
                # Check if the construction is already in the dict
                if face.properties.energy.construction.identifier in wall_construction_dict:
                    wall_construction_dict[face.properties.energy.construction.identifier]["occurrence"] += 1
                else:
                    # Add the construction to the dict
                    wall_construction_dict[face.properties.energy.construction.identifier] = {
                        "occurrence": 1,
                        "construction": face.properties.energy.construction
                    }
                for hb_aperture in face.apertures:
                    # Check if the construction is already in the dict
                    if hb_aperture.properties.energy.construction.identifier in window_construction_dict:
                        window_construction_dict[hb_aperture.properties.energy.construction.identifier]["occurrence"] += 1
                    else:
                        # Add the construction to the dict
                        window_construction_dict[hb_aperture.properties.energy.construction.identifier] = {
                            "occurrence": 1,
                            "construction": hb_aperture.properties.energy.construction
                        }
            elif isinstance(face.boundary_condition, Outdoors) and isinstance(face.type, RoofCeiling):
                # Check if the construction is already in the dict
                if face.properties.energy.construction.identifier in roof_construction_dict:
                    roof_construction_dict[face.properties.energy.construction.identifier]["occurrence"] += 1
                else:
                    # Add the construction to the dict
                    roof_construction_dict[face.properties.energy.construction.identifier] = {
                        "occurrence": 1,
                        "construction": face.properties.energy.construction
                    }
    # Get the most common construction
    wall_construction = max(wall_construction_dict, key=lambda key: wall_construction_dict[key]["occurrence"])
    roof_construction = max(roof_construction_dict, key=lambda key: roof_construction_dict[key]["occurrence"])
    window_construction = max(window_construction_dict, key=lambda key: window_construction_dict[key]["occurrence"])

    return wall_construction_dict[wall_construction]["construction"], \
        roof_construction_dict[roof_construction]["construction"], \
        window_construction_dict[window_construction]["construction"]


def assign_construction_to_merged_faces_hb_model(hb_model_obj, merged_faces_hb_model_obj):
    """
    Assign the most common construction for each type of facade (wall, roof, window) to the merged faces model
    :param hb_model_obj: Honeybee Model
    :param merged_faces_hb_model_obj: Honeybee Model
    """
    # Get the most common construction
    wall_construction, roof_construction, window_construction = get_hb_construction(hb_model_obj)
    # Assign the construction to the merged faces model
    for room in merged_faces_hb_model_obj.rooms:
        for face in room.faces:
            if isinstance(face.boundary_condition, Outdoors) and isinstance(face.type, Wall):
                face.properties.energy.construction = wall_construction
                for hb_aperture in face.apertures:
                    hb_aperture.properties.energy.construction = window_construction
            elif isinstance(face.boundary_condition, Outdoors) and isinstance(face.type, RoofCeiling):
                face.properties.energy.construction = roof_construction


if __name__ == "__main__":
    None
    # for i in range(0, 10):
    #     path_folder = r"C:\Users\elie-medioni\OneDrive\OneDrive - Technion\Ministry of Energy Research\IBPSA US conference\hbjson_2\var_sub_optimal"
    #     hb_model = Model.from_hbjson(os.path.join(path_folder, f"Buil_TA_{i}.hbjson"))
    #     # hb_model_merged = merge_facades_and_roof_faces_in_hb_model(hb_model, orient_roof_mesh_to_south=True,name=hb_model.identifier + "_merged_south")
    #     # hb_model_merged.add_shades(hb_model.outdoor_shades)
    #     # hb_model_merged.to_hbjson(os.path.join(path_folder,"merged_south",f"Buil_TA_{i}_merged_south.hbjson"))
    #
    #     hb_model_merged = merge_facades_and_roof_faces_in_hb_model(hb_model, orient_roof_mesh_to_south=True,
    #                                                                name=hb_model.identifier + "_merged_or")
    #     hb_model_merged.add_shades(hb_model.outdoor_shades)
    #     hb_model_merged.to_hbjson(os.path.join(path_folder, "merged_or", f"Buil_TA_{i}_merged_or.hbjson"))
    #
    #     # hb_model = Model.from_hbjson(
    #     #     f"C:\\Users\\elie-medioni\\OneDrive\\OneDrive - Technion\\Ministry of Energy Research\\IBPSA US conference\\buildings_hbjson\\variation_1\\ResidentialBldg_{i}.hbjson")
    #     # hb_model_merged = merge_facades_and_roof_faces_in_hb_model(hb_model, hb_model.identifier + "_merged")
    #     # hb_model_merged.add_shades(hb_model.outdoor_shades)
    #     # hb_model_merged.to_hbjson(
    #     #     f"C:\\Users\\elie-medioni\\OneDrive\\OneDrive - Technion\\Ministry of Energy Research\\IBPSA US conference\\buildings_hbjson\\variation_1\\ResidentialBldg_{i}_merged.hbjson")
