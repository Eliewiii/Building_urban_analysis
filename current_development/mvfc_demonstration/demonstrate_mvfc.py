"""

"""

from tqdm import tqdm

from current_development.mvfc_demonstration.utils_random_rectangle_generation import \
    generate_random_rectangles
from current_development.mvfc_demonstration.utils_mvfc_demonstration import computes_vf_betweem_2_rectangles
from current_development.mvfc_demonstration.test.plot_pyvista_obj import *

n_rectangles = 10000
path_temp_folder = r".\file_temp"

vf_tuple_list = []
exceptions = []

# for i in tqdm(range(n_rectangles)):
for i in range(n_rectangles):
    if i % 100 == 0:
        print(f"Progress: {i}/{n_rectangles}%")
    ref_rectangle, random_rectangle_list = generate_random_rectangles(min_size=0.1, max_size=10,
                                                                 max_distance_factor=10)
    vf, vf_radiance, supremum_vf = computes_vf_betweem_2_rectangles(ref_rectangle, random_rectangle_list[0],
                                                                    path_temp_folder)
    vf_tuple_list.append((vf, supremum_vf, True if supremum_vf >= vf else False))
    # if supremum_vf <= vf:
    #     # print(f"VF: {vf} , Radiance_VF :{vf_radiance}, Supremum VF: {supremum_vf}")
    #     exceptions.append((ref_rectangle, random_rectangle))
    #     # plot_rectangle([ref_rectangle,random_rectangle],['blue',"red"])
    if vf_radiance >= supremum_vf and vf_radiance - supremum_vf > 0.0001:
        print(f"Radiance bigger !, Radiance_VF :{vf_radiance}, Supremum VF: {supremum_vf}")
        exceptions.append((ref_rectangle, random_rectangle))
        plot_rectangle([ref_rectangle, random_rectangle], ['blue', "red"])

print([result_tuple[2] for result_tuple in vf_tuple_list])
