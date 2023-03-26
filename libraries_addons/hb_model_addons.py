"""
Additional functions to apply on honeybee model
"""


from honeybee.room import Room
from honeybee_energy.lib.constructionsets import construction_set_by_identifier
from honeybee_energy.lib.programtypes import program_type_by_identifier


def elevation_and_height_from_HB_model(HB_model):
    """
    Extract the elevation of the building from the hb model
    :param HB_model: honeybee Model
    :return: elevation, height
    """
    elevation = min([room.min.z for room in HB_model.rooms])
    height = max([room.max.z for room in HB_model.rooms]) - elevation

    return elevation, height



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

    if typology_layout:
        None
    if not typology_layout:  # Automatic subdivision of the building on cores an apartments
        HB_model = Room.from_footprint("building", LB_face_footprint, height, elevation)



    return None










def HB_model_apply_constructionset(HB_model, constructions_set_id):
    """
    Assign construction set and program type to each room of the model
    """
    for room in HB_model.rooms:
        ## assign construction set
        room.properties.energy.construction_set = construction_set_by_identifier(constructions_set_id)
        ## assign program


def HB_model_apply_programs(HB_model, program_type_apartment_id, program_type_core_id):
    """
    Assign construction set and program type to each room of the model
    """
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
    for room in HB_model.rooms:
        if room.properties.energy.is_conditioned or only_conditioned==False:
            for face in room.faces:
            # get the length of the surface => projection of the face on the XY plane
                pt_a , pt_b = room.min, room.max # extreme points of the
