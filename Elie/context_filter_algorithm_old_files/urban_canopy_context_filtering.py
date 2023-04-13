"""
Additional methods for the Urban_canopy class.
Deals with the context filtering
"""

import logging

from time import time
from math import sqrt, atan, pi, log


class Mixin:

    # def filter_context(self, vf_criteria):
    #     """
    #     1- identify the buildings that are close to the target buildings and that should be simulated as well
    #     2- identify the buildings that are close to the simulated context buildings and that should be part
    #        of their context
    #     3- Select the context surfaces
    #     """
    #
    #     target_buildings_face_list = []
    #     all_building_face_list = []
    #     context_simulated_building_face_list = []
    #
    #     ## prepare target building_zon surfaces
    #     for id in self.target_buildings:
    #         target_buildings_face_list.append([id, self.building_dict[id].prepare_face_for_context(reverse=False)])
    #     ## prepare all building_zon surfaces
    #     for not_used, (id, building_obj) in enumerate(self.building_dict.items()):
    #         all_building_face_list.append([id, building_obj.prepare_face_for_context(reverse=True)])
    #
    #     for target_building_face_list in target_buildings_face_list:
    #         context_building_face_list_kept = []  # list with the id of the context buildings for this building_zon
    #         ## first check, just identify the buildings if one surface fits the requirement
    #         for test_context_building_face_list in all_building_face_list:
    #             # check if the buildings are not the same
    #             if target_building_face_list[0] != test_context_building_face_list[0]:
    #                 if is_context_building(target_building_face_list[1], test_context_building_face_list[1],
    #                                        vf_criteria):
    #                     context_building_face_list_kept.append(test_context_building_face_list)
    #                     self.building_dict[target_building_face_list[0]].context_buildings_id.append(
    #                         test_context_building_face_list[0])
    #                     # self.building_dict[test_context_building_face_list[0]].is_simulated=True
    #                 else:
    #                     None
    #             else:
    #                 None
    #         for test_context_building_face_list in context_building_face_list_kept:
    #             self.filter_context_surfaces(target_building_face_list[1], test_context_building_face_list[1],
    #                                          target_id=target_building_face_list[0],
    #                                          vf_criteria=vf_criteria)
    #
    #         ## second check, check every surfaces in the selected context buildings
    #
    #     ## prepare the simulated buildings that are not targets
    #
    # def filter_context_surfaces(self, target_building_face_list, test_context_building_face_list, target_id,
    #                             vf_criteria):
    #     """ Check if the test_context_building is part of the context """
    #     ## first pass
    #     for test_face in test_context_building_face_list:
    #         for target_face in target_building_face_list:
    #             if max_VF(target_face, test_face) >= vf_criteria:
    #                 self.building_dict[target_id].context_buildings_HB_faces.append(test_face[0])
    #                 break
    #     ## second pass
    #
    #     # to be continued...

    def identify_building_to_simulate(self, vf_criteria):
        """
        identify, according to the LWR, with the filtering criteria if we should keep the surfaces
        """

    def prepare_building_face_for_context_new(self):
        """
        Generate the face_list attributes for the buildings to simplify the computation
        """
        for not_used, (id, building_obj) in enumerate(self.building_dict.items()):
            building_obj.prepare_face_for_context_new(is_target=building_obj.is_target)

    def prepare_bounding_box_faces_for_context(self):
        """
        Generate the face_list for the bounding box of the buildings to simplify the computation
        """
        for not_used, (id, building_obj) in enumerate(self.building_dict.items()):
            building_obj.prepare_bounding_box_face_list()

    def generate_pre_processed_bb_building_surface_dict(self):
        """
            Generate the dictionary containing the face dictionary of the bounding box
            and the envelop faces of the buildings
        """
        pre_processed_bb_building_surface_dict = {}
        for not_used, (id, building_obj) in enumerate(self.building_dict.items()):
            pre_processed_bb_building_surface_dict[id] = {
                "bounding_box_faces": building_obj.bounding_box_face_list,
                "envelope_faces": building_obj.external_face_list_context
            }
        return pre_processed_bb_building_surface_dict

    def filter_context_bounding_box(self, mvfc=0.01, first_pass=True,
                                    second_pass=True):
        """

        """

        # for id in self.target_buildings:
        #     target_buildings_face_list.append([id, self.building_dict[id].prepare_face_for_context(reverse=False)])
        # ## prepare all building_zon surfaces
        # for not_used, (id, building_obj) in enumerate(self.building_dict.items()):
        #     all_building_face_list.append([id, building_obj.prepare_face_for_context(reverse=True)])

        ## Prepare surfaces
        timer = time()
        self.prepare_building_face_for_context_new()
        timer = time() - timer
        logging.warning(
            f" Preprocessing of surfaces for context filtering second pass duration :{round(timer, 4)}s")
        ## Prepare Bounding Box
        timer = time()
        self.prepare_bounding_box_faces_for_context()
        timer = time() - timer
        pre_processed_bb_building_dict = self.generate_pre_processed_bb_building_surface_dict()
        logging.warning(
            f" Preprocessing of bounding boxes for context filtering second pass duration :{round(timer, 4)}s")

        ## Loop over all the target buildings
        for id_target in self.building_to_simulate:
            target_building_obj = self.building_dict[id_target]
            ## select the relevant context surfaces with the first and second pass criteria
            kept_surface_first_pass, kept_surface_second_pass, first_pass_duration, second_pass_duration = target_building_obj.shading_context_bb_surfaces_selection(
                pre_processed_bb_building_surface_dict=pre_processed_bb_building_dict, mvfc=mvfc, first_pass=first_pass,
                second_pass=second_pass)

    def filter_context_new(self, mvfc=0.01, first_pass=True,
                           second_pass=True):
        """
        1- identify the buildings that are close to the target buildings and that should be simulated as well
        2- identify the buildings that are close to the simulated context buildings and that should be part
           of their context
        3- Select the context surfaces
        """

        # for id in self.target_buildings:
        #     target_buildings_face_list.append([id, self.building_dict[id].prepare_face_for_context(reverse=False)])
        # ## prepare all building_zon surfaces
        # for not_used, (id, building_obj) in enumerate(self.building_dict.items()):
        #     all_building_face_list.append([id, building_obj.prepare_face_for_context(reverse=True)])

        # ## prepare target building_zon surfaces
        self.prepare_building_face_for_context_new()
        ## Loop over all the target buildings
        for id_target in self.building_to_simulate:
            target_building_obj = self.building_dict[id_target]
            pre_processed_surface_list = []
            ## loop over all the buildings, that can potentially be context
            for id_context in self.building_dict:
                ## check that it's not executing the code on itself
                if id_target == id_context:
                    continue  # if it's the same it skips
                context_building_obj = self.building_dict[id_context]
                for surface_dict in context_building_obj.external_face_list_context:
                    pre_processed_surface_list.append(surface_dict)
                ## select the relevant context surfaces with the first and second pass criteria
            kept_surface_first_pass, kept_surface_second_pass, first_pass_duration, second_pass_duration = target_building_obj.shading_context_surfaces_selection(
                pre_processed_surface_list=pre_processed_surface_list, mvfc=mvfc, first_pass=first_pass,
                second_pass=second_pass)

    def correct_context_elevation(self):
        """
        correct the elevation of the context compared to the the target buildings (as the buildings should be simulated
        with a 0 meter elevation)
        #todo
        """
        for building_id in self.building_to_simulate:
            self.building_dict[building_id].correct_context_elevation()


def is_context_building(target_building_face_list, test_context_building_face_list, VF_criteria):
    """
    Check if the at least one of the surface of the context building has a view factor superior to the Min_VF criterion.
    Can be used to select which buildings to simulate for LWR.
    Can be used to say which building should be considered in the context (mutual shading)
    """
    for target_face in target_building_face_list:
        for test_face in test_context_building_face_list:
            if max_VF(target_face, test_face) >= VF_criteria:
                return (True)
    return (False)


def LB_distance_pt_3D(pt_1, pt_2):
    """ Distance between 2 LB geometry Point3D """
    return sqrt((pt_1.x - pt_2.x) ** 2 + (pt_1.y - pt_2.y) ** 2 + (pt_1.z - pt_2.z) ** 2)


def max_VF(target_face, test_face):
    """
    Maximal view factor between the 2 surface, in the optimal configuration described in the context paper
    the faces are lists with following format :  [LB_face_obj,area, centroid]
    """
    ## distance between the centroids
    d = LB_distance_pt_3D(target_face[2], test_face[2])
    if d == 0:
        d = 0.01
    ## width of the optimal squares
    W_1 = sqrt(target_face[1])
    W_2 = sqrt(test_face[1])
    ## intermediary variable for the computation
    w_1 = W_1 / d
    w_2 = W_2 / d
    x = w_2 - w_1
    y = w_2 + w_1
    p = (w_1 ** 2 + w_2 ** 2 + 2) ** 2
    q = (x ** 2 + 2) * (y ** 2 + 2)
    u = sqrt(x ** 2 + 4)
    v = sqrt(y ** 2 + 4)
    s = u * (x * atan(x / u) - y * atan(y / u))
    t = v * (x * atan(x / v) - y * atan(y / v))
    return 1 / (pi * w_1 ** 2) * (log(p / q) + s - t)
