"""
Additional functions to apply on polyface3d object
"""

import logging

from ladybug_geometry.geometry3d.polyface import Polyface3D
from ladybug_geometry.geometry3d.pointvector import Vector3D
from honeybee.room import Room
from honeybee.model import Model
from dragonfly.building import Building

dev_logger = logging.getLogger("dev")
user_logger = logging.getLogger("user")


class LbPolyface3dAddons:

    @staticmethod
    def elevation_and_height_from_polyface3d(lb_polyface3d_obj):
        """
        Extract the elevation and height of a building from a LB polyface3d object
        :param lb_polyface3d_obj: LB polyface3d object
        :return elevation: elevation of the building
        :return height: height of the building
        """
        elevation = lb_polyface3d_obj.min.z
        height = lb_polyface3d_obj.max.z - elevation
        return elevation, height

    @staticmethod
    def make_lb_face3d_footprint_from_polyface3d(lb_polyface3d_obj, elevation):
        """
        Extract the footprint of the building from the lb polyface3d object
        :param lb_polyface3d_obj: LB polyface3d object
        :param elevation: elevation of the building
        :return lb_footprint: LB face3d object
        """
        # Convert the polyface3d object to a Honeybee Room then to Model
        hb_room = Room.from_polyface3d(identifier="temp",polyface=lb_polyface3d_obj)
        hb_model = Model(identifier="temp",rooms=[hb_room])
        # turn into dragonfly building
        dragonfly_building = Building.from_honeybee(hb_model)
        # get the footprint
        lb_footprint_list = dragonfly_building.footprint()
        if len(lb_footprint_list) > 1:
            user_logger.warning("The HB model has more than one footprint, an oriented bounded box will be used to represent the footprint")
            dev_logger.warning("The HB model has more than one footprint, an oriented bounded box will be used to represent the footprint")
            # todo : @Elie : convert the function that makes the oriented bounded box from LB

        elif len(lb_footprint_list) == 0:
            user_logger.warning("The HB model has no footprint")
            dev_logger.warning("The HB model has no footprint")
            # todo : @Elie : convert the function that makes the oriented bounded box from LB
        else:
            # Move the footprint to elevation 0
            lb_footprint = lb_footprint_list[0].move(Vector3D(0., 0., - elevation))
            return lb_footprint

