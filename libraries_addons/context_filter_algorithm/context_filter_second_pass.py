"""

"""
from libraries_addons.utils_libraries_addons import *
from mains_tool.utils_general import default_number_of_rays_context_filter_second_pass


def select_non_obstructed_surfaces_of_context_HB_Model_for_target_LB_polyface3d(
        target_LB_polyface3d_extruded_footprint,context_HB_Model_list_to_test,full_urban_canopy_Pyvista_mesh,
        number_of_rays = default_number_of_rays_context_filter_second_pass):
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
                        context_HB_Face_surface_to_test=HB_Face_surface_to_test, full_urban_canopy_Pyvista_mesh=full_urban_canopy_Pyvista_mesh,
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

    # Make the list of ray to launch
    ray_list = None
    # Loop over all the rays
    for ray in ray_list :
        # Check if the ray is obstructed
        points, ind = full_urban_canopy_Pyvista_mesh.ray_trace(origin=ray[0], end_point=ray[1], first_point=False, plot=False)


        if ind.size == 0:  # no obstruction
            return False

    return True





def are_hb_faces_facing(hb_face_1, centroid_1, hb_face_2, centroid_2):
    """ Check with the normals if the surfaces are facing each other (and thus they can shade on each other) """
    # todo @Elie: update
    # normal vectors
    normal_1 = hb_face_1.normal
    normal_2 = hb_face_2.normal
    # vectors from centroid_2 to centroid_1
    vector_21 = centroid_1 - centroid_2  # operation possible with LB Point3D
    # dot product
    dot_product_sup = normal_2.dot(vector_21)
    dot_product_inf = normal_1.dot(vector_21)
    # vivibility/facing criteria  (same as PyviewFactor)
    if dot_product_sup > 0 and dot_product_inf < 0:
        return True
    else:
        return False


def ray_list_from_emitter_to_receiver(emitter, receiver, exclude_surface_from_ray=True, number_of_rays=3):
    """
        Args:
            emitter [dict]: dictionary with the following properties of the emitter surface {"hb_face_obj", "area",
                "centroid":(Point3D), "lower_corner_point3d":{"left","right"},"height"}
            receiver [dict]: dictionary with the following properties of the receiver surface {"hb_face_obj", "area",
                "centroid":(Point3D), "lower_corner_point3d":{"left","right"},"height"}
            exclude_surface_from_ray [boolean]: True the rays are slightly shorten not to intersect
                with the emitter and receiver surfaces

        Output:
            ray list, with ray tuple (start, stop)
    """
    # todo @Elie: update
    # z coordinate of the start and end of the rays
    z_receiver = receiver["elevation"] + receiver["height"]
    z_emitter = min([emitter["elevation"] + emitter["height"], z_receiver])
    # start vertices
    start_c = emitter["lower_corner_points"]["center"]
    start_l = emitter["lower_corner_points"]["left"]
    start_r = emitter["lower_corner_points"]["right"]
    start_c[2], start_l[2], start_r[2] = z_emitter, z_emitter, z_emitter  # correct the z coordinate
    # end vertices
    end_c = receiver["lower_corner_points"]["center"]
    end_l = receiver["lower_corner_points"]["left"]
    end_r = receiver["lower_corner_points"]["right"]
    end_c[2], end_l[2], end_r[2] = z_receiver, z_receiver, z_receiver  # correct the z coordinate

    # ray list
    ray_list = [
        (start_c, end_c),
        (start_c, end_l),
        (start_c, end_r),
        (start_l, end_l),
        (start_r, end_r),
        (start_l, end_c),
        (start_r, end_c),
        (start_l, end_r),
        (start_r, end_l),
    ]
    if exclude_surface_from_ray:
        for i in range(number_of_rays):
            ray_list[i] = excluding_surfaces_from_ray(start=ray_list[i][0], end=ray_list[i][1])
    return ray_list[:number_of_rays]


def excluding_surfaces_from_ray(start, end):
    """
        Return the start and end point of a ray reducing slightly the distance between the vertices to prevent
        considering the sender and receiver in the raytracing obstruction detection
    """
    # todo @Elie: update
    ray_vector = end - start
    unit_vector = ray_vector / np.linalg.norm(ray_vector)  # normalize the vector with it's norm
    # Move the ray boundaries
    new_start = start + unit_vector * 0.05  # move the start vertex by 10cm on the toward the end vertex
    new_end = end - unit_vector * 0.05  # move the end vertex by 10cm on the toward the start vertex

    return new_start, new_end


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
        LB_Face3D_list.extend(list(LB_polyface3d.faces)) # add the faces of the polyface3d to the list, need to use list()
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


