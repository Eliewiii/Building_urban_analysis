"""

"""

from libraries_addons.libraries_utils import *


def is_bounding_box_context_using_mvfc_criterion(target_LB_polyface3d_extruded_footprint,
                                                 context_LB_polyface3d_oriented_bounding_box, minimum_vf_criterion):
    """
    Check if the bounding box of a context building is a context for the current building.
    It correspond to the first pass of the
    :param target_LB_polyface3d_extruded_footprint: LB polyface3d of the current building
    :param context_LB_polyface3d_oriented_bounding_box: LB polyface3d of the bounding box of the context building
    :param minimum_vf_criterion: minimum view factor between surfaces to be considered as context surfaces
    in the first pass of the algorithm
    :return: boolean
    """
    # todo @Elie check the description of the function and test it
    # Loop over all the couples of surfaces between the target building and the context building
    for context_LB_Face3D in list(context_LB_polyface3d_oriented_bounding_box.faces):  # polyface3D.faces is a tuple
        if not is_vector3D_vertical(context_LB_Face3D.normal):  # exclude the horizontal/roof/ground surfaces
            for target_LB_Face3D in list(target_LB_polyface3d_extruded_footprint):
                # Get the view factor between the context building and the current building
                majorized_view_factor = max_VF(Point3D_centroid_1=target_LB_Face3D.centroid,
                                               area_1=target_LB_Face3D.area,
                                               Point3D_centroid_2=context_LB_Face3D.centroid,
                                               area_2=context_LB_Face3D.arrea)
                # If the view factor is above the minimum criterion, add the building to the list of buildings
                # that will be used for the second pass
                if majorized_view_factor > minimum_vf_criterion:
                    return True
    # if none of the surfaces match the criterion, return False
    return False


def distance_between_LB_Point3d(pt_1, pt_2):
    """ Distance between 2 LB geometry Point3D """
    return sqrt((pt_1.x - pt_2.x) ** 2 + (pt_1.y - pt_2.y) ** 2 + (pt_1.z - pt_2.z) ** 2)


def max_VF(Point3D_centroid_1, area_1, Point3D_centroid_2, area_2):
    """
        Maximal view factor between the 2 surface, in the optimal configuration described in the context paper
        the faces are lists with following format :  [LB_face_obj,area, centroid]
    """
    ## distance between the centroids
    d = distance_between_LB_Point3d(Point3D_centroid_1, Point3D_centroid_2)
    if d == 0:  # avoid cases when surfaces are overlapping
        d = 0.01
    ## width of the optimal squares
    W_1 = sqrt(area_1)
    W_2 = sqrt(area_2)
    ## intermediary variable for the computation
    w_1 = W_1 / d
    w_2 = W_2 / d
    x = w_2 - w_1
    y = w_2 + w_1
    p = (w_1 ** 2 + w_2 ** 2 + 2) ** 2
    q = (x ** 2 + 2) * (y ** 2 + 2)
    u = sqrt(x ** 2 + 4)
    v = sqrt(y ** 2 + 4)
    s = u * (x * atan(x / u) - y * atan(y / u))
    t = v * (x * atan(x / v) - y * atan(y / v))

    return 1 / (pi * w_1 ** 2) * (log(p / q) + s - t)


def is_vector3D_vertical(Vector3D):
    if Vector3D.x == 0 and Vector3D.y == 0:
        return True
    else:
        return False
