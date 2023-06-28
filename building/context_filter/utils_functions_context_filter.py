from building.context_filter.utils_libraries_context_filter import *  # todo @ Ale is that ok if it's from my own imports ?

from honeybee.face import Face
from ladybug_geometry.geometry3d import Face3D


def is_vector3D_vertical(Vector3D):
    if Vector3D.x == 0 and Vector3D.y == 0:
        return True
    else:
        return False


def convert_Point3D_to_list(Point3D):
    # todo @Elie move this function to utils_libraries_addons in a adequate file
    return [Point3D.x, Point3D.y, Point3D.z]


def convert_Point3D_to_numpy_array(pt_3d):
    """ Convert LB Point3D to numpy array """

    return (np.array([pt_3d.x, pt_3d.y, pt_3d.z]))


def distance_between_LB_Point3d(pt_1, pt_2):
    """ Distance between 2 LB geometry Point3D """
    return sqrt((pt_1.x - pt_2.x) ** 2 + (pt_1.y - pt_2.y) ** 2 + (pt_1.z - pt_2.z) ** 2)


def majorized_VF_between_2_surfaces(Point3D_centroid_1, area_1, Point3D_centroid_2, area_2):
    """
        Maximal view factor between the 2 surface, in the optimal configuration described in the context paper
        the faces are lists with following format :  [LB_face_obj,area, centroid]
    """
    ## distance between the centroids
    d = distance_between_LB_Point3d(Point3D_centroid_1, Point3D_centroid_2)
    if d == 0:  # avoid cases when surfaces are overlapping
        d = 0.01
    ## width of the optimal squares
    W_1 = sqrt(area_1)
    W_2 = sqrt(area_2)
    ## intermediary variable for the computation
    w_1 = W_1 / d
    w_2 = W_2 / d
    x = w_2 - w_1
    y = w_2 + w_1
    p = (w_1 ** 2 + w_2 ** 2 + 2) ** 2
    q = (x ** 2 + 2) * (y ** 2 + 2)
    u = sqrt(x ** 2 + 4)
    v = sqrt(y ** 2 + 4)
    s = u * (x * atan(x / u) - y * atan(y / u))
    t = v * (x * atan(x / v) - y * atan(y / v))

    return 1 / (pi * w_1 ** 2) * (log(p / q) + s - t)


def make_Pyvista_Polydata_from_HB_Face_or_LB_Face3D(face_object):
    """
    Convert a Honeybee Face or Ladybug Face3D to a Pyvista PolyData mesh
    :param face_object:
    :return:
    """
    # todo @Elie: update if needed
    # Get the vertices of the face
    vertices = []  # initialize the list of vertices
    lb_vertex_list = face_object.vertices  # extract the ladybug-geometry Point3D vertices
    # format of the face expected by PyVista [number of vertices, index vertex 1, index vertex 2 ...] <=> [n, 0,1,2...]
    face = [len(lb_vertex_list)]
    # convert the vertices to a list of coordinates and add the vertices index to the face
    for index, vertex in enumerate(lb_vertex_list):
        vertices.append([vertex.x, vertex.y, vertex.z])  # add the coordinates of the vertices
        face.append(index)
    vertices = np.array(vertices)  # convert into numpy array, makes it faster for Pyvista to process

    return pv.PolyData(vertices, face)


def make_Pyvista_Polydata_from_HB_Face_or_LB_Face3D_list(face_list):
    """ Convert the context hb face to a polydata Pyvista mesh  """

    if face_list != []:
        # Initialize mesh
        Pyvista_Polydata_mesh = make_Pyvista_Polydata_from_HB_Face_or_LB_Face3D(face_list[0])
        # concatenate the other faces to the mesh
        for hb_face in face_list[1:]:
            PV_Polydata_mesh = PV_Polydata_mesh + make_Pyvista_Polydata_from_HB_Face_or_LB_Face3D(hb_face)

        return Pyvista_Polydata_mesh

    else:
        return []


def make_Pyvista_Polydata_from_LB_Polyface3D_list(LB_Polyface3D_list):
    """
    Convert a list of LB Polyface3D to a Pyvista Polydata mesh
    :param LB_Polyface3D_list: list of LB Polyface3D
    :return Pyvista_Polydata_mesh: Pyvista Polydata mesh
    """
    # todo @Elie: to test
    # todo LATER : maybe add some test before to avaoid errors
    # Make a list of all the faces in the Polyface3D
    LB_Face3D_list = []
    for LB_polyface3d in LB_Polyface3D_list:
        LB_Face3D_list.extend(
            list(LB_polyface3d.faces))  # add the faces of the polyface3d to the list, need to use list()
    # Convert the list of LB_Face3D to a Pyvista Polydata mesh
    Pyvista_Polydata_mesh = make_Pyvista_Polydata_from_HB_Face_or_LB_Face3D_list(face_list=LB_Face3D_list)

    return Pyvista_Polydata_mesh


def excluding_surfaces_from_ray(start_point, end_point):
    """
        Return the start and end point of a ray reducing slightly the distance between the vertices to prevent
        considering the sender and receiver in the raytracing obstruction detection
        :param start_point: numpy array, start point of the ray
        :param end_point: numpy array, end point of the ray
        :return: new_start_point, new_end_point: numpy arrays, new start and end points of the ray
    """
    # todo @Elie: update
    ray_vector = end_point - start_point
    unit_vector = ray_vector / np.linalg.norm(ray_vector)  # normalize the vector with it's norm
    # Move the ray boundaries
    new_start_point = start_point + unit_vector * 0.05  # move the start vertex by 5cm on the toward the end vertex
    new_end_point = end_point - unit_vector * 0.05  # move the end vertex by 5cm on the toward the start vertex

    return new_start_point, new_end_point


def ray_list_from_emitter_to_receiver(face_emitter, face_receiver, exclude_surface_from_ray=True, number_of_rays=3):
    """
        Args:

        Output:
            ray list, with ray tuple (start, stop)
    """
    # todo @Elie: check if it works
    # Check the type of the input, could be either a Ladybug Face3D or a Honeybee Face for more flexibility
    if isinstance(face_emitter, Face3D):
        emitter_Face3D = face_emitter
    elif isinstance(face_emitter, Face):
        emitter_Face3D = face_emitter.geometry
    else:
        raise TypeError("face_emitter should be a Ladybug Face3D or a Honeybee Face object")

    if isinstance(face_receiver, Face3D):
        receiver_Face3D = face_receiver
    elif isinstance(face_receiver, Face):
        receiver_Face3D = face_receiver.geometry
    else:
        raise TypeError("face_receiver should be a Ladybug Face3D or a Honeybee Face object")

    # z coordinate of the start and end of the rays
    z_receiver = receiver_Face3D.max.z  # maximum z coordinate of the max (Point3D) of the Face receiver
    z_emitter = min([emitter_Face3D.max.z, z_receiver])
    # start vertices, numpy arrays
    start_point_l = convert_Point3D_to_numpy_array(emitter_Face3D.lower_left_corner)
    start_point_r = convert_Point3D_to_numpy_array(emitter_Face3D.lower_right_corner)
    start_point_c = (start_point_l + start_point_r) / 2.
    start_point_l[2], start_point_l[2], start_point_c[2] = z_emitter, z_emitter, z_emitter  # correct the z coordinate
    # end vertices, numpy arrays
    end_point_l = convert_Point3D_to_numpy_array(receiver_Face3D.lower_left_corner)
    end_point_r = convert_Point3D_to_numpy_array(receiver_Face3D.lower_right_corner)
    end_point_c = (end_point_l + end_point_r) / 2.
    end_point_l[2], end_point_l[2], end_point_c[2] = z_receiver, z_receiver, z_emitter  # correct the z coordinate

    # ray list
    ray_list = [
        (start_point_c, end_point_c),
        (start_point_c, end_point_l),
        (start_point_c, end_point_r),
        (start_point_l, end_point_l),
        (start_point_r, end_point_r),
        (start_point_l, end_point_c),
        (start_point_r, end_point_c),
        (start_point_l, end_point_r),
        (start_point_r, end_point_l),
    ]
    if exclude_surface_from_ray:
        for i in range(number_of_rays):
            ray_list[i] = excluding_surfaces_from_ray(start=ray_list[i][0], end_point=ray_list[i][1])
    return ray_list[:number_of_rays]


def are_HB_Face_or_LB_Face3D_facing(face_1, face_2):
    """ Check with the normals if the surfaces are facing each other (and thus they can shade on each other)
    :param face_1: HB Face or LB Face3D
    :param face_2: HB Face or LB Face3D
    :return: True if the surfaces are facing each other, False otherwise
    Credit: highly inspired from the PyviewFactor code
    """
    # todo @Elie: update
    # centroids
    centroid_1 = face_1.centroid
    centroid_2 = face_2.centroid
    # normal vectors
    normal_1 = face_1.normal
    normal_2 = face_2.normal
    # vectors from centroid_2 to centroid_1
    vector_21 = centroid_1 - centroid_2  # operation possible with LB Point3D
    # dot product
    dot_product_sup = normal_2.dot(vector_21)
    dot_product_inf = normal_1.dot(vector_21)
    # visibility/facing criteria  (same as PyviewFactor)
    if dot_product_sup > 0 and dot_product_inf < 0:
        return True
    else:
        return False
