"""
This file contains the functions that create and modify the honeybee room objects
"""

from ladybug_geometry.geometry3d import Vector3D, Polyface3D

from honeybee.room import Room


def lb_face_footprint_to_elevated_hb_room_envelop(lb_face_footprint, building_id, height, elevation):
    """
    Create a honeybee room with extruded footprints of the building and put it at the right elevation.
    :param lb_face_footprint: ladybug geometry footprint
    :param building_id: id of the building
    :param height: height of the building in meters
    :param elevation: elevation of the building in meters
    :return: honeybee room
    """
    # extrude the footprint to obtain the room envelop
    extruded_face = Polyface3D.from_offset_face(lb_face_footprint, height)
    # set the identifier
    identifier = "building_{}".format(building_id)
    # create the honeybee room
    hb_room_envelop = Room.from_polyface3d(identifier, extruded_face)
    # move the room to the right elevation
    hb_room_move_vertically(hb_room_envelop, elevation)

    return hb_room_envelop


def hb_room_move_vertically(hb_room, elevation):
    """
    Move a honeybee room vertically to the right elevation
    :param hb_room: honeybee room
    :param elevatiopn: elevation in meters
    :return:
    """
    # create a vector to move the room
    moving_vector = Vector3D(0., 0., elevation)
    # move the room
    hb_room.move(moving_vector)
