"""
Utils functions for the generation of SensorGrids objects
"""

import logging

from honeybee.model import Model

user_logger = logging.getLogger("user")
dev_logger = logging.getLogger("dev")




def generate_sensor_grid_for_hb_model(hb_model_obj, grid_size_x, grid_size_y, offset_dist, surface_type):
    """
    :param hb_model_obj: Honeybee Model object
    :param grid_size_x: float : size of the grid in the x direction in meter
    :param grid_size_y: float : size of the grid in the y direction in meter
    :param offset_dist: float : offset distance on the border of the face to generate the mesh
    :param surface_type: str : Surface type to generate the Sensorgrid on, either "Roof" or "Facade"

    :return sensorgrid_dict:
    """
    # not sure if necessary

    assert isinstance(hb_model_obj, Model), 'Expected Honeybee Model. Got {}.'.format(type(hb_model_obj))

    if surface_type not in ["Roof", "Facade"]:
        dev_logger.critical(f"the surface_type is either not specified or incorrect, please check")
        # TODO @Ale, what to do to stop the program here
    elif surface_type == "Roof":
        hb_face_list = get_hb_faces_roof(hb_model_obj)
    else:
        hb_face_list = get_hb_faces_facades(hb_model_obj)

    sensor_grid_obj = generate_sensorgrid_obj_on_hb_face_list(hb_face_list, grid_size_x, grid_size_y, offset_dist)

    return sensor_grid_obj.to_dict()


def generate_sensorgrid_obj_on_hb_face_list(hb_face_list, grid_size_x, grid_size_y, offset_dist):
    """

    """
    # generate Ladybug Mesh on the Honeybee Face
    lb_mesh_obj = get_lb_mesh_BUA_grid_y(hb_face_list, grid_size_x, grid_size_y, offset_dist)
    # Generate a SensorGrid object out of the mesh
    sensor_grid_obj = create_sensor_grid_from_mesh(lb_mesh_obj)

    return sensor_grid_obj
