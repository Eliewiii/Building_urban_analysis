import pyvista as pv
import pyviewfactor as pvf
import numpy as np

# points = np.array(
#     [
#         [0.0480, 0.0349, 0.9982],
#         [0.0305, 0.0411, 0.9987],
#         [0.0207, 0.0329, 0.9992],
#         [0.0218, 0.0158, 0.9996],
#         [0.0377, 0.0095, 0.9992],
#         [0.0485, 0.0163, 0.9987],
#         [0.0572, 0.0603, 0.9965],
#         [0.0390, 0.0666, 0.9970],
#         [0.0289, 0.0576, 0.9979],
#         [0.0582, 0.0423, 0.9974],
#         [0.0661, 0.0859, 0.9941],
#         [0.0476, 0.0922, 0.9946],
#         [0.0372, 0.0827, 0.9959],
#         [0.0674, 0.0683, 0.9954],
#     ],
# )
#
#
# face_a = [6, 0, 1, 2, 3, 4, 5]
# face_b = [6, 6, 7, 8, 1, 0, 9]
# face_c = [6, 10, 11, 12, 7, 6, 13]
# faces = np.concatenate((face_a, face_b, face_c))
#
# mesh = pv.PolyData(points, faces)
# mesh.plot(show_edges=True, line_width=5)

# points = np.array(
#     [
#         [0.0480, 0.0349, 0.9982],
#         [0.0305, 0.0411, 0.9987],
#         [0.0207, 0.0329, 0.9992],
#         [0.0218, 0.0158, 0.9996],
#         [0.0377, 0.0095, 0.9992],
#         [0.0485, 0.0163, 0.9987],
#         [0.0572, 0.0603, 0.9965],
#         [0.0390, 0.0666, 0.9970],
#         [0.0289, 0.0576, 0.9979],
#         [0.0582, 0.0423, 0.9974],
#         [0.0661, 0.0859, 0.9941],
#         [0.0476, 0.0922, 0.9946],
#         [0.0372, 0.0827, 0.9959],
#         [0.0674, 0.0683, 0.9954],
#     ],
# )
#
#
# face_a = [6, 0, 1, 2, 3, 4, 5]
# face_b = [6, 6, 7, 8, 1, 0, 9]
# face_c = [6, 10, 11, 12, 7, 6, 13]
# faces = np.concatenate((face_a, face_b, face_c))
#
# mesh = pv.PolyData(points, faces)
# mesh.plot(show_edges=True, line_width=5)



points = np.array(
    [
        [0., 0., 0.],
        [0., 1., 0.],
        [1., 0., 0],
    ],
)

face = [3,0,1,2]

mesh_1 =pv.PolyData(points, face)

points = np.array(
    [
        [0., 0., 1.],
        [0., 1., 1.],
        [1., 0., 1.],

    ],
)
face = [3,0,1,2]

mesh_2 =pv.PolyData(points, face)

mesh = mesh_1+mesh_2

points = np.array(
    [
        [0., 0., 0.5],
        [0., 1., 0.5],
        [1., 0., 0.5],

    ],
)
face = [3,0,1,2]

mesh_3 =pv.PolyData(points, face)

points = np.array(
    [
        [0., 0., 0.7],
        [0., 1., 0.7],
        [1., 0., 0.7],

    ],
)
face = [3,1,0,2]

mesh_4 =pv.PolyData(points, face)

mesh = mesh_1+mesh_2+mesh_3+mesh_4

points = np.array(
    [
        [0., 0., 0.],
        [0., 0.01, 0.],
        [0., 0, 1],
        [0., 0.01, 1]

    ],
)
ray = [4,0,2,3,1]

mesh_5 = pv.PolyData(points, ray)

mesh_5.plot(show_edges=True)
# print (mesh)

print(mesh.ray_trace(np.array([0., 0., 0.0000000001]),np.array([0.1, 0.1, 0.2]),first_point=False,plot=True))

print(mesh_3.ray_trace(np.array([0., 0., -1.]),np.array([0.1, 0.1, 1.1]),first_point=False,plot=True))

print(pvf.get_visibility_raytrace(mesh_1,mesh_2,mesh_3))

# mesh.plot(show_edges=True, line_width=5)


# points = np.array(
#     [
#         [0.0480, 0.0349, 0.9982],
#         [0.0305, 0.0411, 0.9987],
#         [0.0207, 0.0329, 0.9992],
#         [0.0218, 0.0158, 0.9996],
#         [0.0377, 0.0095, 0.9992],
#         [0.0485, 0.0163, 0.9987],
#         [0.0572, 0.0603, 0.9965],
#         [0.0390, 0.0666, 0.9970],
#         [0.0289, 0.0576, 0.9979],
#         [0.0582, 0.0423, 0.9974],
#         [0.0661, 0.0859, 0.9941],
#         [0.0476, 0.0922, 0.9946],
#         [0.0372, 0.0827, 0.9959],
#         [0.0674, 0.0683, 0.9954],
#     ],
# )
#
#
# face_a = [6, 0, 1, 2, 3, 4, 5]
# face_b = [6, 6, 7, 8, 1, 0, 9]
# face_c = [6, 10, 11, 12, 7, 6, 13]
# faces = np.concatenate((face_a, face_b, face_c))
#
# mesh = pv.PolyData(points, faces)
# mesh.plot(show_edges=True, line_width=5)