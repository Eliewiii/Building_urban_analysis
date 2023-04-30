"""
Additional functions to apply on honeybee model
"""

from libraries_addons.utils_libraries_addons import *

def elevation_and_height_from_HB_model(HB_model):
    """
    Extract the elevation of the building from the hb model
    :param HB_model: honeybee Model
    :return: elevation, height
    """
    elevation = min([room.min.z for room in HB_model.rooms])
    height = max([room.max.z for room in HB_model.rooms]) - elevation
    return elevation, height

def make_LB_face_footprint_from_HB_model(HB_model):
    """
    Extract the footprint of the building from the hb model
    :param HB_model:
    :return:
    """
    # todo @Elie : finish the function (and check if it works)
    # turn into dragonfly building
    dragonfly_building = Building.from_honeybee(HB_model)
    # get the footprint
    LB_footprint_list = dragonfly_building.footprint()
    if len(LB_footprint_list) > 1:
        logging.warning("The HB model has more than one footprint, an oriented bounded box will be used to represent the footprint")
        # todo : @Elie : convert the function that makes the oriented bounded box from LB

    elif len(LB_footprint_list) == 0:
        logging.warning("The HB model has no footprint")
        # todo : @Elie : convert the function that makes the oriented bounded box from LB
    else:
        return LB_footprint_list[0]



def get_LB_faces_with_ground_bc_from_HB_model(HB_model):
    """
    Extract LB geometry faces 3D that have ground boundary condition from the HB model
    todo: not relevant if the building is on pillar...
    :param HB_model:
    :return:
    """
    # Init the list of LB geometry faces 3D that have ground boundary condition
    LB_face_ground_bc_list = []
    # Loop through the rooms of the HB model
    for room in HB_model.rooms:
        for face in room.faces:
            if face.boundary_condition.boundary_condition == "Ground":
                LB_face_ground_bc_list.append(face.geometry)

    return LB_face_ground_bc_list


# todo: @Elie : from mow on not


def LB_footprint_to_HB_model(LB_face_footprint, height, elevation, typology_layout=False,core_to_floor_area_ratio=0.15):
    """
    Create a honeybee model with extruded footprints of the building
    :param LB_face_footprint:
    :param height:
    :param elevation:
    :param typology_layout: if True, it will use the layout of the building typology to build the building
    :param core_to_floor_area_ratio:
    :return:
    """
    # todo: @Elie : finish the function (and check if it works)
    if typology_layout:
        None
    if not typology_layout:  # Automatic subdivision of the building on cores an apartments
        HB_model = Room.from_footprint("building", LB_face_footprint, height, elevation)
    return None

def HB_model_apply_constructionset(HB_model, constructions_set_id):
    """
    Assign construction set and program type to each room of the model
    """
    # todo: @Elie : finish the function (and check if it works)
    for room in HB_model.rooms:
        ## assign construction set
        room.properties.energy.construction_set = construction_set_by_identifier(constructions_set_id)
        ## assign program


def HB_model_apply_programs(HB_model, program_type_apartment_id, program_type_core_id):
    """
    Assign construction set and program type to each room of the model
    """
    # todo: @Elie : finish the function (and check if it works)
    for room in HB_model.rooms:
        ## assign program
        if room.properties.energy.is_conditioned:
            # if conditioned => apartment
            room.properties.energy.program_type = program_type_by_identifier(program_type_apartment_id)
        else:
            room.properties.energy.program_type = program_type_by_identifier(program_type_core_id)


def HB_model_window_by_facade_ratio_per_direction(HB_model, ratio_per_direction, min_length_wall_for_window=2.,only_conditioned=True):
    """
    Assign window to each room of the model
    """
    # todo: @Elie : finish the function (and check if it works)
    for room in HB_model.rooms:
        if room.properties.energy.is_conditioned or only_conditioned==False:
            for face in room.faces:
            # get the length of the surface => projection of the face on the XY plane
                pt_a , pt_b = room.min, room.max # extreme points of the
