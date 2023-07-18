from shapely.geometry import Polygon, MultiPolygon
from shapely import coverage_union_all, coverage_union, normalize
from ladybug_geometry.geometry3d.polyface import Polyface3D
from ladybug_geometry.geometry3d.face import Face3D
from ladybug_geometry.geometry3d.pointvector import Point3D
from ladybug_geometry.geometry3d.plane import Plane

from honeybee.room import Room
from honeybee.model import Model
from honeybee.boundarycondition import Outdoors, Ground
from honeybee.facetype import Wall, RoofCeiling

import numpy as np

default_tolerance = 0.01


def merge_facades_and_roof_faces_in_hb_model(HB_model, name):
    """
    Merge the faces of a HB model
    :param HB_model:
    :return:
    """
    # Collect all the LB Face3D of the HB model that are exterior walls
    lb_face3d_list = [face.geometry for face in HB_model.faces if (isinstance(face.boundary_condition, Outdoors) and (
            isinstance(face.type, Wall) or isinstance(face.type, RoofCeiling)) or isinstance(face.boundary_condition,
                                                                                             Ground))]

    # todo @Elie,test !
    # make a a new face and round the coordinates of the vertices for each face of lb_face3d_list
    new_lb_face3d_list = []
    for face in lb_face3d_list:
        new_vertices = []
        for vertex in face.vertices:
            new_vertices.append(Point3D(round(vertex.x, 2), round(vertex.y, 2), round(vertex.z, 2)))
        new_lb_face3d_list.append(Face3D(new_vertices))

    lb_face3d_list= new_lb_face3d_list

    # Merge coplanar faces
    merged_multipolygon_and_matrix = []  # Initialize the list of merged faces
    used_faces = []  # Initialize the list of used faces

    # Loop through all the faces
    for index, face in enumerate(lb_face3d_list):
        print(index)
        # Check if the face has been used already, and don't reuse it if so
        if index not in used_faces:
            plane = face.plane  # Get the plane of the face
            # Make a rotation matrix from the plane to project the other faces on the plane
            rotation_matrix = make_rotation_matrix(plane)
            origin_new_coordinate_system = plane.o  # Get the origin of the new coordinate system
            new_shapely_multipolygon_2d = make_shapely_2D_polygon_from_lb_face(face)  # Initialize the new multipolygon
            used_faces.append(index)
            for index_face_to_merge, face_to_merge in enumerate(lb_face3d_list):  # Loop through all the faces
                # Merge only if the face is not used and is coplanar to the first face
                if index_face_to_merge not in used_faces and face.plane.is_coplanar_tolerance(face_to_merge.plane,
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
                (new_shapely_multipolygon_2d, rotation_matrix, origin_new_coordinate_system,plane))
        else:
            pass

    # Convert back to LB Face3D format
    new_lb_face3d_list = []  # Initialize the list of new LB Face3D
    for (obj, rotation_matrix, origin,plane) in merged_multipolygon_and_matrix:

        if isinstance(obj, Polygon):
            new_lb_face3d_list.append(make_lb_face_from_shapely_2d_polygon(obj, rotation_matrix, origin, plane))
        elif isinstance(obj, MultiPolygon):
            for polygon in obj.geoms:
                new_lb_face3d_list.append(make_lb_face_from_shapely_2d_polygon(polygon, rotation_matrix, origin, plane))

    # Make Polyface3D from the merged polygons
    polyface_3d = Polyface3D.from_faces(new_lb_face3d_list, tolerance=default_tolerance)
    # Make HB Room from Polyface 3D
    room_merged_facades = Room.from_polyface3d(identifier=hb_model.identifier + "_merged_facades", polyface=polyface_3d)
    Room.solve_adjacency([room_merged_facades], tolerance=default_tolerance)
    # Convert the HB Room to a HB Model
    hb_model_merge_facades = Model(identifier=name, rooms=[room_merged_facades])

    # for face in hb_model_merge_facades.faces:  # todo @Elie, for debugging, to delete
    #     print(face.boundary_condition, face.type, face.geometry.plane.x, face.geometry.plane.y)

    hb_model_aperture_list = hb_model.apertures
    # add apertures to the Model
    for aperture_obj in hb_model_aperture_list:
        for room in hb_model_merge_facades.rooms:
            for face in room.faces:
                if face.geometry.is_sub_face(aperture_obj.geometry, tolerance=default_tolerance, angle_tolerance=0.1):
                    face.add_aperture(aperture_obj)

    return hb_model_merge_facades


def merge_faces_except_roof_and_ground_in_hb_model(hb_model, name):
    """
    Merge the faces of a hb model
    :param hb_model: a hb model
    :param name: name of the new model
    :return:
    """
    # Collect all the LB Face3D of the HB model that are exterior walls
    lb_face3d_list = [face.geometry for face in hb_model.faces if isinstance(face.boundary_condition, Outdoors) and
                      isinstance(face.type, Wall)]




    # Collect all the LB Face3D of the HB model that are exterior walls
    roof_and_ground_face_list = [face.geometry for face in hb_model.faces if (
            isinstance(face.boundary_condition, Outdoors) and isinstance(face.type, RoofCeiling)) or isinstance(
        face.boundary_condition, Ground)]

    # Merge coplanar faces
    merged_multipolygon_and_matrix = []  # Initialize the list of merged faces
    used_faces = []  # Initialize the list of used faces

    # Loop through all the faces
    for index, face in enumerate(lb_face3d_list):

        # Check if the face has been used already, and don't reuse it if so
        if index not in used_faces:
            plane = face.plane  # Get the plane of the face
            # Make a rotation matrix from the plane to project the other faces on the plane
            rotation_matrix = make_rotation_matrix(plane)
            origin_new_coordinate_system = plane.o  # Get the origin of the new coordinate system
            new_shapely_multipolygon_2d = make_shapely_2D_polygon_from_lb_face(face)  # Initialize the new multipolygon
            used_faces.append(index)
            for index_face_to_merge, face_to_merge in enumerate(lb_face3d_list):  # Loop through all the faces
                # Merge only if the face is not used and is coplanar to the first face
                if index_face_to_merge not in used_faces and face.plane.is_coplanar_tolerance(face_to_merge.plane,
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
                (new_shapely_multipolygon_2d, rotation_matrix, origin_new_coordinate_system))
        else:
            pass

    # Convert back to LB Face3D format
    new_lb_face3d_list = []  # Initialize the list of new LB Face3D
    for (obj, rotation_matrix, origin) in merged_multipolygon_and_matrix:

        if isinstance(obj, Polygon):
            new_lb_face3d_list.append(make_lb_face_from_shapely_2d_polygon(obj, rotation_matrix, origin))
        elif isinstance(obj, MultiPolygon):
            for polygon in obj.geoms:
                new_lb_face3d_list.append(make_lb_face_from_shapely_2d_polygon(polygon, rotation_matrix, origin))

    # Add rof and ground to the face list
    new_lb_face3d_list += roof_and_ground_face_list
    # Make Polyface3D from the merged polygons
    polyface_3d = Polyface3D.from_faces(new_lb_face3d_list, tolerance=default_tolerance)
    # Make HB Room from Polyface 3D
    room_merged_facades = Room.from_polyface3d(identifier=hb_model.identifier + "_merged_facades", polyface=polyface_3d)
    Room.solve_adjacency([room_merged_facades], tolerance=default_tolerance)
    # Convert the HB Room to a HB Model
    hb_model_merge_facades = Model(identifier=name, rooms=[room_merged_facades])

    for face in hb_model_merge_facades.faces:
        print(face.boundary_condition, face.type, face.geometry.plane.x, face.geometry.plane.y)

    list_of_aperture = hb_model.apertures
    # add apertures to the Model
    for aperture in list_of_aperture:
        for room in hb_model_merge_facades.rooms:
            for face in room.faces:
                if face.geometry.is_sub_face(aperture.geometry, tolerance=default_tolerance, angle_tolerance=0.1):
                    face.add_aperture(aperture)

    return hb_model_merge_facades


def make_shapely_2D_polygon_from_lb_face(lb_face_3D):
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
        np.dot(np.transpose(vertex) - np.transpose(np.array(origin_new_coordinate_system)), rotation_matrix) for vertex
        in
        list_vertices_np_array]
    # Convert the list of np.array to a list of tuples
    list_tuple_vertices_2d = [(vertex[0], vertex[1]) for vertex in
                              list_vertices_np_array]  # we don't need the z coordinate as the polygon is supposed to be coplanar

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


# def make_shapely_2d_polygon_from_LB_face_in_plan(LB_face_3D,plane):
#     """Convert a Ladybug Face to a Shapely Polygon."""
#     # convert vertices into tuples
#     lb_polygon2d=LB_face_3D.polygon2d
#     lb_polygon2d=lb_polygon2d.move((LB_face_3D.plane.o-plane.o).project(plane.n))
#     print((Point3D((LB_face_3D.plane.o-plane.o).x,(LB_face_3D.plane.o-plane.o).y,(LB_face_3D.plane.o-plane.o).z).project(plane.n,plane.o))) # tocorrect
#     list_tuple_vertices_2d = lb_polygon2d.vertices
#     return Polygon(list_tuple_vertices_2d)

# def make_shapely_2d_polygon_from_LB_face_in_plan(LB_face_3D, plane):
#     """Convert a Ladybug Face to a Shapely Polygon."""
#     # convert vertices into tuples
#     list_pt = [point.project(plane.n, plane.o) for point in LB_face_3D.vertices]
#     print(list_pt)
#
#     return Polygon(list_pt)


# def make_lb_face_from_shapely_2d_polygon(polygon, rotation_matrix, origin_new_coordinate_system,
#                                          tolerance=default_tolerance):
#     """Convert a Ladybug Face to a Shapely Polygon."""
#     # convert vertices into tuples
#     point_list_outline_2d = [list(point) for point in polygon.exterior.__geo_interface__['coordinates']]
#     # convert the list of points to a list of Ladybug Point3D
#     point_list_outline = [np.array([point[0], point[1], 0]) for point in point_list_outline_2d]
#     # Transform back the vertices to the original coordinate system
#     rotation_matrix_inverse = np.linalg.inv(rotation_matrix)
#     point_list_outline_origin_coordinate_system = [
#         np.dot(np.transpose(vertex), rotation_matrix_inverse) + np.transpose(np.array(origin_new_coordinate_system)) for
#         vertex in point_list_outline]
#
#     point_3d_list = [Point3D(vertex[0], vertex[1], vertex[2]) for vertex in point_list_outline_origin_coordinate_system]
#     # Convert the list of points to a Ladybug Face3D
#     lb_face_footprint = Face3D(boundary=point_3d_list, enforce_right_hand=True)
#     # Remove collinear vertices
#     lb_face_footprint = lb_face_footprint.remove_colinear_vertices(tolerance=tolerance)
#
#     return lb_face_footprint


def make_lb_face_from_shapely_2d_polygon(polygon, rotation_matrix, origin_new_coordinate_system, plane,
                                         tolerance=default_tolerance):
    """Convert a Ladybug Face to a Shapely Polygon."""
    # convert vertices into tuples
    point_list_outline_2d = [list(point) for point in polygon.exterior.__geo_interface__['coordinates']]
    # convert the list of points to a list of Ladybug Point3D
    point_list_outline = [np.array([point[0], point[1], 0]) for point in point_list_outline_2d]
    # Transform back the vertices to the original coordinate system
    rotation_matrix_inverse = np.linalg.inv(rotation_matrix)
    point_list_outline_origin_coordinate_system = [
        np.dot(np.transpose(vertex), rotation_matrix_inverse) + np.transpose(np.array(origin_new_coordinate_system)) for
        vertex in point_list_outline]

    point_3d_list = [Point3D(vertex[0], vertex[1], vertex[2]) for vertex in point_list_outline_origin_coordinate_system[:-1]]
    # Convert the list of points to a Ladybug Face3D
    lb_face_footprint = Face3D(boundary=point_3d_list, plane=plane, enforce_right_hand=True)
    # Remove collinear vertices
    lb_face_footprint = lb_face_footprint.remove_colinear_vertices(tolerance=0.001)

    return lb_face_footprint


# def make_LB_face_from_shapely_polygon(polygon, tolerance=default_tolerance):
#     """Convert a Ladybug Face to a Shapely Polygon."""
#     # convert vertices into tuples
#     point_list_outline = [list(point) for point in polygon.exterior.__geo_interface__['coordinates']]
#     # convert the list of points to a list of Ladybug Point3D
#     point_3d_list_outline = [Point3D(point[0], point[1], 0) for point in point_list_outline]
#     # Convert the list of points to a Ladybug Face3D
#     LB_face_footprint = Face3D(boundary=point_3d_list_outline, enforce_right_hand=True)
#     # Remove collinear vertices
#     LB_face_footprint = LB_face_footprint.remove_colinear_vertices(tolerance=tolerance)
#
#     return LB_face_footprint


if __name__ == "__main__":
    # hb_model = Model.from_hbjson(
    #     r"C:\Users\elie-medioni\OneDrive\OneDrive - Technion\BUA\Samples\Elie\hb_model\complex_hb_model.hbjson")
    # hb_model_merged = merge_faces_in_HB_Model(hb_model, "test_all")
    # hb_model_merged_seperate_roof_and_ground = merge_faces_except_roof_and_ground_in_hb_model(hb_model,
    #                                                                                           "test_all_seperate_roof_and_ground")
    # hb_model_merged.to_hbjson(
    #     r"C:\Users\elie-medioni\OneDrive\OneDrive - Technion\BUA\Samples\Elie\hb_model\complex_hb_model_merge_facades.hbjson")
    # hb_model_merged_seperate_roof_and_ground.to_hbjson(
    #     r"C:\Users\elie-medioni\OneDrive\OneDrive - Technion\BUA\Samples\Elie\hb_model\complex_hb_model_merge_facades_sep_roof.hbjson")

    hb_model = Model.from_hbjson(
        r"C:\Users\elie-medioni\OneDrive\OneDrive - Technion\BUA\Samples\Grasshopper\Dragonfly_H-Building+Balconies+Context.hbjson")
    hb_model_merged = merge_facades_and_roof_faces_in_hb_model(hb_model, "test_all")
    # hb_model_merged_seperate_roof_and_ground = merge_faces_except_roof_and_ground_in_hb_model(hb_model,
    #                                                                                           "test_all_seperate_roof_and_ground")
    hb_model_merged.to_hbjson(
        r"C:\Users\elie-medioni\OneDrive\OneDrive - Technion\BUA\Samples\Grasshopper\Dragonfly_H-Building+Balconies+Context_merged.hbjson")
    # hb_model_merged_seperate_roof_and_ground.to_hbjson(
    #     r"C:\Users\elie-medioni\OneDrive\OneDrive - Technion\BUA\Hilany\Samples\mesh_issue\complex_model_Abraham.hbjson")
