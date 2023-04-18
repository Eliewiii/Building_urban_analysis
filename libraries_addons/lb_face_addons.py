"""
Additional functions for Ladybug Face objects.
"""

from libraries_addons.utils import *

# todo : for some rreason, the following import is necessary for _orient_geometry to work
from ladybug_geometry.bounding import  _orient_geometry



def make_shapely_polygon_from_LB_face(LB_face):
    """Convert a Ladybug Face to a Shapely Polygon."""
    # convert vertices into tuples
    list_tuple_vertices_2d = [(x, y) for [x, y, z] in LB_face.vertices]

    return Polygon(list_tuple_vertices_2d)


def make_LB_face_from_shapely_polygon(polygon, tolerance=0.01):
    """Convert a Ladybug Face to a Shapely Polygon."""
    # convert vertices into tuples
    point_list_outline = [list(point) for point in polygon.exterior.__geo_interface__['coordinates']]
    # convert the list of points to a list of Ladybug Point3D
    point_3d_list_outline = [Point3D(point[0], point[1], 0) for point in point_list_outline]
    # Convert the list of points to a Ladybug Face3D
    LB_face_footprint = Face3D(boundary=point_3d_list_outline, enforce_right_hand=True)
    # Remove collinear vertices
    LB_face_footprint = LB_face_footprint.remove_colinear_vertices(tolerance=tolerance)

    return LB_face_footprint


def LB_face_footprint_to_lB_polyface3D_extruded_footprint(LB_face_footprint, height= 9.,elevation=0.):
    """
    Extrude a ladybug geometry footprint to obtain the room envelop
    :param LB_face_footprint: ladybug geometry footprint
    :param height: height of the building in meters
    :return: ladybug geometry extruded footprint
    """
    # extrude the footprint to obtain the room envelop
    extruded_face = Polyface3D.from_offset_face(LB_face_footprint, height)
    # move the room to the right elevation
    extruded_face.move(Vector3D(0, 0, elevation))

    return extruded_face


def make_LB_polyface3D_oriented_bounding_box_from_LB_face3D_footprint(LB_face_footprint, height=9., elevation=0.):
    """ Make Ladybug Polyface3D oriented bounding box from a Ladybug Face3D (mostly from the footprint of buildings)
    :param LB_face_footprint: Ladybug Face3D
    :param height: float : height of the building
    :param elevation: float : elevation of the building compared to the ground
    :return: LB_polyface3D_bounding_box: Ladybug Polyface3D : oriented bounding box
    """
    # Identify the oriented bounding rectangle and the angle of orientation
    LB_face3d_bounding_rectangle, angle = make_LB_Face3D_oriented_bounding_rectangle_from_LB_Face3D_footprint(
        LB_face_footprint)
    # extrude the rectangle to obtain the oriented bounding box
    LB_polyface3d_bounding_box = Polyface3D.from_offset_face(LB_face3d_bounding_rectangle, height)
    # move the bounding box to the right elevation
    LB_polyface3d_bounding_box.move(Vector3D(0, 0, elevation))

    return LB_polyface3d_bounding_box.move(Vector3D(0, 0, elevation))


def make_LB_Face3D_oriented_bounding_rectangle_from_LB_Face3D_footprint(LB_Face3D_footprint, n_step=360):
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
    # get the bounding rectangle for the best angle
    oriented_bounding_rectangle = make_LB_Face3D_footprint_bounding_rectangle(LB_Face3D_footprint=LB_Face3D_footprint,
                                                                              angle=angle)

    return oriented_bounding_rectangle, angle


def make_LB_Face3D_footprint_bounding_rectangle(LB_Face3D_footprint, angle=0):
    """ Get the oriented bounding rectangle of a Face3D geometry
    :param LB_Face3D_footprint: Ladybug Face3D
    :param angle: float : angle of rotation of the bounding box
    :return: LB_Face3D_bounding_rectangle: Ladybug Face3D : oriented bounding rectangle
    """
    if angle != 0:  # rotate geometry to the bounding box
        center_of_rotation = LB_Face3D_footprint.vertices[0]
        oriented_LB_Face3D_footprint_list = _orient_geometry(geometries=[LB_Face3D_footprint], axis_angle=angle,
                                                        center=center_of_rotation)

    else:
        oriented_LB_Face3D_footprint_list = [LB_Face3D_footprint]
        # The result from _orient_geometry is a list
    xx = bounding_domain_x(oriented_LB_Face3D_footprint_list)  # x minimum and maximum
    yy = bounding_domain_y(oriented_LB_Face3D_footprint_list)  # y minimum and maximum
    pt_1 = Point3D(xx[0], yy[0])  # lower left corner
    pt_2 = Point3D(xx[0], yy[1])  # upper left corner
    pt_3 = Point3D(xx[1], yy[1])  # upper right corner
    pt_4 = Point3D(xx[1], yy[0])  # lower right corner
    if angle != 0:  # rotate the points back
        # center_of_rotation = Point3D(center_of_rotation.x, center_of_rotation.y, 0.)  # cast Point3D to Point2D
        pt_1 = pt_1.rotate_xy(angle, center_of_rotation)
        pt_2 = pt_2.rotate_xy(angle, center_of_rotation)
        pt_3 = pt_3.rotate_xy(angle, center_of_rotation)
        pt_4 = pt_4.rotate_xy(angle, center_of_rotation)
    # Create the rectangle
    LB_Face3D_bounding_rectangle = Face3D([pt_4, pt_3, pt_2, pt_1])  # The points need to be counterclockwise

    return LB_Face3D_bounding_rectangle


def merge_LB_face_list(LB_face_list):
    """
    Merge LB Face3D into one.
    I cannot consider holes ! would need to adapt it eventually but it's not necessary for now
    todo: adapt if the merging create a multy-polygon
    :param LB_face_list:
    :return:
    """
    # Merge only of there is more than one face
    if len(LB_face_list) > 1:
        # convert each LB face to Polygon
        polygon_list = [make_shapely_polygon_from_LB_face(LB_face) for LB_face in LB_face_list]
        # Initialize merging polygon
        merged_polygon = polygon_list[0]
        # loop over each polygon
        for polygon in polygon_list[1:]:
            merged_polygon.union(polygon)  # merge the polygon with the merged polygon
        # convert the merged polygon to a LB geometry face 3D
        if type(merged_polygon) is Polygon:
            LB_face_merged = make_LB_face_from_shapely_polygon(merged_polygon)
            return LB_face_merged
        else:
            logging.warning("The footprint of the building is not a single polygon")
            # raise error
            raise ValueError("The footprint of the building is not a single polygon")
    # if there is only one face, return it
    elif len(LB_face_list) == 1:
        return (LB_face_list[0])
    # if there is no face, return a warning
    else:
        logging.warning("The list of faces to merge is empty")
        # raise error
        raise ValueError("The list of faces to merge is empty")


def LB_footprint_to_df_building(LB_face_footprint, core_area_ratio=0.15, tol=0.005):
    """ generate a Dragonfly building out of the footprint, generating a core in the center """
    # todo @Elie : adapt to the new tool

    footprint_area = LB_face_footprint.area
    # target area of the core and the acceptable range
    target_core_area = footprint_area * core_area_ratio
    max_core_area = target_core_area * (1 + tol)
    min_core_area = target_core_area * (1 - tol)
    # list with the floor height between each floor
    #TODO what do wanted to do here?
    #floor_to_floor_heights = [self.floor_height for i in range(self.num_floor)]
    # initialization of the dichotomy
    perimeter_offset_boundary_up = 20
    perimeter_offset_boundary_down = 1
    perimeter_offset = perimeter_offset_boundary_down
    first_try_df_building = dragonfly.building.Building.from_footprint(identifier="Building_" + str(self.id),
                                                                       footprint=[LB_face_footprint],
                                                                       floor_to_floor_heights=[3.],
                                                                       perimeter_offset=perimeter_offset)
    # number of rooms including the core when subdivided by the Dragonfly algorithm
    nb_rooms_per_stories = len(first_try_df_building.unique_stories[0].room_2ds)
    # core_area = first_try_df_building.unique_stories[0].room_2ds[-1].floor_area()

    max_iteration = 30
    converged = False
    for i in range(max_iteration):
        # print("it {}".format(i),footprint_area,target_core_area)
        perimeter_offset = (perimeter_offset_boundary_up + perimeter_offset_boundary_down) / 2.

        df_building = dragonfly.building.Building.from_footprint(identifier="Building_" + str(self.id),
                                                                 footprint=[LB_face_footprint],
                                                                 floor_to_floor_heights=[3.],
                                                                 perimeter_offset=perimeter_offset)
        # print("it {}".format(i))
        if len(df_building.unique_stories[0].room_2ds) >= nb_rooms_per_stories:
            nb_cores = len(df_building.unique_stories[0].room_2ds) - nb_rooms_per_stories + 1
            core_area = sum([df_building.unique_stories[0].room_2ds[-i - 1].floor_area for i in range(nb_cores)])
            if max_core_area < core_area:
                perimeter_offset_boundary_down = perimeter_offset
            elif min_core_area > core_area:
                perimeter_offset_boundary_up = perimeter_offset
            else:
                converged = True
                break
        else:
            # print("wrong number of room")
            perimeter_offset_boundary_up = perimeter_offset

    if converged:
        self.DF_building = dragonfly.building.Building.from_footprint(identifier="Building_" + str(self.id),
                                                                      footprint=[LB_face_footprint],
                                                                      floor_to_floor_heights=floor_to_floor_heights,
                                                                      perimeter_offset=perimeter_offset)
        # Rename the room to know what are the apartments and cores
        for id_story in range(len(self.DF_building.unique_stories)):
            for room_id in range(nb_rooms_per_stories - 1):
                self.DF_building.unique_stories[0].room_2ds[room_id].identifier = "apartment_" + str(room_id)
            # last room is the core
            for i in range(len(self.DF_building.unique_stories[0].room_2ds) - nb_rooms_per_stories + 1):
                self.DF_building.unique_stories[0].room_2ds[-i - 1].identifier = "core_" + str(i)



    else:
        logging.warning(f" building_{self.id} : the automatic subdivision in rooms and cores failed")
        self.DF_building = dragonfly.building.Building.from_footprint(identifier="Building_" + str(self.id),
                                                                      footprint=[LB_face_footprint],
                                                                      floor_to_floor_heights=floor_to_floor_heights)
        # rename only the main room
        for id_story in range(len(self.DF_building.unique_stories)):
            self.DF_building.unique_stories[0].room_2ds[0].identifier = "apartment_" + str(0)


def find_perimeter_offset_df_building(LB_face_footprint, core_area_ratio=0.15, tol=0.005):
    """ generate a Dragonfly building out of the footprint, generating a core in the center """

    footprint_area = LB_face_footprint.area
    # target area of the core and the acceptable range
    target_core_area = footprint_area * core_area_ratio
    max_core_area = target_core_area * (1 + tol)
    min_core_area = target_core_area * (1 - tol)
    # Dichotomy parameters
    perimeter_offset_boundary_up = 20
    perimeter_offset_boundary_down = 1

    max_iteration = 30
    converged = False
    for i in range(max_iteration):
        # print("it {}".format(i),footprint_area,target_core_area)
        perimeter_offset = (perimeter_offset_boundary_up + perimeter_offset_boundary_down) / 2.

        df_building = dragonfly.building.Building.from_footprint(identifier="temp",
                                                                 footprint=[LB_face_footprint],
                                                                 floor_to_floor_heights=[3.],  # Doesn't matter
                                                                 perimeter_offset=perimeter_offset)
        # print("it {}".format(i))

        # get the Room2D that are cores = without any Outdoor boundary condition

        if len(df_building.unique_stories[0].room_2ds) >= nb_rooms_per_stories:
            nb_cores = len(df_building.unique_stories[0].room_2ds) - nb_rooms_per_stories + 1
            core_area = sum([df_building.unique_stories[0].room_2ds[-i - 1].floor_area for i in range(nb_cores)])
            if max_core_area < core_area:
                perimeter_offset_boundary_down = perimeter_offset
            elif min_core_area > core_area:
                perimeter_offset_boundary_up = perimeter_offset
            else:
                converged = True
                break
        else:
            # print("wrong number of room")
            perimeter_offset_boundary_up = perimeter_offset

    if converged:
        self.DF_building = dragonfly.building.Building.from_footprint(identifier="Building_" + str(self.id),
                                                                      footprint=[LB_face_footprint],
                                                                      floor_to_floor_heights=floor_to_floor_heights,
                                                                      perimeter_offset=perimeter_offset)
        # Rename the room to know what are the apartments and cores
        for id_story in range(len(self.DF_building.unique_stories)):
            for room_id in range(nb_rooms_per_stories - 1):
                self.DF_building.unique_stories[0].room_2ds[room_id].identifier = "apartment_" + str(room_id)
            # last room is the core
            for i in range(len(self.DF_building.unique_stories[0].room_2ds) - nb_rooms_per_stories + 1):
                self.DF_building.unique_stories[0].room_2ds[-i - 1].identifier = "core_" + str(i)


def room2d_is_core(room_2d):
    """ check if a room is a core or not """
    # isinstance(surface.boundary_condition, Outdoors)
    for boundary_condition in room_2d.boun:
        if isinstance(boundary_condition, Outdoors):
            return False
    return True