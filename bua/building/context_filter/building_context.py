"""
todo
"""

import logging
from time import time

from ladybug_geometry.geometry3d.polyface import Polyface3D
from honeybee.boundarycondition import Outdoors

from bua.building.context_filter.utils_functions_mvfc import majorized_vf_between_2_surfaces
from bua.building.context_filter.utils_functions_context_filter import is_vector3d_vertical

from bua.utils.utils_constants import TOLERANCE_LBT

user_logger = logging.getLogger("user")
dev_logger = logging.getLogger("dev")

# Minimum and maximum value for the minimum view factor criterion
min_mvfc = 0.0000001
max_mvfc = 1.


class BuildingContextFilter:
    """ Class to perform the context filtering on buildings """

    def __init__(self):
        # Parameter
        self.min_vf_criterion = None
        # Result
        self.selected_context_building_id_list = []
        self.first_pass_duration = None
        # Simulation tracking
        self.first_pass_done = False

    def set_mvfc(self, min_vf_criterion):
        """ todo """
        if isinstance(min_vf_criterion, float) and min_mvfc < min_vf_criterion < max_mvfc:
            self.min_vf_criterion = min_vf_criterion
        else:
            self.min_vf_criterion = 0.01
            user_logger.warning(f"The minimum view factor criterion inputted was not valid, the minimum view"
                                f" factor criterion was set to 0.01")

    def select_context_building_using_the_mvfc(self, target_lb_polyface3d_of_outdoor_faces, target_building_id,
                                               uc_building_id_list, uc_building_bounding_box_list, include_target_building:bool=False):
        """
        Select the context buildings of a target building using the minimum view factor criterion.
        It corresponds to the first pass of the context filter algorithm
        :param target_lb_polyface3d_of_outdoor_faces: Ladybug polyface3d of the outdoor faces of the target building
        :param target_building_id: str, id of the target building
        :param uc_building_id_list: list of str, list of the id of the buildings in the urban canopy
        :param uc_building_bounding_box_list: list of Ladybug polyface3d of the oriented bounding box of the buildings
        in the urban canopy
        """

        # Timer to tack the duration of the simulation
        timer = time()
        # Loop over all the context buildings
        for context_building_id, context_lb_polyface3d_oriented_bounding_box in zip(uc_building_id_list,
                                                                                    uc_building_bounding_box_list):
            # Check if the bounding box of the tested context building verifies the mvf criterion and is not already
            if (context_building_id != target_building_id
                    and context_building_id not in self.selected_context_building_id_list
                    and self.is_bounding_box_context_using_mvfc_criterion(target_lb_polyface3d_of_outdoor_faces,
                                                                          context_lb_polyface3d_oriented_bounding_box,
                                                                          min_vf_criterion=self.min_vf_criterion)):
                # if it verifies the criterion we add it to the context building
                self.selected_context_building_id_list.append(context_building_id)
        # If the target building is included in the context buildings, we add it to the list
        if include_target_building:
            self.selected_context_building_id_list.append(target_building_id)
        # Set the first pass as done
        self.first_pass_done = True
        self.first_pass_duration = time() - timer

        return self.selected_context_building_id_list, self.first_pass_duration

    @staticmethod
    def is_bounding_box_context_using_mvfc_criterion(target_lb_polyface3d,
                                                     context_lb_polyface3d_oriented_bounding_box,
                                                     min_vf_criterion):
        """
        Check if the bounding box of a context building is a context for the current building.
        It corresponds to the first pass of the context filter algorithm
        :param target_lb_polyface3d: Ladybug polyface3d of the current building
        :param context_lb_polyface3d_oriented_bounding_box: Ladybug polyface3d of the bounding box of the context building
        :param min_vf_criterion: minimum view factor between surfaces to be considered as context surfaces
        in the first pass of the algorithm
        :return: boolean
        """
        # todo @Elie check the description of the function and tests it
        # Loop over all the couples of surfaces between the target building and the context building
        for context_lb_face3d in list(context_lb_polyface3d_oriented_bounding_box.faces):  # polyface3d.faces is a tuple
            if not is_vector3d_vertical(context_lb_face3d.normal):  # exclude the horizontal/roof/ground surfaces
                for target_lb_face3d in list(target_lb_polyface3d.faces):
                    # Get the view factor between the context building and the current building
                    majorized_view_factor = majorized_vf_between_2_surfaces(
                        point3d_centroid_1=target_lb_face3d.centroid,
                        area_1=target_lb_face3d.area,
                        point3d_centroid_2=context_lb_face3d.centroid,
                        area_2=context_lb_face3d.area)
                    # If the view factor is above the minimum criterion, add the building to the list of buildings
                    # that will be used for the second pass
                    if majorized_view_factor > min_vf_criterion:
                        return True
        # if none of the surfaces match the criterion, return False
        return False

    @staticmethod
    def get_lb_polyface3d_of_outdoor_faces_from_hb_model(hb_model):
        """
        Get the Ladybug polyface3d of the outdoor faces of a Honeybee model
        :param hb_model: Honeybee model
        :return: Ladybug polyface3d of the outdoor faces of the Honeybee model
        """
        # todo @Elie: check the function
        # Initialize the list of outdoor faces
        lb_face3d_list = []
        # Loop over all the rooms of the HB model
        for room in hb_model.rooms:
            # Loop over all the faces of the room
            for face in room.faces:
                # Check if the face is an outdoor face
                if isinstance(face.boundary_condition, Outdoors):
                    # Add the face to the list of outdoor faces
                    lb_face3d_list.append(face.geometry)
        # Convert the list of surfaces to Polyface3D
        return Polyface3D.from_faces(faces=lb_face3d_list,tolerance=TOLERANCE_LBT)
