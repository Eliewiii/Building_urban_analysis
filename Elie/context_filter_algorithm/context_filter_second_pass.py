"""

"""
from libraries_addons.utils_libraries_addons import *
from Elie.context_filter_algorithm.utils_context_filter import *

from mains_tool.utils_general import default_number_of_rays_context_filter_second_pass


def select_non_obstructed_surfaces_of_context_HB_Model_for_target_LB_polyface3d(
        target_LB_polyface3d_extruded_footprint, context_HB_Model_list_to_test, full_urban_canopy_Pyvista_mesh,
        number_of_rays=default_number_of_rays_context_filter_second_pass):
    """
    Select the context surfaces that will be used for the shading simulation of the current target building.
    :param target_LB_polyface3d_extruded_footprint: LB polyface3d of the target building
    :param context_HB_Model_list_to_test: list of HB model of the context building to test
    :param full_urban_canopy_Pyvista_mesh: Pyvista mesh containing the envelopes of all the in the urban canopy
    :param number_of_rays: number of rays to be used for the ray tracing to check if the context surfaces are obstructed
    :return HB_Face_list_kept :
    """
    # Initialization
    non_obstructed_HB_Face_list = []
    # Loop through the context HB model
    for context_HB_Model_to_test in context_HB_Model_list_to_test:
        # Loop through the rooms of the context HB model
        for HB_Room in context_HB_Model_to_test.rooms:
            # Loop through the faces of the context HB model
            for HB_Face_surface_to_test in HB_Room.faces:
                if not is_HB_Face_context_surface_obstructed_for_target_LB_polyface3d(
                        target_LB_polyface3d_extruded_footprint=target_LB_polyface3d_extruded_footprint,
                        context_HB_Face_surface_to_test=HB_Face_surface_to_test,
                        full_urban_canopy_Pyvista_mesh=full_urban_canopy_Pyvista_mesh,
                        number_of_rays=number_of_rays):
                    # If the context surface is not obstructed, add it to the list of non-obstructed surfaces
                    non_obstructed_HB_Face_list.append(HB_Face_surface_to_test)

    return non_obstructed_HB_Face_list


def is_HB_Face_context_surface_obstructed_for_target_LB_polyface3d(target_LB_polyface3d_extruded_footprint,
                                                                   context_HB_Face_surface_to_test,
                                                                   full_urban_canopy_Pyvista_mesh,
                                                                   number_of_rays=default_number_of_rays_context_filter_second_pass):
    """
    Check if the context surface is obstructed for the target building
    :param target_LB_polyface3d_extruded_footprint: LB polyface3d of the target building
    :param context_HB_Face_surface_to_test: HB face of the context surface to test
    :param full_urban_canopy_Pyvista_mesh: Pyvista mesh containing the envelopes of all the in the urban canopy
    :param number_of_rays: number of rays to be used for the ray tracing to check if the context surfaces are obstructed
    :return  :
    """
    # todo @Elie : to check
    # Loop over all the Face3D of the LB Polyface3D of the target building
    for target_LB_Face3D in list(target_LB_polyface3d_extruded_footprint.faces):
        # Check if the normal of the target LB Face3D is vertical (ground or roof) and if the context surface is facing it
        if not is_vector3D_vertical(target_LB_Face3D.normal) and are_HB_Face_or_LB_Face3D_facing(target_LB_Face3D,
                                                                                                 context_HB_Face_surface_to_test):
            # Check if the context surface is obstructed for the target building
            if is_HB_Face_context_surface_obstructed_for_target_LB_Face3D(target_LB_Face3D=target_LB_Face3D,
                                                                          context_HB_Face_surface_to_test=context_HB_Face_surface_to_test,
                                                                          full_urban_canopy_Pyvista_mesh=full_urban_canopy_Pyvista_mesh,
                                                                          number_of_rays=number_of_rays):
                return False

    return True


def is_HB_Face_context_surface_obstructed_for_target_LB_Face3D(target_LB_Face3D,
                                                               context_HB_Face_surface_to_test,
                                                               full_urban_canopy_Pyvista_mesh,
                                                               number_of_rays=default_number_of_rays_context_filter_second_pass):
    """
    Check if the context surface is obstructed for the target building
    :param target_LB_polyface3d_extruded_footprint: LB polyface3d of the target building
    :param context_HB_Face_surface_to_test: HB face of the context surface to test
    :param full_urban_canopy_Pyvista_mesh: Pyvista mesh containing the envelopes of all the in the urban canopy
    :param number_of_rays: number of rays to be used for the ray tracing to check if the context surfaces are obstructed
    :return  :
    """
    # todo @Elie : to finish
    # Make the list of ray to launch
    ray_list = ray_list_from_emitter_to_receiver(face_emitter=target_LB_Face3D,
                                                 face_receiver=context_HB_Face_surface_to_test,
                                                 exclude_surface_from_ray=True, number_of_rays=number_of_rays)
    # Loop over all the rays
    for ray in ray_list:
        # Check if the ray is obstructed
        points, ind = full_urban_canopy_Pyvista_mesh.ray_trace(origin=ray[0], end_point=ray[1], first_point=False,
                                                               plot=False)

        if ind.size == 0:  # no obstruction
            return False

    return True


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


def ray_list_from_emitter_to_receiver(face_emitter, face_receiver, exclude_surface_from_ray=True, number_of_rays=3):
    """
        Args:

        Output:
            ray list, with ray tuple (start, stop)
    """
    # todo @Elie: check if it works
    # Check the type of the input, could be either a Ladybug Face3D or a Honeybee Face for more flexibility
    if isinstance(face_emitter,Face3D):
        emitter_Face3D=face_emitter
    elif isinstance(face_emitter,Face):
        emitter_Face3D=face_emitter.geometry
    else:
        raise TypeError("face_emitter should be a Ladybug Face3D or a Honeybee Face object")

    if isinstance(face_receiver,Face3D):
        receiver_Face3D=face_receiver
    elif isinstance(face_receiver,Face):
        receiver_Face3D=face_receiver.geometry
    else:
        raise TypeError("face_receiver should be a Ladybug Face3D or a Honeybee Face object")

    # z coordinate of the start and end of the rays
    z_receiver = receiver_Face3D.max.z  # maximum z coordinate of the max (Point3D) of the Face receiver
    z_emitter = min([emitter_Face3D.max.z, z_receiver])
    # start vertices, numpy arrays
    start_point_l = convert_Point3D_to_numpy_array(emitter_Face3D.lower_left_corner)
    start_point_r = convert_Point3D_to_numpy_array(emitter_Face3D.lower_right_corner)
    start_point_c = (start_point_l+start_point_r)/2.
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


# def ray_list_from_emitter_to_receiver_old(face_emitter, face_receiver, exclude_surface_from_ray=True, number_of_rays=3):
#     """
#         Args:
#
#         Output:
#             ray list, with ray tuple (start, stop)
#     """
#     # todo @Elie: update
#     # z coordinate of the start and end of the rays
#     z_receiver = receiver["elevation"] + receiver["height"]
#     z_emitter = min([emitter["elevation"] + emitter["height"], z_receiver])
#     # start vertices
#     start_c = emitter["lower_corner_points"]["center"]
#     start_l = emitter["lower_corner_points"]["left"]
#     start_r = emitter["lower_corner_points"]["right"]
#     start_c[2], start_l[2], start_r[2] = z_emitter, z_emitter, z_emitter  # correct the z coordinate
#     # end vertices
#     end_c = receiver["lower_corner_points"]["center"]
#     end_l = receiver["lower_corner_points"]["left"]
#     end_r = receiver["lower_corner_points"]["right"]
#     end_c[2], end_l[2], end_r[2] = z_receiver, z_receiver, z_receiver  # correct the z coordinate
#
#     # ray list
#     ray_list = [
#         (start_c, end_c),
#         (start_c, end_l),
#         (start_c, end_r),
#         (start_l, end_l),
#         (start_r, end_r),
#         (start_l, end_c),
#         (start_r, end_c),
#         (start_l, end_r),
#         (start_r, end_l),
#     ]
#     if exclude_surface_from_ray:
#         for i in range(number_of_rays):
#             ray_list[i] = excluding_surfaces_from_ray(start=ray_list[i][0], end=ray_list[i][1])
#     return ray_list[:number_of_rays]


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


def adjust_lower_corners(pt_left, pt_right):
    """
        move slightly the vertices to launch the rays from so that surfaces on corner will be detected as well
        pt_1 [Point3D]: point left
        pt_2 [Point3D]: point right
    """
    # todo @Elie: update and check what's the purpose of thid function again, not sure what it does, think it prevent surfaces on corners from being selected
    vector = pt_left - pt_right
    unit_vector = vector / np.linalg.norm(vector)
    new_point_left = pt_left - unit_vector * 0.1
    new_point_right = pt_right + unit_vector * 0.1
    return ([new_point_left, new_point_right])


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


def convert_Point3D_to_numpy_array(pt_3d):
    """ Convert LB Point3D to numpy array """

    return (np.array([pt_3d.x, pt_3d.y, pt_3d.z]))