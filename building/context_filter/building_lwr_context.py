"""
We'll see, we need same first pass context filtering, with a different mvfc value, but the second filtering
will be much different
todo @Elie
"""
from building.context_filter.building_context import BuildingContextFilter


class BuildingLWRContextFilter(BuildingContextFilter):
    """ todo """

    def __init__(self):
        """ todo """
        super().__init__()  # inherit from all the attributes of the super class









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
        :return hb_face_list_kept :
        """
        # Initialization
        context_shading_hb_shade_list = {}
        # Loop through the context hb model
        for context_hb_model, context_building_id in zip(context_building_hb_model_list, context_building_id_list):
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
                                                                             0.1)  # todo : check if it is the right direction
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
                context_shading_hb_shade_list[context_building_id] = non_obstructed_hb_face_or_aperture_list

        return context_shading_hb_shade_list