"""
Additional functions for Ladybug Face objects.
"""
import logging

from shapely.geometry import Polygon

import dragonfly

from ladybug_geometry.geometry3d.pointvector import Point3D
from ladybug_geometry.geometry3d.face import Face3D
from honeybee.boundarycondition import Outdoors

def LB_face_to_shapely_polygon(LB_face):
    """Convert a Ladybug Face to a Shapely Polygon."""
    # convert vertices into tuples
    list_tuple_vertices_2d = [(x,y) for [x,y,z] in LB_face.vertices]
    
    return Polygon(list_tuple_vertices_2d)


def shapely_polygon_to_LB_face(polygon,tolerance=0.01):
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


def merge_LB_face_list(LB_face_list,):
    """
    todo: @ Elie, solve number of arguments
    Merge LB Face3D into one.
    I cannot consider holes ! would need to adapt it eventually but it's not necessary for now
    todo: adapt if the merging create a multy-polygon
    :param LB_face_list:
    :return:
    """
    # Merge only of there is more than one face
    if len (LB_face_list) > 1:
        # convert each LB face to Polygon
        polygon_list = [LB_face_to_shapely_polygon(LB_face) for LB_face in LB_face_list]
        # Initialize merging polygon
        merged_polygon = polygon_list[0]
        # loop over each polygon
        for polygon in polygon_list[1:] :
            merged_polygon.union(polygon)  # merge the polygon with the merged polygon
        # convert the merged polygon to a LB geometry face 3D
        LB_face_merged = shapely_polygon_to_LB_face(merged_polygon)
        return LB_face_merged
    # if there is only one face, return it
    if len (LB_face_list) == 1:
        return(LB_face_list[0])
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
    floor_to_floor_heights = [self.floor_height for i in range(self.num_floor)]
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
            nb_cores=len(df_building.unique_stories[0].room_2ds)-nb_rooms_per_stories+1
            core_area = sum([df_building.unique_stories[0].room_2ds[-i-1].floor_area for i in range(nb_cores)])
            if max_core_area < core_area:
                perimeter_offset_boundary_down = perimeter_offset
            elif min_core_area > core_area:
                perimeter_offset_boundary_up = perimeter_offset
            else :
                converged= True
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
        for id_story in range (len(self.DF_building.unique_stories)):
            for room_id in range(nb_rooms_per_stories-1):
                self.DF_building.unique_stories[0].room_2ds[room_id].identifier= "apartment_" + str(room_id)
            # last room is the core
            for i in range(len(self.DF_building.unique_stories[0].room_2ds)-nb_rooms_per_stories + 1):
                self.DF_building.unique_stories[0].room_2ds[-i-1].identifier = "core_" + str(i)



    else:
        logging.warning(f" building_{self.id} : the automatic subdivision in rooms and cores failed")
        self.DF_building = dragonfly.building.Building.from_footprint(identifier="Building_" + str(self.id),
                                                                      footprint=[LB_face_footprint],
                                                                      floor_to_floor_heights=floor_to_floor_heights)
        # rename only the main room
        for id_story in range (len(self.DF_building.unique_stories)):
                self.DF_building.unique_stories[0].room_2ds[0].identifier= "apartment_" + str(0)

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

def roo2d_is_core(room_2d):
    """ check if a room is a core or not """
    # isinstance(surface.boundary_condition, Outdoors)
    for boundary_condition in room_2d.boun:
        if isinstance(boundary_condition, Outdoors):
            return False
    return True



if __name__== "__main__":

    None