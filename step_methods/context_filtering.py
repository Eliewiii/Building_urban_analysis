"""
Functions for the context filtering step.
For both shading and LWR.
"""

from mains_tool.utils_general import *
from step_methods.utils_step_methods import *

from mains_tool.utils_default_values_user_parameters import *


class SimulationContextFiltering:
    """ todo   """

    @staticmethod
    def perform_first_pass_of_context_filtering_on_buildings(urban_canopy_object,
                                                             min_VF_criterion=default_mvfc_context_shading_selection,
                                                             number_of_rays=default_number_of_rays,
                                                             building_id_list=None, on_building_to_simulate=True,
                                                             automatic_floor_subdivision_for_new_BuildingModeled=default_automatic_floor_subdivision_for_new_BuildingModeled,
                                                             use_layout_from_typology_for_new_BuildingModeled=default_use_layout_from_typology_for_new_BuildingModeled,
                                                             use_properties_from_typology_for_new_BuildingModeled=default_use_properties_from_typology_for_new_BuildingModeled,
                                                             make_new_BuildingModeled_simulated=default_make_new_BuildingModeled_simulated):
        """
        Perform first pass of context filtering on buildings
        :param urban_canopy_object:
        :param min_VF_criterion:
        :param number_of_rays:
        :param building_id_list:
        :param on_building_to_simulate:
        :return:
        """

        # Initialize the BuildingShadingContext obj if needed
        urban_canopy_object.initialize_shading_context_obj_of_buildings_to_simulate(min_VF_criterion, number_of_rays)
        # Perform first pass of context filtering on buildings
        building_id_list_to_convert_to_BuildingModeled = urban_canopy_object.perform_first_pass_context_filtering_on_buildings(
            building_id_list=building_id_list,
            on_building_to_simulate=on_building_to_simulate)
        # Convert the context buildings in BuildingModeled objects
        urban_canopy_object.convert_list_of_buildings_to_BuildingModeled(building_id_list_to_convert_to_BuildingModeled,
                                                                         automatic_floor_subdivision=automatic_floor_subdivision_for_new_BuildingModeled,
                                                                         layout_from_typology=use_layout_from_typology_for_new_BuildingModeled,
                                                                         properties_from_typology=use_properties_from_typology_for_new_BuildingModeled,
                                                                         are_simulated=make_new_BuildingModeled_simulated)
