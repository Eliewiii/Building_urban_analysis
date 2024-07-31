"""

"""

from current_development.mvfc_demonstration.utils_random_rectangle_generation import \
    generate_random_rectangles

from current_development.mvfc_demonstration.utils_to_radiance import \
    compute_vf_between_one_rectangle_and_a_list_of_rectangles_with_radiance

def test_compute_vf_between_one_rectangle_and_a_list_of_rectangles_with_radiance():
    """
    Test the function to compute the view factor between one rectangle and a list of rectangles with Radiance
    """

    rectangle_1, rectangle_2_list = generate_random_rectangles(min_size=0.1, max_size=5,
                                                               max_distance_factor=5,
                                                               nb_random_rectangles=1,
                                                               parallel_coaxial_squares=True)
    path_temp_folder = r"..\file_temp"
    vf_radiance = compute_vf_between_one_rectangle_and_a_list_of_rectangles_with_radiance(rectangle_1, rectangle_2_list, path_temp_folder, nb_rays=10000)
    print(vf_radiance)
    assert len(vf_radiance) == 1.0

    nb_random_rectangles = 100
    rectangle_1, rectangle_2_list = generate_random_rectangles(min_size=0.2, max_size=5,
                                                               max_distance_factor=15,
                                                               parallel_coaxial_squares=False,
                                                               nb_random_rectangles=nb_random_rectangles)
    vf_radiance = compute_vf_between_one_rectangle_and_a_list_of_rectangles_with_radiance(rectangle_1, rectangle_2_list, path_temp_folder, nb_rays=100000)
    print(vf_radiance)
    assert len(vf_radiance) == nb_random_rectangles
