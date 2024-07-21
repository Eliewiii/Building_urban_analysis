"""
Test the functions that generate rectangles.
"""
import numpy as np
from current_development.mvfc_demonstration.utils_random_rectangle_generation import \
    generate_random_rectangles,rectangle_normal

from current_development.mvfc_demonstration.utils_mvfc_demonstration import distance_between_points
def test_generate_proper_squares():
    """
    Test the function generate_proper_squares.
    """

    rectangle_1, rectangle_2 = generate_random_rectangles(min_size=0.1, max_size=10,max_distance_factor=10,parallel_coaxial_squares=True)
    rectangle_1_vertices = rectangle_1.points
    rectangle_2_vertices = rectangle_2.points
    # Check the size of the squares
    assert distance_between_points(rectangle_1_vertices[0],rectangle_1_vertices[1]) == distance_between_points(rectangle_1_vertices[1],rectangle_1_vertices[2])
    assert distance_between_points(rectangle_2_vertices[0],rectangle_2_vertices[1]) == distance_between_points(rectangle_2_vertices[1],rectangle_2_vertices[2])
    # check the normal of the squares
    assert np.array_equal(rectangle_normal(rectangle_1,normalize=True),np.array([0.,0.,1.]))
    assert np.array_equal(rectangle_normal(rectangle_2,normalize=True),np.array([0.,0.,-1.]))
    # # check that the squares are coaxial
    assert rectangle_normal(rectangle_1,normalize=True).dot(rectangle_normal(rectangle_2,normalize=True)) == -1.0
