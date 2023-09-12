"""
BuildingShadingContext class, used to perform and store the result of the context filtering for shading computation using the 2 pass filtering method
"""
import logging

from building.context_filter.building_context import BuildingContext

from building.context_filter.utils_functions_context_filter import is_vector3d_vertical, \
    are_hb_face_or_lb_face3d_facing, ray_list_from_emitter_to_receiver

user_logger = logging.getLogger("user")
dev_logger = logging.getLogger("dev")

possible_numbers_of_rays_list = [1, 3, 6, 9]


class BuildingShadingContext(BuildingContext):
    """ todo """

    def __init__(self, min_vf_criterion, number_of_rays):
        """ todo """
        super().__init__(min_vf_criterion=min_vf_criterion)  # inherit from all the attributes of the super class
        self.number_of_rays = self.set_number_of_rays(number_of_rays)
        self.hb_shade_context_list = []

    def set_number_of_rays(self, number_of_rays):
        """ todo """
        if isinstance(number_of_rays, int) and number_of_rays in possible_numbers_of_rays_list:
            self.number_of_rays = number_of_rays
        else:
            self.number_of_rays = 3
            user_logger.warning(f"The number of ray inputted was not valid, the number of ray was set to 3")

    def select_non_obstructed_context_faces_with_ray_tracing(self, target_lb_polyface3d_extruded_footprint,
                                                             context_hb_model_list_to_test,
                                                             full_urban_canopy_pyvista_mesh):
        """"""
        hb_face_context_list = self.select_non_obstructed_surfaces_of_context_hb_model_for_target_lb_polyface3d(
            target_lb_polyface3d_extruded_footprint, context_hb_model_list_to_test, full_urban_canopy_pyvista_mesh,
            number_of_rays=self.number_of_rays)
        self.hb_shade_context_list = None  # todo : Transform the faces into shades

    def select_non_obstructed_surfaces_of_context_hb_model_for_target_lb_polyface3d(self,
                                                                                    target_lb_polyface3d_extruded_footprint,
                                                                                    context_hb_model_list_to_test,
                                                                                    full_urban_canopy_pyvista_mesh,
                                                                                    number_of_rays):
        """
        Select the context surfaces that will be used for the shading simulation of the current target building.
        :param target_lb_polyface3d_extruded_footprint: Ladybug Polyface3D of the target building
        :param context_hb_model_list_to_test: list of Honeybee Model of the context building to test
        :param full_urban_canopy_pyvista_mesh: Pyvista Mesh containing the envelopes of all the in the urban canopy
        :param number_of_rays: number of rays to be used for the ray tracing to check if the context surfaces are obstructed
        :return hb_face_list_kept :
        """
        # Initialization
        non_obstructed_hb_face_list = []
        # Loop through the context hb model
        for context_hb_model_to_test in context_hb_model_list_to_test:
            # Loop through the rooms of the context Honeybee model
            for hb_Room in context_hb_model_to_test.rooms:
                # Loop through the faces of the context Honeybee model
                # todo !! don't use the face, use punched geometry of the faces ad the aperture
                for hb_face_surface_to_test in hb_Room.faces:
                    if not self.is_hb_face_context_surface_obstructed_for_target_lb_polyface3d(
                            target_lb_polyface3d_extruded_footprint=target_lb_polyface3d_extruded_footprint,
                            context_hb_face_surface_to_test=hb_face_surface_to_test,
                            full_urban_canopy_pyvista_mesh=full_urban_canopy_pyvista_mesh,
                            number_of_rays=number_of_rays):
                        # If the context surface is not obstructed, add it to the list of non-obstructed surfaces
                        non_obstructed_hb_face_list.append(hb_face_surface_to_test)

        return non_obstructed_hb_face_list

    def is_hb_face_context_surface_obstructed_for_target_lb_polyface3d(self, target_lb_polyface3d_extruded_footprint,
                                                                       context_hb_face_surface_to_test,
                                                                       full_urban_canopy_pyvista_mesh,
                                                                       number_of_rays):
        """
        Check if the context surface is obstructed for the target building
        :param target_lb_polyface3d_extruded_footprint: Ladybug Polyface3D of the target building
        :param context_hb_face_surface_to_test: Honeybee face of the context surface to test
        :param full_urban_canopy_pyvista_mesh: Pyvista Mesh containing the envelopes of all the in the urban canopy
        :param number_of_rays: number of rays to be used for the ray tracing to check if the context surfaces are obstructed
        :return  :
        """
        # todo @Elie : to check
        # Loop over all the Face3D of the Ladybug Polyface3D of the target building
        for target_lb_face3d in list(target_lb_polyface3d_extruded_footprint.faces):
            # Check if the normal of the target ladybug face3D is vertical (ground or roof) and if the context surface is facing it
            if not is_vector3d_vertical(target_lb_face3d.normal) and are_hb_face_or_lb_face3d_facing(target_lb_face3d,
                                                                                                     context_hb_face_surface_to_test):
                # Check if the context surface is obstructed for the target building
                if self.is_hb_face_context_surface_obstructed_for_target_lb_face3d(target_lb_face3d=target_lb_face3d,
                                                                                   context_hb_face_surface_to_test=context_hb_face_surface_to_test,
                                                                                   full_urban_canopy_pyvista_mesh=full_urban_canopy_pyvista_mesh,
                                                                                   number_of_rays=number_of_rays):
                    return False

        return True

    @staticmethod
    def is_hb_face_context_surface_obstructed_for_target_lb_face3d(target_lb_face3d,
                                                                   context_hb_face_surface_to_test,
                                                                   full_urban_canopy_pyvista_mesh,
                                                                   number_of_rays):
        """
        Check if the context surface is obstructed for the target building
        :param target_lb_face3d: Ladybug polyface3d of the target building
        :param context_hb_face_surface_to_test: Honeybee face of the context surface to test
        :param full_urban_canopy_pyvista_mesh: Pyvista Mesh containing the envelopes of all the in the urban canopy
        :param number_of_rays: number of rays to be used for the ray tracing to check if the context surfaces are obstructed
        :return  :
        """
        # todo @Elie : to finish
        # Make the list of ray to launch
        ray_list = ray_list_from_emitter_to_receiver(face_emitter=target_lb_face3d,
                                                     face_receiver=context_hb_face_surface_to_test,
                                                     exclude_surface_from_ray=True, number_of_rays=number_of_rays)
        # Loop over all the rays
        for ray in ray_list:
            # Check if the ray is obstructed
            points, ind = full_urban_canopy_pyvista_mesh.ray_trace(origin=ray[0], end_point=ray[1], first_point=False,
                                                                   plot=False)

            if ind.size == 0:  # no obstruction
                return False

        return True
