"""
Test the functions that generate rectangles.
"""
import numpy as np
from current_development.mvfc_demonstration.utils_random_rectangle_generation import \
    generate_random_rectangles, rectangle_normal

from current_development.mvfc_demonstration.utils_mvfc_demonstration import computes_vf_betweem_2_rectangles


def test_radiance_computation_compared_to_analytical_solution():
    """
    Test the function generate_proper_squares.
    """
    n_rectangles = 10
    nb_ray = 1000000
    path_temp_folder = r"..\file_temp"
    for i in range(n_rectangles):
        print(f"Progress: {100*i/n_rectangles}%")
        rectangle_1, rectangle_2_list = generate_random_rectangles(min_size=0.2, max_size=5,
                                                              max_distance_factor=3,
                                                              parallel_coaxial_squares=True)
        vf, vf_radiance, supremum_vf = computes_vf_betweem_2_rectangles(rectangle_1, rectangle_2_list[0],
                                                                        path_temp_folder, nb_rays=nb_ray)
        assert abs(1 - vf_radiance / supremum_vf) < 0.01
        print(f"VF: {vf}, VF Radiance: {vf_radiance}, Supremum VF: {supremum_vf}")
