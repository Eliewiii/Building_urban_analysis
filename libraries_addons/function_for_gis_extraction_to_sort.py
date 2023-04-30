"""

"""

from utils_libraries_addons import *

def polygon_to_LB_footprint(polygon_obj, unit, tolerance=0.01):
    """
        Transform a Polygon object to a Ladybug footprint.
        Args:
            polygon_obj: A Polygon object.
            unit: Unit of the shp file.
        Returns:
            LB_face_footprint:A Ladybug footprint.
    """
    # todo @Elie: move to LBT methods

    # Convert the exterior of the polygon to a list of points
    point_list_outline = [list(point) for point in polygon_obj.exterior.__geo_interface__['coordinates']]
    # if there is less than 3 points, the geometry is not valid, then return None
    if len(point_list_outline) < 3:
        return None
    # Reverse the list of points to have the right orientation (facing down)
    point_list_outline.reverse()
    # Scale the point list according to the unit of the shp file
    scale_point_list_according_to_unit(point_list_outline, unit)
    # Remove redundant vertices (maybe not necessary, already included in Ladybug)
    # remove_redundant_vertices(point_list_outline, tol=tolerance)

    # Convert the list of points to a list of Ladybug Point3D
    point_3d_list_outline = [Point3D(point[0], point[1], 0) for point in point_list_outline]

    # Convert the exterior of the polygon to a list of points
    # Check if the polygon has holes
    try:
        polygon_obj.interiors  # Check if the polygon has holes
    except:
        interior_holes_pt_list = None
    else:
        interior_holes_pt_list = []
        for hole in polygon_obj.interiors:
            if hole.__geo_interface__['coordinates'] != None:
                if len(hole) == 1:
                    hole = hole[0]
                list_point_hole = [list(point) for point in hole]
                # if their is less than 3 points in the geometry, then the geometry is not valid =>
                if len(list_point_hole) < 3:
                    return None
                list_point_hole.reverse()

                interior_holes_pt_list.append(list_point_hole)
        if interior_holes_pt_list == [None]:
            interior_holes_pt_list = []
        for holes in interior_holes_pt_list:
            scale_point_list_according_to_unit(holes, unit)
            # remove_redundant_vertices(holes,tol = tolerance)  #(maybe not necessary, already included in Ladybug)

        interior_holes_pt_3d_list = []
        for hole in interior_holes_pt_list:
            interior_holes_pt_3d_list.append([Point3D(point[0], point[1], 0) for point in hole])

    # Convert the list of points to a Ladybug footprint
    LB_face_footprint = Face3D(boundary=point_3d_list_outline, holes=interior_holes_pt_3d_list, enforce_right_hand=True)
    # Remove collinear vertices
    LB_face_footprint = LB_face_footprint.remove_colinear_vertices(tolerance=tolerance)

    return LB_face_footprint


def scale_point_list_according_to_unit(point_list, unit):
    """
    Scale the point list according to the unit of the shp file.
    :param point_list: list of points, a point is a list of two coordinates
    :param unit: unit of the shp file, usually degree or meter
    """
    # todo @Elie: move to a "additional function" file/package
    if unit == "deg":
        factor = 111139  # conversion factor, but might be a bit different, it depends on the altitude, but the
        # deformation induced should be small if it's not on a very high mountain
        for point in point_list:
            point[0] = point[0] * factor
            point[1] = point[1] * factor
    # a priori the only units re degrees and meters. For meter not need to scale
    else:
        None


def remove_redundant_vertices(point_list, tol=0.5):
    """
    Check if the points of the footprint are too close to each other. If yes, delete one of the points.
    :param point_list: list of points, a point is a list of two coordinates
    :param tol: tolerance in meter. if the distance between 2 consecutive point is lower than this value, one of the point is deleted
    """
    # todo @Elie: move to a "additional function" file/package

    # Number of points in the point list
    number_of_points = len(point_list)
    # Initialize the index
    i = 0
    while i <= number_of_points - 1:  # go over all points
        if distance(point_list[i], point_list[i + 1]) < tol:
            point_list.pop(i + 1)
        else:
            i += 1
        if i >= len(
                point_list) - 1:  # if we reach the end of the footprint, considering some points were removed, the loop ends
            break
    if distance(point_list[0],
                point_list[-1]) < tol:  # check also with the first and last points in the footprint
        point_list.pop(-1)


def distance(pt_1, pt_2):
    """
    :param pt_1: list for the point 1
    :param pt_2: list for the point 2
    :return: distance between the 2 points
    """
    # todo @Elie: move to a "additional function" file/package

    return sqrt((pt_1[0] - pt_2[0]) ** 2 + (pt_1[1] - pt_2[1]) ** 2)


def add_additional_attribute_keys_to_dict(attribute_key_dict, additional_attribute_key_dict):
    """
    Add additional attribute keys to the attribute key dictionary.
    :param attribute_key_dict: dictionary of attribute keys
    :param additional_attribute_key_dict: dictionary of additional attribute keys
    :return: dictionary of attribute keys
    """
    # todo @Elie: move to a "additional function" file/package
    if additional_attribute_key_dict is None:
        # if there is no additional attribute key dictionary, return the default attribute key dictionary
        return attribute_key_dict
    else:
        concatenated_attribute_key_dict = {}  # initialize the concatenated attribute key dictionary
        for key in additional_attribute_key_dict.keys():
            # sum the list = concatenating the attribute keys
            concatenated_attribute_key_dict[key] = attribute_key_dict[key] + additional_attribute_key_dict[key]
        return concatenated_attribute_key_dict
