"""
BuildingShadingContext class, used to perform and store the result of the context filtering for shading computation using the 2 pass filtering method
"""
import logging
from time import time

from ladybug_geometry.geometry3d.polyface import Polyface3D
from ladybug_geometry.geometry3d.face import Face3D
from honeybee.model import Model
from honeybee.face import Face
from honeybee.aperture import Aperture
from honeybee.boundarycondition import Outdoors
from honeybee.shade import Shade

from bua.building.context_filter.building_context import BuildingContextFilter

from bua.building.context_filter.utils_functions_context_filter import are_hb_face_or_lb_face3d_facing, ray_list_from_emitter_to_receiver

from bua.utils.utils_constants import AREA_TOLERANCE

user_logger = logging.getLogger("user")
dev_logger = logging.getLogger("dev")

possible_numbers_of_rays_list = [0, 1, 3, 6, 9]


class BuildingShadingContextFilter(BuildingContextFilter):
    """ todo """

    def __init__(self):
        """ todo """
        super().__init__()  # inherit from all the attributes of the super class
        # Parameters
        self.number_of_rays = None
        self.consider_windows = None

        # Results
        self.second_pass_duration = None
        self.forced_hb_shades_from_user_list = []  # todo : Check if shades need to be turned to dict before pickling
        self.context_shading_hb_shade_list = []
        # Additional shades
        self.solar_panels_hb_shade_list = []  # from the solar panels simulation
        # todo: In this specific case, the panels need to face the building to be considered (so basically
        #  flipped), and be opaque with reflectance to 0
        # Simulation tracking
        self.discarded_lb_face3d_context_shading_second_pass_list = []
        """
        We use a dictionary to store the shades of the context buildings. The keys are the building ids and the values 
        are a list of shades of the context buildings.
        """
        # Simulation tracking
        self.second_pass_done = False

    def prepare_for_pkl(self):
        """ Prepare the object for pickling """
        self.forced_hb_shades_from_user_list = [hb_shade.to_dict() for hb_shade in
                                                self.forced_hb_shades_from_user_list]
        self.context_shading_hb_shade_list = [hb_shade.to_dict() for hb_shade in
                                              self.context_shading_hb_shade_list]

    def load_from_pkl(self):
        """ Load the object from pickling """
        self.forced_hb_shades_from_user_list = [Shade.from_dict(hb_shade) for hb_shade in
                                                self.forced_hb_shades_from_user_list]
        self.context_shading_hb_shade_list = [Shade.from_dict(hb_shade) for hb_shade in
                                              self.context_shading_hb_shade_list]

    def to_dict(self):
        """
        Convert the BuildingShadingContext object to a dictionary
        """
        return {
            # First pass
            "min_vf_criterion": self.min_vf_criterion,
            "selected_context_building_id_list": self.selected_context_building_id_list,
            "first_pass_duration": self.first_pass_duration,
            "first_pass_done": self.first_pass_done,
            # Second pass
            "number_of_rays": self.number_of_rays,
            "consider_windows": self.consider_windows,
            "forced_hb_shades_from_user_list": self.forced_hb_shades_from_user_list,
            # Already converted to dict for pkl
            "context_shading_hb_shade_list": self.context_shading_hb_shade_list,
            # Already converted to dict for pkl
            "discarded_lb_face3d_context_shading_second_pass_list": [lb_face3d.to_dict() for lb_face3d in
                                                                     self.discarded_lb_face3d_context_shading_second_pass_list],
            "second_pass_duration": self.second_pass_duration,
            "second_pass_done": self.second_pass_done
        }

    def move(self, moving_vector):
        """
        Move the all the shading surfaces along the moving vector. (if the building is moved)
        :param moving_vector: list: [x, y, z] translation vector
        """
        # todo Elie

    def overwrite_filtering(self, overwrite_first_pass=False, overwrite_second_pass=False):
        """
        Overwrite the filtering of the BuildingShadingContext object
        :param overwrite_first_pass: boolean to overwrite the first pass of the context filtering. If the first pass is
        overwritten, it automatically overwrites the second pass
        :param overwrite_second_pass: boolean to overwrite the second pass of the context filtering
        """
        if overwrite_first_pass:
            self.selected_context_building_id_list = []
            self.context_shading_hb_shade_list = []
            self.first_pass_done = False
            self.second_pass_done = False
        if overwrite_second_pass:
            self.context_shading_hb_shade_list = []
            self.second_pass_done = False

    def set_number_of_rays(self, number_of_rays, no_ray_tracing=False):
        """ todo """
        if isinstance(number_of_rays, int) and number_of_rays in possible_numbers_of_rays_list:
            self.number_of_rays = number_of_rays
        elif no_ray_tracing:
            self.number_of_rays = 0
        else:
            self.number_of_rays = 3
            user_logger.warning(f"The number of ray inputted was not valid, the number of ray was set to 3")

    def set_consider_windows(self, consider_windows):
        """ todo """
        if isinstance(consider_windows, bool):
            self.consider_windows = consider_windows
        else:
            self.consider_windows = False
            user_logger.warning(
                f"The consider windows inputted was not valid, the consider windows was set to False")

    def get_hb_shades_from_hb_model(self, hb_model):
        """
        Extract the shades from the Honeybee Model and add them to context_shading_hb_shade_list attribute
        :param hb_model: Honeybee Model
        """
        self.forced_hb_shades_from_user_list.extend(hb_model.orphaned_shades)

    def select_non_obstructed_context_faces_with_ray_tracing(self, uc_shade_manager,
                                                             target_lb_polyface3d_extruded_footprint,
                                                             context_hb_model_or_lb_polyface3d_list_to_test,
                                                             full_urban_canopy_pyvista_mesh,
                                                             keep_shades_from_user=False,
                                                             no_ray_tracing=False,
                                                             keep_discarded_faces=False):
        """
        Perform the second pass of the context filtering for the shading computation. It selects the context surfaces
        for the shading computation using the ray tracing method.
        :param uc_shade_manager: ShadeManager object
        :param target_lb_polyface3d_extruded_footprint: Ladybug Polyface3D of the target building
        :param context_hb_model_or_lb_polyface3d_list_to_test: list of Honeybee Model of the context building to tests. It will
        be more efficient (for the algorithm efficiency as well as the shading computation in EnergyPlus)
        to use HB models with merged facades.
        :param full_urban_canopy_pyvista_mesh: Pyvista Mesh containing the envelopes of all the in the urban canopy
        :param keep_shades_from_user: boolean to keep the shades forced by the user
        :param no_ray_tracing: boolean to not perform the ray tracing (for validation purposes)
        :param keep_discarded_faces: boolean to keep the discarded faces
        """
        # Start the timer
        timer = time()

        if no_ray_tracing:
            selected_hb_face_lb_face3d_or_hb_aperture_list, discarded_hb_face_lb_face3d_or_hb_aperture_list = self.get_all_the_surfaces(
                context_hb_model_or_lb_polyface3d_list_to_test=context_hb_model_or_lb_polyface3d_list_to_test,
                consider_windows=self.consider_windows)
        else:
            selected_hb_face_lb_face3d_or_hb_aperture_list, discarded_hb_face_lb_face3d_or_hb_aperture_list = \
                self.select_non_obstructed_surfaces_of_context_hb_model_for_target_lb_polyface3d(
                    target_lb_polyface3d_extruded_footprint=target_lb_polyface3d_extruded_footprint,
                    context_hb_model_or_lb_polyface3d_list_to_test=context_hb_model_or_lb_polyface3d_list_to_test,
                    full_urban_canopy_pyvista_mesh=full_urban_canopy_pyvista_mesh,
                    consider_windows=self.consider_windows,
                    keep_discarded_faces=keep_discarded_faces)

        # Convert the Honeybee faces and apertures to Honeybee shades managing properly the construction
        self.context_shading_hb_shade_list = self.convert_hb_faces_and_apertures_to_shade(
            uc_shade_manager=uc_shade_manager,
            hb_face_or_aperture_context_list=selected_hb_face_lb_face3d_or_hb_aperture_list)
        # Convert the discarded faces to Ladybug Face3D
        self.discarded_lb_face3d_context_shading_second_pass_list = self.convert_discarded_faces_to_lb_face3d(
            discarded_hb_face_lb_face3d_or_hb_aperture_list=discarded_hb_face_lb_face3d_or_hb_aperture_list)

        # Stop the timer
        self.second_pass_duration = time() - timer

        # Delete the forced shades from the user if needed
        if not keep_shades_from_user:
            self.forced_hb_shades_from_user_list = []
        # Get the number of surfaces selected
        nb_context_faces = len(self.context_shading_hb_shade_list)

        self.second_pass_done = True

        return nb_context_faces, self.second_pass_duration

    def select_non_obstructed_surfaces_of_context_hb_model_for_target_lb_polyface3d(self,
                                                                                    target_lb_polyface3d_extruded_footprint,
                                                                                    context_hb_model_or_lb_polyface3d_list_to_test,
                                                                                    full_urban_canopy_pyvista_mesh,
                                                                                    consider_windows=False,
                                                                                    keep_discarded_faces=False):
        """
        Select the context surfaces that will be used for the shading simulation of the current target building.
        :param target_lb_polyface3d_extruded_footprint: Ladybug Polyface3D of the target building
        :param context_hb_model_or_lb_polyface3d_list_to_test: list of Honeybee Model of the context building to tests. It will be more
        efficient (for the algorithm efficiency as well as the shadiong computation in EnergyPlus) to use HB models
        with merged facades.
        :param full_urban_canopy_pyvista_mesh: Pyvista Mesh containing the envelopes of all the in the urban canopy
        :return hb_face_list_kept :
        """
        # Initialization
        selected_hb_face_lb_face3d_or_hb_aperture_list = []
        discarded_hb_face_lb_face3d_or_hb_aperture_list = []
        hb_face_or_lb_face3d_to_test_list = []
        # Loop through the context hb model
        for context_hb_model_or_lb_polyface_3d in context_hb_model_or_lb_polyface3d_list_to_test:
            if isinstance(context_hb_model_or_lb_polyface_3d, Model):
                for hb_room in context_hb_model_or_lb_polyface_3d.rooms:
                    for hb_face in list(hb_room.faces):
                        if isinstance(hb_face.boundary_condition, Outdoors) and hb_face.area > AREA_TOLERANCE:
                            hb_face_or_lb_face3d_to_test_list.append(hb_face)
            elif isinstance(context_hb_model_or_lb_polyface_3d, Polyface3D):
                for face in list(context_hb_model_or_lb_polyface_3d.faces):
                    if face.area > AREA_TOLERANCE:
                        hb_face_or_lb_face3d_to_test_list.append(face)
            else:
                raise ValueError(
                    "The context_hb_model_or_lb_polyface_3d is not a Honeybee Model or a Ladybug Polyface3D")

        # Loop through the rooms of the context Honeybee model
        for face in hb_face_or_lb_face3d_to_test_list:
            """ Here the horizontal context surfaces are not discarded as they can reflect the sun light, 
            even if they do not shade """
            if not self.is_hb_face_context_surface_obstructed_for_target_lb_polyface3d(
                    target_lb_polyface3d_extruded_footprint=target_lb_polyface3d_extruded_footprint,
                    context_hb_face_or_lb_face3d_to_test=face,
                    full_urban_canopy_pyvista_mesh=full_urban_canopy_pyvista_mesh,
                    number_of_rays=self.number_of_rays):
                # If the context surface is not obstructed, add it to the list of non-obstructed surfaces
                selected_hb_face_lb_face3d_or_hb_aperture_list.append(face)
            else:
                if keep_discarded_faces:
                    discarded_hb_face_lb_face3d_or_hb_aperture_list.append(face)
            # Consider the windows (only if it is a Honeybee Face)
            if isinstance(face, Face) and consider_windows:
                for hb_aperture in list(face.apertures):
                    # Make a copy of the window geometry
                    window_lb_face3d = hb_aperture.geometry
                    if not self.is_hb_face_context_surface_obstructed_for_target_lb_polyface3d(
                            target_lb_polyface3d_extruded_footprint=target_lb_polyface3d_extruded_footprint,
                            context_hb_face_or_lb_face3d_to_test=window_lb_face3d,
                            full_urban_canopy_pyvista_mesh=full_urban_canopy_pyvista_mesh,
                            number_of_rays=self.number_of_rays):
                        # If the context surface is not obstructed, add it to the list of non-obstructed surfaces
                        selected_hb_face_lb_face3d_or_hb_aperture_list.append(hb_aperture)
                    else:
                        if keep_discarded_faces:
                            discarded_hb_face_lb_face3d_or_hb_aperture_list.append(hb_aperture)

        return selected_hb_face_lb_face3d_or_hb_aperture_list, discarded_hb_face_lb_face3d_or_hb_aperture_list

    @staticmethod
    def get_all_the_surfaces(context_hb_model_or_lb_polyface3d_list_to_test, consider_windows=False):
        """
        Select all the context surfaces of the context hb model. This option is used when we do not want to perform the
        ray tracing, especially for validation purposes.
        :param context_hb_model_or_lb_polyface3d_list_to_test: list of Honeybee Model of the context building to tests. It will
        be more efficient (for the algorithm efficiency as well as the shading computation in EnergyPlus)
        to use HB models with merged facades.
        :param consider_windows: boolean to consider the windows as well
        :return hb_face_or_aperture_to_keep_list :
        """
        # Initialization
        selected_hb_face_lb_face3d_or_hb_aperture_list = []
        discarded_hb_face_lb_face3d_or_hb_aperture_list = []  # Not used here, but bette for the consistency of the code
        # Loop through the context hb model
        for context_hb_model_or_lb_polyface_3d in context_hb_model_or_lb_polyface3d_list_to_test:
            if isinstance(context_hb_model_or_lb_polyface_3d, Model):
                hb_face_or_lb_face3d_to_test_list = [hb_face for hb_face in hb_room.faces for hb_room in
                                                     context_hb_model_or_lb_polyface_3d.rooms if
                                                     isinstance(face.boundary_condition, Outdoors)]
            elif isinstance(context_hb_model_or_lb_polyface_3d, Polyface3D):
                hb_face_or_lb_face3d_to_test_list = list(context_hb_model_or_lb_polyface_3d.faces)
            else:
                raise ValueError(
                    "The context_hb_model_or_lb_polyface_3d is not a Honeybee Model or a Ladybug Polyface3D")
            # Loop through the rooms of the context Honeybee model
            for face in hb_face_or_lb_face3d_to_test_list:
                if face.area > AREA_TOLERANCE:
                    selected_hb_face_lb_face3d_or_hb_aperture_list.append(face)
                    # Consider the windows if needed
                    if isinstance(face, Face) and consider_windows:
                        for hb_aperture in face.apertures:
                            selected_hb_face_lb_face3d_or_hb_aperture_list.append(hb_aperture)

        return selected_hb_face_lb_face3d_or_hb_aperture_list, discarded_hb_face_lb_face3d_or_hb_aperture_list

    @staticmethod
    def convert_hb_faces_and_apertures_to_shade(uc_shade_manager, hb_face_or_aperture_context_list):
        """
        Convert the Honeybee faces and apertures to Honeybee shades, preserving the reflection properties
        of the surfaces, using the urban canopy ShadeManager.
        :param uc_shade_manager: ShadeManager object
        :param hb_face_or_aperture_context_list: list of Honeybee faces or Honeybee apertures
        """
        shade_index = 0
        hb_shade_list = []
        for hb_face_or_aperture in hb_face_or_aperture_context_list:
            hb_shade_list.append(
                uc_shade_manager.from_hb_face_or_aperture_to_shade(hb_or_lb_object=hb_face_or_aperture,
                                                                   shade_index=shade_index))
            shade_index += 1

        return hb_shade_list

    @staticmethod
    def convert_discarded_faces_to_lb_face3d(discarded_hb_face_lb_face3d_or_hb_aperture_list):
        """
        Convert the discarded Honeybee faces and apertures to Ladybug Face3D
        :param discarded_hb_face_lb_face3d_or_hb_aperture_list: list of Honeybee faces or Honeybee apertures
        :return discarded_lb_face3d_list: list of Ladybug Face3D
        """
        discarded_lb_face3d_list = []
        for face in discarded_hb_face_lb_face3d_or_hb_aperture_list:
            if isinstance(face, Face3D):
                discarded_lb_face3d_list.append(face)
            elif isinstance(face, Face) or isinstance(face, Aperture):
                discarded_lb_face3d_list.append(face.geometry)
            else:
                raise ValueError("The hb_face_or_aperture is not a Honeybee Face or a Honeybee Aperture")

        return discarded_lb_face3d_list

    def is_hb_face_context_surface_obstructed_for_target_lb_polyface3d(self,
                                                                       target_lb_polyface3d_extruded_footprint,
                                                                       context_hb_face_or_lb_face3d_to_test,
                                                                       full_urban_canopy_pyvista_mesh,
                                                                       number_of_rays):
        """
        Check if the context surface is obstructed for the target building
        :param target_lb_polyface3d_extruded_footprint: Ladybug Polyface3D of the target building
        :param context_hb_face_or_lb_face3d_to_test: Honeybee face of the context surface to tests
        :param full_urban_canopy_pyvista_mesh: Pyvista Mesh containing the envelopes of all the in the urban canopy
        :param number_of_rays: number of rays to be used for the ray tracing to check if the context surfaces are obstructed
        :return  :
        """
        # todo @Elie : to check
        # Loop over all the Face3D of the Ladybug Polyface3D of the target building
        for target_lb_face3d in list(target_lb_polyface3d_extruded_footprint.faces):
            # Check if the faces are facing each other
            if are_hb_face_or_lb_face3d_facing(target_lb_face3d, context_hb_face_or_lb_face3d_to_test):
                # Check if the context surface is obstructed for the target building
                if not self.is_hb_face_context_surface_obstructed_for_target_lb_face3d(
                        target_lb_face3d=target_lb_face3d,
                        context_hb_face_or_lb_face3d_to_test=context_hb_face_or_lb_face3d_to_test,
                        full_urban_canopy_pyvista_mesh=full_urban_canopy_pyvista_mesh,
                        number_of_rays=number_of_rays):
                    return False

        return True

    @staticmethod
    def is_hb_face_context_surface_obstructed_for_target_lb_face3d(target_lb_face3d,
                                                                   context_hb_face_or_lb_face3d_to_test,
                                                                   full_urban_canopy_pyvista_mesh,
                                                                   number_of_rays):
        """
        Check if the context surface is obstructed for the target building
        :param target_lb_face3d: Ladybug polyface3d of the target building
        :param context_hb_face_or_lb_face3d_to_test: Honeybee face of the context surface to tests
        :param full_urban_canopy_pyvista_mesh: Pyvista Mesh containing the envelopes of all the in the urban canopy
        :param number_of_rays: number of rays to be used for the ray tracing to check if the context surfaces are obstructed
        :return  :
        """
        # todo @Elie : to finish
        # Make the list of ray to launch
        ray_list = ray_list_from_emitter_to_receiver(face_emitter=target_lb_face3d,
                                                     face_receiver=context_hb_face_or_lb_face3d_to_test,
                                                     exclude_surface_from_ray=True,
                                                     number_of_rays=number_of_rays)
        # Loop over all the rays
        for ray in ray_list:
            # Check if the ray is obstructed
            points, ind = full_urban_canopy_pyvista_mesh.ray_trace(origin=ray[0], end_point=ray[1],
                                                                   first_point=False,
                                                                   plot=False)

            if ind.size == 0:  # no obstruction
                # TEST
                # from building.context_filter.utils_functions_context_filter import plot_ray_and_surface
                # plot_ray_and_surface(ray=ray, face_emitter=target_lb_face3d, context=full_urban_canopy_pyvista_mesh,
                #                      ind=ind)

                return False

        return True

    def add_bipv_panel_as_shades(self, panel_lb_face3d_list):
        """
        Add the BIPV panels as shades to the BuildingShadingContext object
        """
        # todo, but likely to be impossible to do properly as we cannot adjust the R value of the external
        #  wall and roofto consider the influence of the BIPV panels
