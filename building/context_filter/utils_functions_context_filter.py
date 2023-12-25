"""
todo @Elie
"""
import numpy as np
import pyvista as pv

from math import sqrt, atan, log, pi

from ladybug_geometry.geometry3d.face import Face3D
from ladybug_geometry.geometry3d.polyface import Polyface3D
from honeybee.face import Face
from honeybee.model import Model
from honeybee.boundarycondition import Outdoors, Ground


def is_vector3d_vertical(vector3d):
    if vector3d.x == 0 and vector3d.y == 0:
        return True
    else:
        return False


def is_roof_lower_than_face_emitter(face_emitter, roof_face):
    """
    Check if the roof is higher than the face emitter, in that case the roof cannot shade the face emitter
    :param roof_face: Honeybee Face or Ladybug Face3D
    :param face_emitter: Honeybee Face or Ladybug Face3D
    """

    # Check the type of the input, could be either a Ladybug Face3D or a Honeybee Face for more flexibility
    if isinstance(face_emitter, Face3D):
        emitter_face3d = face_emitter
    elif isinstance(face_emitter, Face):
        emitter_face3d = face_emitter.geometry
    else:
        raise TypeError("face_emitter should be a Ladybug Face3D or a Honeybee Face object")

    if isinstance(roof_face, Face3D):
        receiver_face3d = roof_face
    elif isinstance(roof_face, Face):
        receiver_face3d = roof_face.geometry
    else:
        raise TypeError("face_receiver should be a Ladybug Face3D or a Honeybee Face object")

    # z coordinate of the start and end of the rays
    z_receiver = receiver_face3d.max.z  # maximum z coordinate of the max (Point3D) of the Face receiver
    z_emitter = emitter_face3d.max.z

    if z_receiver < z_emitter:
        return True
    else:
        return False


def convert_point3d_to_list(point3d):
    # todo @Elie move this function to utils_libraries_addons in a adequate file
    return [point3d.x, point3d.y, point3d.z]


def convert_point3d_to_numpy_array(pt_3d):
    """ Convert Ladybug Point3D to numpy array """

    return (np.array([pt_3d.x, pt_3d.y, pt_3d.z]))


def make_pyvista_polydata_from_hb_face_or_lb_face3d(face_object):
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


def make_pyvista_polydata_from_hb_face_or_lb_face3d_list(face_list):
    """ Convert the context hb face to a polydata Pyvista mesh  """

    if face_list != []:
        # Initialize mesh
        pyvista_polydata_mesh = make_pyvista_polydata_from_hb_face_or_lb_face3d(face_list[0])
        # concatenate the other faces to the mesh
        for face_obj in face_list[1:]:
            pyvista_polydata_mesh = pyvista_polydata_mesh + make_pyvista_polydata_from_hb_face_or_lb_face3d(face_obj)

        return pyvista_polydata_mesh

    else:
        return []


def make_pyvista_polydata_from_list_of_hb_model_and_lb_polyface3d(hb_model_and_lb_polyface3d_list):
    """
    Convert a list of Honeybee Model and Ladybug Polyface3D to a unified Pyvista Polydata mesh.
    The function is useful to make a Pyvista mesh of all the context buildings, but can be used with LBT objects only.
    :param hb_model_and_lb_polyface3d_list: list of Honeybee Model and Ladybug Polyface3D
    :return pyvista_polydata_mesh: Pyvista Polydata mesh
    """
    # list that wil contain the faces from the Honeybee Model and the Ladybug Polyface3D.
    # They can be either LB Face3D or HB Face objects
    list_of_faces_objects = []
    # Loop over all the elements of the list
    for lbt_obj in hb_model_and_lb_polyface3d_list:
        if isinstance(lbt_obj, Polyface3D):  # The attribute are the same for both
            list_of_faces_objects.extend(list(lbt_obj.faces))
        elif isinstance(lbt_obj, Model):
            hb_model_face_list = list(lbt_obj.faces)
            # Select only faces with outdoor boundary condition
            for hb_face in hb_model_face_list:
                if isinstance(hb_face.boundary_condition, Outdoors) or isinstance(hb_face.boundary_condition, Ground):
                    list_of_faces_objects.append(hb_face)
        else:
            raise TypeError("The object {} is not a Honeybee Model or a Ladybug Polyface3D, it cannot be handled "
                            "by the context filter".format(lbt_obj.identifier))
    # Convert the list of faces to a Pyvista Polydata mesh
    pyvista_polydata_mesh = make_pyvista_polydata_from_hb_face_or_lb_face3d_list(face_list=list_of_faces_objects)

    return pyvista_polydata_mesh


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


def ray_list_from_emitter_to_receiver(face_emitter, face_receiver, exclude_surface_from_ray=True,
                                      lower_ray_z_axis=True, number_of_rays=3):
    """
        Args:
        todo @Elie
        Output:
            ray list, with ray tuple (start, stop)
    """
    # todo @Elie: check if it works
    # Check the type of the input, could be either a Ladybug Face3D or a Honeybee Face for more flexibility
    if isinstance(face_emitter, Face3D):
        emitter_face3d = face_emitter
    elif isinstance(face_emitter, Face):
        emitter_face3d = face_emitter.geometry
    else:
        raise TypeError("face_emitter should be a Ladybug Face3D or a Honeybee Face object")

    if isinstance(face_receiver, Face3D):
        receiver_face3d = face_receiver
    elif isinstance(face_receiver, Face):
        receiver_face3d = face_receiver.geometry
    else:
        raise TypeError("face_receiver should be a Ladybug Face3D or a Honeybee Face object")

    # z coordinate of the start and end of the rays
    z_receiver = receiver_face3d.max.z  # maximum z coordinate of the max (Point3D) of the Face receiver
    z_emitter = min([emitter_face3d.max.z, z_receiver])
    # start vertices, numpy arrays
    start_point_l = convert_point3d_to_numpy_array(emitter_face3d.lower_left_corner)
    start_point_r = convert_point3d_to_numpy_array(emitter_face3d.lower_right_corner)
    start_point_c = (start_point_l + start_point_r) / 2.
    start_point_l[2], start_point_l[2], start_point_c[
        2] = z_emitter, z_emitter, z_emitter  # correct the z coordinate
    # end vertices, numpy arrays
    end_point_l = convert_point3d_to_numpy_array(receiver_face3d.lower_left_corner)
    end_point_r = convert_point3d_to_numpy_array(receiver_face3d.lower_right_corner)
    end_point_c = (end_point_l + end_point_r) / 2.
    end_point_l[2], end_point_l[2], end_point_c[
        2] = z_receiver, z_receiver, z_receiver  # correct the z coordinate

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

    correct_rays(ray_list=ray_list, face_receiver=face_receiver, exclude_surface_from_ray=exclude_surface_from_ray,
                 lower_ray_z_axis=lower_ray_z_axis)

    # if exclude_surface_from_ray:
    #     for i in range(number_of_rays):
    #         ray_list[i] = excluding_surfaces_from_ray(start_point=ray_list[i][0], end_point=ray_list[i][1])
    # if lower_ray_z_axis:  # todo @Elie: DO SOMETHING ABOUT THIS
    #     for i in range(number_of_rays):
    #         ray_list[i] = (ray_list[i][0] - np.array([0, 0, 0.1]), ray_list[i][1] - np.array([0, 0, 0.1]))

    return ray_list[:number_of_rays]


def are_hb_face_or_lb_face3d_facing(face_emitter, face_receiver):
    """ Check with the normals if the surfaces are facing each other (and thus they can shade on each other)
    :param face_emitter: Honeybee Face or Ladybug Face3D
    :param face_receiver: Honeybee Face or Ladybug Face3D
    :return: True if the surfaces are facing each other, False otherwise
    Credit: highly inspired from the PyviewFactor code
    """
    # Special treatment for roofs as we use the center of the facade to check, and it cannot work if the roof is higher
    # than the centroid of the facade. If there is an obstruction it will be discarded by the ray tracing
    if is_vector3d_vertical(face_receiver.normal) and face_receiver.normal.z > 0:
        if is_roof_lower_than_face_emitter(face_emitter=face_emitter,roof_face=face_receiver):
            return True
        else:
            return False
    # centroids
    centroid_1 = get_centroid_of_hb_face_and_lb_face3d(face_emitter)
    centroid_2 = get_centroid_of_hb_face_and_lb_face3d(face_receiver)
    # normal vectors
    normal_1 = face_emitter.normal
    normal_2 = face_receiver.normal
    # vectors from centroid_2 to centroid_1
    vector_21 = centroid_1 - centroid_2  # operation possible with Ladybug Point3D
    # dot product
    dot_product_sup = normal_2.dot(vector_21)
    dot_product_inf = normal_1.dot(vector_21)
    # visibility/facing criteria  (same as PyviewFactor)
    if dot_product_sup > 0 and dot_product_inf < 0:
        return True
    else:
        return False


def correct_rays(ray_list, face_receiver, exclude_surface_from_ray=True, lower_ray_z_axis=True):
    """ Correct the rays to avoid considering the sender and receiver in the raytracing obstruction detection
        :param ray_list: list of rays
        :param face_receiver: Honeybee Face or Ladybug Face3D
        :param exclude_surface_from_ray: bool, True if the surfaces should be excluded from the ray
        :param lower_ray_z_axis: bool, True if the z axis of the ray should be lowered
        :return: corrected ray list
        """
    number_of_rays = len(ray_list)

    if exclude_surface_from_ray:
        for i in range(number_of_rays):
            new_start_point, new_end_point = excluding_surfaces_from_ray(start_point=ray_list[i][0],
                                                                         end_point=ray_list[i][1])
            new_start_point[2], new_end_point[2] = ray_list[i][0][2], ray_list[i][1][
                2]  # correct the z coordinate. it does not influence here
            ray_list[i] = (new_start_point, new_end_point)
            if is_vector3d_vertical(face_receiver.normal):
                ray_list[i] = (ray_list[i][0] + np.array([0, 0, 0.1]), ray_list[i][1] + np.array([0, 0, 0.1]))
    if lower_ray_z_axis:  # todo @Elie: DO SOMETHING ABOUT THIS
        for i in range(number_of_rays):
            if not is_vector3d_vertical(face_receiver.normal):
                ray_list[i] = (ray_list[i][0], ray_list[i][1] - np.array([0, 0, 0.1]))


def get_centroid_of_hb_face_and_lb_face3d(face):
    """

    """
    if isinstance(face, Face3D):
        return face.centroid
    elif isinstance(face, Face):
        return face.geometry.centroid
    else:
        raise TypeError("face should be a Ladybug Face3D or a Honeybee Face object")


def plot_ray_and_surface(ray, face_emitter, context, ind):
    """
    from building.context_filter.utils_functions_context_filter import plot_ray_and_surface
    plot_ray_and_surface(ray=ray, face_emitter=target_lb_face3d, context=full_urban_canopy_pyvista_mesh, ind=ind)
    """

    ray_3D = pv.PolyData(
        np.array([ray[0], ray[1], [ray[1][0], ray[1][1], ray[1][2] + 1.], [ray[0][0], ray[0][1], ray[0][2] + 1.]]),
        [4, 0, 1, 2, 3])
    pv_emitter = make_pyvista_polydata_from_hb_face_or_lb_face3d(face_emitter)
    context_2 = context.copy()
    context_2 = context_2 + ray_3D + pv_emitter
    print(ind)
    context_2.plot(show_edges=True)
