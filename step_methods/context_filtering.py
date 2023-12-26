"""
Functions for the context filtering step.
For both shading and LWR.
"""

from time import time

from utils.utils_default_values_user_parameters import default_mvfc_context_shading_selection, \
    default_shading_number_of_rays_context_filter_second_pass, \
    default_automatic_floor_subdivision_for_new_BuildingModeled, \
    default_use_layout_from_typology_for_new_BuildingModeled, \
    default_use_properties_from_typology_for_new_BuildingModeled, default_make_new_BuildingModeled_simulated


class SimulationContextFiltering:
    """ todo   """

    @classmethod
    def perform_context_filtering_on_building(cls,
                                              urban_canopy_object,
                                              min_VF_criterion=default_mvfc_context_shading_selection,
                                              number_of_rays=default_shading_number_of_rays_context_filter_second_pass,
                                              building_id_list=None, on_building_to_simulate=True,
                                              automatic_floor_subdivision_for_new_BuildingModeled=default_automatic_floor_subdivision_for_new_BuildingModeled,
                                              use_layout_from_typology_for_new_BuildingModeled=default_use_layout_from_typology_for_new_BuildingModeled,
                                              use_properties_from_typology_for_new_BuildingModeled=default_use_properties_from_typology_for_new_BuildingModeled,
                                              make_new_BuildingModeled_simulated=default_make_new_BuildingModeled_simulated):
        """
        Perform the 2 context filtering pass on buildings
        :param urban_canopy_object:
        :param min_VF_criterion:
        :param number_of_rays:
        :param building_id_list:
        :param on_building_to_simulate:
        :param automatic_floor_subdivision_for_new_BuildingModeled:
        :param use_layout_from_typology_for_new_BuildingModeled:
        :param use_properties_from_typology_for_new_BuildingModeled:
        :param make_new_BuildingModeled_simulated:
        :return:
        """

        # Initialize the BuildingShadingContext obj if needed
        # urban_canopy_object.initialize_shading_context_obj_of_buildings_to_simulate(min_VF_criterion,
        #                                                                             number_of_rays)
        # # Perform the first pass of context filtering
        # building_id_list_to_convert_to_BuildingModeled = cls.perform_first_pass_of_context_filtering_on_buildings(
        #     urban_canopy_object, min_VF_criterion=min_VF_criterion,
        #     number_of_rays=number_of_rays, building_id_list=building_id_list,
        #     on_building_to_simulate=on_building_to_simulate)
        #
        # # todo : new version
        #
        # # # Convert the context buildings in BuildingModeled objects
        # # urban_canopy_object.convert_list_of_buildings_to_BuildingModeled(
        # #     building_id_list_to_convert_to_BuildingModeled,
        # #     automatic_floor_subdivision=automatic_floor_subdivision_for_new_BuildingModeled,
        # #     layout_from_typology=use_layout_from_typology_for_new_BuildingModeled,
        # #     properties_from_typology=use_properties_from_typology_for_new_BuildingModeled,
        # #     are_simulated=make_new_BuildingModeled_simulated)

        # Perform the second pass of context filtering
        cls.perform_second_pass_of_context_filtering_on_buildings(urban_canopy_object)

    @staticmethod
    def perform_first_pass_of_context_filtering_on_buildings(urban_canopy_object,
                                                             building_id_list=None,
                                                             on_building_to_simulate=False,
                                                             min_vf_criterion=default_mvfc_context_shading_selection,
                                                             overwrite=False):
        """
        Perform first pass of context filtering on buildings
        :param urban_canopy_object: UrbanCanopy object, the urban canopy
        :param building_id_list: list of str, the list of building id to perform the first pass context filtering on.
        :param on_building_to_simulate: bool, if True, perform the first pass context filtering on the buildings to simulate.
        :param min_vf_criterion: float, the minimum view factor criterion.
        :param overwrite: bool, if True, the existing context selection will be overwritten.
        :return:
        """

        timer = time()

        # Perform first pass of context filtering on buildings
        context_building_id_list, sim_duration_dict = urban_canopy_object.perform_first_pass_context_filtering_on_buildings(
            building_id_list=building_id_list,
            on_building_to_simulate=on_building_to_simulate,
            min_vf_criterion=min_vf_criterion,
            overwrite=overwrite)

        tot_duration = time() - timer

        return context_building_id_list, tot_duration, sim_duration_dict

    @staticmethod
    def perform_second_pass_of_context_filtering_on_buildings(urban_canopy_object,
                                                              building_id_list=None,
                                                              number_of_rays=default_shading_number_of_rays_context_filter_second_pass,
                                                              on_building_to_simulate=False,
                                                              consider_windows=False,
                                                              keep_shades_from_user=False,
                                                              no_ray_tracing=False,
                                                              overwrite=False):
        """
        Perform second pass of context filtering on buildings.
        :param urban_canopy_object: UrbanCanopy object, the urban canopy
        :param building_id_list: list of str, the list of building id to perform the second pass context filtering on.
        :param on_building_to_simulate: bool, if True, perform the second pass context filtering on the buildings
            to simulate.
        :param consider_windows: bool, if True, the windows will be considered in the context filtering.
        :param keep_shades_from_user: bool, if True, the shades from the user will be kept in the context filtering.
        :param no_ray_tracing: bool, if True, the second pass context filtering will be performed without ray-tracing.
        :param overwrite: bool, if True, the existing context selection will be overwritten.
        """

        timer = time()

        # Perform second pass of context filtering on buildings
        result_summary_dict = urban_canopy_object.perform_second_pass_context_filtering_on_buildings(
            building_id_list=building_id_list,
            number_of_rays=number_of_rays,
            on_building_to_simulate=on_building_to_simulate,
            consider_windows=consider_windows,
            keep_shades_from_user=keep_shades_from_user,
            no_ray_tracing=no_ray_tracing,
            overwrite=overwrite)

        tot_duration = time() - timer

        return tot_duration, result_summary_dict
