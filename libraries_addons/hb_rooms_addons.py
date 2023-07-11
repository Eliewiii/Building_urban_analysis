"""
This file contains the functions that create and modify the honeybee room objects
"""

from ladybug_geometry.geometry3d.polyface import Polyface3D
from ladybug_geometry.geometry3d.pointvector import Vector3D

from honeybee.room import Room


class RoomsAddons:
    @classmethod
    def LB_face_footprint_to_elevated_HB_room_envelop(cls, LB_face_footprint, building_id, height, elevation):
        """
        Create a honeybee room with extruded footprints of the building and put it at the right elevation.
        :param LB_face_footprint: ladybug geometry footprint
        :param building_id: id of the building
        :param height: height of the building in meters
        :param elevation: elevation of the building in meters
        :return: honeybee room
        """
        # extrude the footprint to obtain the room envelop
        extruded_face = Polyface3D.from_offset_face(LB_face_footprint, height)
        # set the identifier
        identifier = "building_{}".format(building_id)
        # create the honeybee room
        HB_room_envelop = Room.from_polyface3d(identifier, extruded_face)
        # move the room to the right elevation
        cls.HB_room_move_vertically(HB_room_envelop, elevation)

        return HB_room_envelop

    @staticmethod
    def HB_room_move_vertically(HB_room, elevation):
        """
        Move a honeybee room vertically to the right elevation
        :param HB_room: honeybee room
        :param elevatiopn: elevation in meters
        :return:
        """
        # create a vector to move the room
        moving_vector = Vector3D(0., 0., elevation)
        # move the room
        HB_room.move(moving_vector)
