import pyvista as pv
import pyviewfactor as pvf

# first define a rectangle...
pointa = [1, 0, 0]
pointb = [1, 1, 0]
pointc = [0, 1, 0]
pointd = [0, 0, 0]
rectangle = pv.Rectangle([pointa, pointb, pointc])
print(rectangle.center)

# ... then a triangle
pointa = [1, 0, 1]
pointb = [1, 1, 1]
pointc = [0, 1, 1]
liste_pts = [pointa, pointb, pointc]
liste_pts.reverse() # let us put the normal the other way around (facing the rectangle)
triangle = pv.Rectangle(liste_pts) # ... done with geometry.

# preliminary check for visibility
if pvf.get_visibility(rectangle , triangle):
    F = pvf.compute_viewfactor(rectangle, triangle)
    print("View factor from triangle to rectangle = ", F)
else:
    print("Not facing each other")
