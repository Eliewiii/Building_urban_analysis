"""

"""

from current_development.mvfc_demonstration.utils_random_rectangle_generation import generate_random_rectangles
from current_development.mvfc_demonstration.utils_mvfc_demonstration import computes_vf_betweem_2_rectangles
from current_development.mvfc_demonstration.test.plot_pyvista_obj import *

n_rectangles = 1000

vf_tuple_list = []
exceptions = []

for i in range(n_rectangles):
    ref_rectangle, random_rectangle = generate_random_rectangles(min_size=0.1, max_size=10,max_distance_factor=5)
    vf, supremum_vf = computes_vf_betweem_2_rectangles(ref_rectangle, random_rectangle)
    vf_tuple_list.append((vf, supremum_vf,True if supremum_vf>= vf else False))
    if supremum_vf <= vf:
        print(f"VF: {vf} , Supremum VF: {supremum_vf}")
        exceptions.append((ref_rectangle, random_rectangle))
        if vf>0.001:
            plot_rectangle([ref_rectangle,random_rectangle],['blue',"red"])


print([result_tuple[2] for result_tuple in vf_tuple_list])


