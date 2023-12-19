"""
BuildingShadingContext class, used to perform and store the result of the context filtering for shading computation using the 2 pass filtering method
"""
import logging

from honeybee.boundarycondition import Outdoors

from building.context_filter.building_context import BuildingContext

from building.context_filter.utils_functions_context_filter import is_vector3d_vertical, \
    are_hb_face_or_lb_face3d_facing, ray_list_from_emitter_to_receiver

user_logger = logging.getLogger("user")
dev_logger = logging.getLogger("dev")

possible_numbers_of_rays_list = [1, 3, 6, 9]


class BuildingShadingContext(BuildingContext):
    """ todo """

    def __init__(self):
        """ todo """
        super().__init__()  # inherit from all the attributes of the super class
        # Paramters
        self.number_of_rays = None
        self.consider_windows = None

        # Results
        self.shades_from_hb_model_list = []  # todo : change the name to shade_list_from_hb_model
        self.context_shading_hb_shade_dict = {}
        """
        We use a dictionary to store the shades of the context buildings. The keys are the building ids and the values 
        are a list of shades of the context buildings.
        """

        # Simualtion tracking
        self.second_pass_done = False

    def overwrite_filtering(self, overwrite_first_pass=False, overwrite_second_pass=False):
        """
        Overwrite the filtering of the BuildingShadingContext object
        :param overwrite_first_pass: boolean to overwrite the first pass of the context filtering. If the first pass is
        overwritten, it automatically overwrites the second pass
        :param overwrite_second_pass: boolean to overwrite the second pass of the context filtering
        """
        if overwrite_first_pass:
            self.context_building_id_list = []
            self.context_shading_hb_shade_list = []
            self.first_pass_done = False
            self.second_pass_done = False
        if overwrite_second_pass:
            self.context_shading_hb_shade_list = []
            self.second_pass_done = False

    def set_number_of_rays(self, number_of_rays):
        """ todo """
        if isinstance(number_of_rays, int) and number_of_rays in possible_numbers_of_rays_list:
            self.number_of_rays = number_of_rays
        else:
            self.number_of_rays = 3
            user_logger.warning(f"The number of ray inputted was not valid, the number of ray was set to 3")

    def set_consider_windows(self, consider_windows):
        """ todo """
        if isinstance(consider_windows, bool):
            self.consider_windows = consider_windows
        else:
            self.consider_windows = False
            user_logger.warning(f"The consider windows inputted was not valid, the consider windows was set to False")

    def get_hb_shades_from_hb_model(self, hb_model):
        """
        Extract the shades from the Honeybee Model and add them to context_shading_hb_shade_list attribute
        :param hb_model: Honeybee Model
        """
        self.shades_from_hb_model_list.extend(hb_model.shades)
        self.context_shading_hb_shade_list.extend(self.shades_from_hb_model_list)

    def select_non_obstructed_context_faces_with_ray_tracing(self, target_lb_polyface3d_extruded_footprint,
                                                             context_hb_model_list_to_test,
                                                             full_urban_canopy_pyvista_mesh, consider_windows=False,
                                                             keep_shades_from_hb_model=False):
        """"""
        hb_face_context_list = self.select_non_obstructed_surfaces_of_context_hb_model_for_target_lb_polyface3d(
            target_lb_polyface3d_extruded_footprint=target_lb_polyface3d_extruded_footprint,
            context_hb_model_list_to_test=context_hb_model_list_to_test,
            full_urban_canopy_pyvista_mesh=full_urban_canopy_pyvista_mesh,
            number_of_rays=self.number_of_rays, consider_windows=consider_windows)

        self.context_shading_hb_shade_list = None  # todo : Transform the faces into shades

        if not keep_shades_from_hb_model:
            self.shades_from_hb_model_list = []

    def select_non_obstructed_surfaces_of_context_hb_model_for_target_lb_polyface3d(self,
                                                                                    target_lb_polyface3d_extruded_footprint,
                                                                                    context_building_hb_model_list,
                                                                                    context_building_id_list,
                                                                                    full_urban_canopy_pyvista_mesh,
                                                                                    consider_windows=False):
        """
        Select the context surfaces that will be used for the shading simulation of the current target building.
        :param target_lb_polyface3d_extruded_footprint: Ladybug Polyface3D of the target building
        :param context_hb_model_list_to_test: list of Honeybee Model of the context building to test. It will be more efficient (for the algorithm efficiency as well as the shadiong computation in EnergyPlus) to use HB models with merged facades.
        :param full_urban_canopy_pyvista_mesh: Pyvista Mesh containing the envelopes of all the in the urban canopy
        :param number_of_rays: number of rays to be used for the ray tracing to check if the context surfaces are obstructed
        :return hb_face_list_kept :
        """
        # Initialization
        context_shading_hb_shade_dict= {}
        # Loop through the context hb model
        for context_hb_model,context_building_id in zip(context_building_hb_model_list,context_building_id_list):
            non_obstructed_hb_face_or_aperture_list = []
            # Loop through the rooms of the context Honeybee model
            for hb_Room in context_hb_model.rooms:
                # Loop through the faces of the context Honeybee model
                for hb_face_surface_to_test in hb_Room.faces:
                    """ Here the horizontal context surfaces are not discarded as they can reflect the sun light, 
                    even if they do not shade """
                    if isinstance(hb_face_surface_to_test.boundary_condition, Outdoors):
                        if not self.is_hb_face_context_surface_obstructed_for_target_lb_polyface3d(
                                target_lb_polyface3d_extruded_footprint=target_lb_polyface3d_extruded_footprint,
                                context_hb_face_surface_to_test=hb_face_surface_to_test,
                                full_urban_canopy_pyvista_mesh=full_urban_canopy_pyvista_mesh,
                                number_of_rays=self.number_of_rays):
                            # If the context surface is not obstructed, add it to the list of non-obstructed surfaces
                            non_obstructed_hb_face_or_aperture_list.append(hb_face_surface_to_test)
                        # Consider the windows
                        if consider_windows:
                            for hb_aperture in hb_face_surface_to_test.apertures:
                                # Make a copy of the window geometry
                                lb_face_window_geo = hb_aperture.geometry
                                # Move the windows in the direction of its normal by 1 cm
                                lb_face_window_geo = lb_face_window_geo.move(lb_face_window_geo.normal,
                                                                             0.01)  # todo : check if it is the right direction
                                if not self.is_hb_face_context_surface_obstructed_for_target_lb_polyface3d(
                                        target_lb_polyface3d_extruded_footprint=target_lb_polyface3d_extruded_footprint,
                                        context_hb_face_surface_to_test=lb_face_window_geo,
                                        # todo change the name, works with lb face as well
                                        full_urban_canopy_pyvista_mesh=full_urban_canopy_pyvista_mesh,
                                        number_of_rays=self.number_of_rays):
                                    # If the context surface is not obstructed, add it to the list of non-obstructed surfaces
                                    non_obstructed_hb_face_or_aperture_list.append(
                                        hb_aperture)  # todo : change the name, it could be apperture as well
            if len(non_obstructed_hb_face_or_aperture_list) > 0:
                context_shading_hb_shade_dict[context_building_id] = non_obstructed_hb_face_or_aperture_list

        return context_shading_hb_shade_dict

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
            if (not is_vector3d_vertical(target_lb_face3d.normal)
                    and are_hb_face_or_lb_face3d_facing(target_lb_face3d, context_hb_face_surface_to_test)):
                # Check if the context surface is obstructed for the target building
                if self.is_hb_face_context_surface_obstructed_for_target_lb_face3d(
                        target_lb_face3d=target_lb_face3d,
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
