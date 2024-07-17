"""

"""

import random

import pyvista as pv
import pyviewfactor as pvf

from math import sqrt, atan, log, pi


def generate_random_rectangles(min_size: float = 0., max_size: float = 100.):
    """

    """

    max_distance = 100 * max_size

    def generate_ref_rectangle_in_xy_plane():
        """ Generate a rectangle in the (x, y) plane. """
        width = random.uniform(min_size, max_size)
        pointa = [1, 0, 0]
        pointb = [1, width, 0]
        pointc = [0, width, 0]
        pointd = [0, 0, 0]
        return pv.Rectangle([pointa, pointb, pointc])

    def generate_random_rectangle(ref_rectangle):
        """ Generate a random rectangle that faces the reference rectangle. """
        # Select a random unit vector that points towards the reference rectangle
        # which means that has a strictly negative dot product with the z vector
        random_unit_vector = [random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1, 1)]
        random_unit_vector[2] = -abs(random_unit_vector[2])
        random_unit_vector = [x / sqrt(random_unit_vector[0] ** 2 + random_unit_vector[1] ** 2 + random_unit_vector[2] ** 2) for x in random_unit_vector]
        # Select a random distance from the reference rectangle
        random_distance = random.uniform(0, max_distance)
        # Compute the centroid of the reference rectangle
        centroid = ref_rectangle.center
        # Compute the centroid of the random rectangle
        random_centroid = [centroid[0] + random_distance * random_unit_vector[0], centroid[1] + random_distance * random_unit_vector[1], centroid[2] + random_distance * random_unit_vector[2]]






def computes_vf_betweem_2_rectangles(pv_rectangle_1, pv_rectangle_2):
    """

    """
    if pvf.get_visibility(pv_rectangle_1, pv_rectangle_2, strict=False, print_warning=False):
        vf = pvf.compute_viewfactor(pv_rectangle_1, pv_rectangle_2, epsilon=0.001, rounding_decimal=10)
        supremum_vf = majorized_vf_between_2_surfaces(pv_rectangle_1, pv_rectangle_2)

        return vf, supremum_vf
    else:
        return False, False


def majorized_vf_between_2_surfaces(pv_rectangle_1, pv_rectangle_2):
    """
    Maximal view factor between the 2 surface, in the optimal configuration described in the context paper
    :param pv_rectangle_1: pyvista rectangle
    :param pv_rectangle_2: pyvista rectangle
    """
    # Recangle 1
    area_1 = pv_rectangle_1.area
    # Recangle 2
    area_2 = pv_rectangle_2.area
    # VF computation
    distance_centroids = distance_between_rectangle_centroids(pv_rectangle_1, pv_rectangle_2)

    return compute_analytical_vf_coaxial_parallel_squares(area_1, area_2, distance_centroids)


def distance_between_rectangle_centroids(pv_rectangle_1, pv_rectangle_2):
    """
    Distance between the centroids of 2 pyvista rectangles
    :param pv_rectangle_1: pyvista rectangle
    :param pv_rectangle_2: pyvista rectangle
    :return: distance between the 2 centroids
    """
    return distance_between_points(pv_rectangle_1.center, pv_rectangle_2.center)


def distance_between_points(pt_1, pt_2):
    """
    Distance between 2 Ladybug geometry Point3D
    :param pt_1: Ladybug Point3D
    :param pt_2: Ladybug Point3D
    :return: distance between the 2 points
    """
    return sqrt((pt_1[0] - pt_2[0]) ** 2 + (pt_1[1] - pt_2[1]) ** 2 + (pt_1[2] - pt_2[2]) ** 2)


def compute_analytical_vf_coaxial_parallel_squares(area_1: float, area_2: float, distance: float):
    """
        Maximal view factor between the 2 surface, in the optimal configuration described in the context paper
    """
    ## distance between the centroids
    d = distance
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
