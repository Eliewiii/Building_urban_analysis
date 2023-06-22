"""
todo
"""

from building.context_filter.utils_libraries_context_filter import *
from building.context_filter.utils_functions_context_filter import *


class BuildingContext:
    """ todo """

    def __init__(self):
        self.min_VF_criterion = None
        self.context_building_id_list = []

    def select_context_buildings_using_the_mvfc(self, target_LB_polyface3d_extruded_footprint,
                                                context_LB_polyface3d_oriented_bounding_box, context_building_id):
        """ todo"""
        # Check if the bounding box of the tested context building verifies the mvf criterion
        if self.is_bounding_box_context_using_mvfc_criterion(target_LB_polyface3d_extruded_footprint,
                                                             context_LB_polyface3d_oriented_bounding_box,
                                                             minimum_vf_criterion=self.min_VF_criterion):
            # if it verifies the criterion we add it to the context building
            self.context_building_id_list.append(context_building_id)

    @staticmethod
    def is_bounding_box_context_using_mvfc_criterion(target_LB_polyface3d_extruded_footprint,
                                                     context_LB_polyface3d_oriented_bounding_box, minimum_vf_criterion):
        """
        Check if the bounding box of a context building is a context for the current building.
        It corresponds to the first pass of the context filter algorithm
        :param target_LB_polyface3d_extruded_footprint: LB polyface3d of the current building
        :param context_LB_polyface3d_oriented_bounding_box: LB polyface3d of the bounding box of the context building
        :param minimum_vf_criterion: minimum view factor between surfaces to be considered as context surfaces
        in the first pass of the algorithm
        :return: boolean
        """
        # todo @Elie check the description of the function and test it
        # Loop over all the couples of surfaces between the target building and the context building
        for context_LB_Face3D in list(context_LB_polyface3d_oriented_bounding_box.faces):  # polyface3D.faces is a tuple
            if not is_vector3D_vertical(context_LB_Face3D.normal):  # exclude the horizontal/roof/ground surfaces
                for target_LB_Face3D in list(target_LB_polyface3d_extruded_footprint.faces):
                    # Get the view factor between the context building and the current building
                    majorized_view_factor = majorized_VF_between_2_surfaces(
                        Point3D_centroid_1=target_LB_Face3D.centroid,
                        area_1=target_LB_Face3D.area,
                        Point3D_centroid_2=context_LB_Face3D.centroid,
                        area_2=context_LB_Face3D.arrea)
                    # If the view factor is above the minimum criterion, add the building to the list of buildings
                    # that will be used for the second pass
                    if majorized_view_factor > minimum_vf_criterion:
                        return True
        # if none of the surfaces match the criterion, return False
        return False
