"""
Functions used in the first pass of the context filtering algorithm, the minimum view factor criterion.
"""

from math import sqrt, atan, log, pi

def distance_between_lb_point3d(pt_1, pt_2):
    """ 
    Distance between 2 Ladybug geometry Point3D 
    :param pt_1: Ladybug Point3D
    :param pt_2: Ladybug Point3D
    :return: distance between the 2 points
    """
    return sqrt((pt_1.x - pt_2.x) ** 2 + (pt_1.y - pt_2.y) ** 2 + (pt_1.z - pt_2.z) ** 2)

def majorized_vf_between_2_surfaces(point3d_centroid_1, area_1, point3d_centroid_2, area_2):
    """
        Maximal view factor between the 2 surface, in the optimal configuration described in the context paper
    """
    ## distance between the centroids
    d = distance_between_lb_point3d(point3d_centroid_1, point3d_centroid_2)
    if d == 0:  # avoid cases when surfaces are overlapping
        d = 0.01
    ## width of the optimal squares
    width_1 = sqrt(area_1)
    width_2 = sqrt(area_2)
    ## intermediary variable for the computation
    w_1 = width_1 / d  # "normalized width" of the surface 1
    w_2 = width_2 / d  # "normalized width" of the surface 2
    x = w_2 - w_1
    y = w_2 + w_1
    p = (w_1 ** 2 + w_2 ** 2 + 2) ** 2
    q = (x ** 2 + 2) * (y ** 2 + 2)
    u = sqrt(x ** 2 + 4)
    v = sqrt(y ** 2 + 4)
    s = u * (x * atan(x / u) - y * atan(y / u))
    t = v * (x * atan(x / v) - y * atan(y / v))

    return 1 / (pi * w_1 ** 2) * (log(p / q) + s - t)
