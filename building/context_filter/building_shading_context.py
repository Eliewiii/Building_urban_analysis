"""
BuildingShadingContext class, used to perform and store the result of the context filtering for shading computation using the 2 pass filtering method
"""
from building.context_filter.building_context import BuildingContext

from building.context_filter.utils_functions_context_filter import is_vector3D_vertical, are_HB_Face_or_LB_Face3D_facing,ray_list_from_emitter_to_receiver

possible_numbers_of_rays_list = [1, 3, 6, 9]


class BuildingShadingContext(BuildingContext):
    """ todo """

    def __init__(self, min_VF_criterion, number_of_rays):
        """ todo """
        super().__init__(min_VF_criterion=min_VF_criterion)  # inherit from all the attributes of the super class
        self.number_of_rays = self.set_number_of_rays(number_of_rays)
        self.hb_face_context_list = []

    def set_number_of_rays(self, number_of_rays):
        """ todo """
        if isinstance(number_of_rays, int) and number_of_rays in possible_numbers_of_rays_list:
            self.number_of_rays = number_of_rays
        else:
            self.number_of_rays = None

    def select_non_obstructed_context_faces_with_ray_tracing(self, target_LB_polyface3d_extruded_footprint,
                                                             context_HB_Model_list_to_test,
                                                             full_urban_canopy_Pyvista_mesh):
        """"""
        self.hb_face_context_list = self.select_non_obstructed_surfaces_of_context_HB_Model_for_target_LB_polyface3d(
            target_LB_polyface3d_extruded_footprint, context_HB_Model_list_to_test, full_urban_canopy_Pyvista_mesh,
            number_of_rays=self.number_of_rays)

    def select_non_obstructed_surfaces_of_context_HB_Model_for_target_LB_polyface3d(self,
                                                                                    target_LB_polyface3d_extruded_footprint,
                                                                                    context_HB_Model_list_to_test,
                                                                                    full_urban_canopy_Pyvista_mesh,
                                                                                    number_of_rays):
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
                    if not self.is_HB_Face_context_surface_obstructed_for_target_LB_polyface3d(
                            target_LB_polyface3d_extruded_footprint=target_LB_polyface3d_extruded_footprint,
                            context_HB_Face_surface_to_test=HB_Face_surface_to_test,
                            full_urban_canopy_Pyvista_mesh=full_urban_canopy_Pyvista_mesh,
                            number_of_rays=number_of_rays):
                        # If the context surface is not obstructed, add it to the list of non-obstructed surfaces
                        non_obstructed_HB_Face_list.append(HB_Face_surface_to_test)

        return non_obstructed_HB_Face_list

    def is_HB_Face_context_surface_obstructed_for_target_LB_polyface3d(self, target_LB_polyface3d_extruded_footprint,
                                                                       context_HB_Face_surface_to_test,
                                                                       full_urban_canopy_Pyvista_mesh,
                                                                       number_of_rays):
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
                if self.is_HB_Face_context_surface_obstructed_for_target_LB_Face3D(target_LB_Face3D=target_LB_Face3D,
                                                                                   context_HB_Face_surface_to_test=context_HB_Face_surface_to_test,
                                                                                   full_urban_canopy_Pyvista_mesh=full_urban_canopy_Pyvista_mesh,
                                                                                   number_of_rays=number_of_rays):
                    return False

        return True

    @staticmethod
    def is_HB_Face_context_surface_obstructed_for_target_LB_Face3D(target_LB_Face3D,
                                                                   context_HB_Face_surface_to_test,
                                                                   full_urban_canopy_Pyvista_mesh,
                                                                   number_of_rays):
        """
        Check if the context surface is obstructed for the target building
        :param target_LB_Face3D: LB polyface3d of the target building
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
