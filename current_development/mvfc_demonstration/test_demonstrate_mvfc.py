"""

"""

import pyvista as pv

from utils_mvfc_demonstration import computes_vf_betweem_2_rectangles

# define first rectangle
pointa = [1, 0, 0]
pointb = [1, 1, 0]
pointc = [0, 1, 0]
pointd = [0, 0, 0]
rectangle_1 = pv.Rectangle([pointa, pointb, pointc])

# define second rectangle
a=2
pointa = [1, 0, a]
pointb = [1, 1, a]
pointc = [0, 1, a]
pointd = [0, 0, a]
list_pts = [pointa, pointb, pointc]
list_pts.reverse()
rectangle_2 = pv.Rectangle(list_pts)

# compute view factor between the 2 rectangles
vf, supremum_vf = computes_vf_betweem_2_rectangles(rectangle_1, rectangle_2)
print(f"View factor between the 2 rectangles: {vf}")
print(f"Supremum view factor between the 2 rectangles: {supremum_vf}")
