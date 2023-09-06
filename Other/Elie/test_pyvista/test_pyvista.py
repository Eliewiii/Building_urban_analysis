import pyvista as pv
from pyviewfactor import compute_viewfactor
from multiprocessing import Pool

from time import time

# Initialization #

# rectangle
point_a = [1., 0., 0.]
point_b = [1., 1., 0.]
point_c = [0., 1., 0.]
point_d = [0., 0., 0.]
rectangle_1 = pv.Rectangle([point_a, point_b, point_c, point_d])

rectangle_2 = rectangle_1.copy()
rectangle_2.translate([0, 0, 1], inplace=True)

rectangle_3 = rectangle_1.copy()
rectangle_3.translate([0, 0, 2], inplace=True)

start = rectangle_1.cell_centers().points[0]
stop = rectangle_3.cell_centers().points[0]


# nb_it=100000
# dt=time()
# for i in range(nb_it):
#     points, ind = rectangle_2.ray_trace(start, stop)
#
# dt=time()-dt
# print(points,dt)
if __name__ == '__main__':
    nb_process = 1
    nb_it=3000
    dt=time()
    p=Pool(nb_process)
    p.starmap(compute_viewfactor,[(rectangle_1,rectangle_2) for i in range(nb_it)],chunksize=10)
    p.close()
    p.join()
    # for i in range(nb_it):
    #     h=pvf.compute_viewfactor(rectangle_1, pvf.compute_viewfactor)
    #
    dt=time()-dt
    print(dt)

# print(rectangle_1,rectangle_2)












