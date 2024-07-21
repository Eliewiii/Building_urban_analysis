"""
Test the function to compute the view factor between two rectangles with Radiance
"""

import numpy as np

import pyvista as pv
import pyviewfactor as pvf

from current_development.mvfc_demonstration.utils_to_radiance import compute_vf_between_2_rectangles_with_radiance

# first define a rectangle...
pointa = [1, 0, 0]
pointb = [1, 1, 0]
pointc = [0, 1, 0]
pointd = [0, 0, 0]
rectangle = pv.Rectangle([pointa, pointb, pointc])
print(type(np.array(rectangle.points)))



# ... then a triangle
pointa = [1, 0, 1]
pointb = [1, 1, 1]
pointc = [0, 1, 1]
liste_pts = [pointa, pointb, pointc]
liste_pts.reverse() # let us put the normal the other way around (facing the rectangle)
triangle = pv.Rectangle(liste_pts) # ... done with geometry.

vf_pvf = pvf.compute_viewfactor(rectangle, triangle)

path_temp_folder = r"..\file_temp"
vf_radiance = compute_vf_between_2_rectangles_with_radiance(rectangle, triangle, path_temp_folder,nb_rays=10000)

print (vf_pvf, vf_radiance)