"""
Utils functions for the generation of SensorGrids objects
"""

import logging

from ladybug_geometry.geometry3d.mesh import Mesh3D
from ladybug_geometry.geometry2d.mesh import Mesh2D
from ladybug_geometry.geometry2d.polygon import Polygon2D
from ladybug_geometry.geometry2d.pointvector import Vector2D
from ladybug_geometry.geometry2d.ray import Ray2D
from ladybug_geometry.intersection2d import does_intersection_exist_line2d
from honeybee.model import Model
from honeybee.boundarycondition import Outdoors
from honeybee.facetype import Wall, RoofCeiling
from honeybee.typing import clean_and_id_rad_string, clean_rad_string
from honeybee_radiance.sensorgrid import SensorGrid

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
        hb_face_list = get_hb_faces_list_according_to_type(hb_model_obj, is_roof)
    else:
        hb_face_list = get_hb_faces_list_according_to_type(hb_model_obj, is_facade)

    sensor_grid_obj = generate_sensorgrid_obj_on_hb_face_list(hb_face_list, grid_size_x, grid_size_y,
                                                              offset_dist)

    return sensor_grid_obj.to_dict()


def generate_sensorgrid_obj_on_hb_face_list(hb_face_list, grid_size_x, grid_size_y, offset_dist):
    """

    """
    # generate Ladybug Mesh on the Honeybee Face
    lb_mesh_obj = get_lb_mesh_BUA_grid_y(hb_face_list, grid_size_x, grid_size_y, offset_dist)
    # Generate a SensorGrid object out of the mesh
    sensor_grid_obj = create_sensor_grid_from_mesh(lb_mesh_obj)

    return sensor_grid_obj


def get_hb_faces_list_according_to_type(model, face_type_function):
    """Get the HB faces of the roof and the facades of our HB model"""
    faces = []
    for face in model.faces:
        if face_type_function(face):
            faces.append(face.punched_geometry)
    return faces


def create_sensor_grid_from_mesh(mesh, name=None):
    """Create a HB SensorGrid and add it to a HB model"""
    name = clean_and_id_rad_string('SensorGrid') if name is None else name
    id = clean_rad_string(name) if '/' not in name else clean_rad_string(name.split('/')[0])
    sensor_grid = SensorGrid.from_mesh3d(id, mesh)
    return sensor_grid


def is_facade(face):
    """Check if the face is an exterior wall"""
    return (isinstance(face.type, Wall) and isinstance(face.boundary_condition, Outdoors))


def is_roof(face):
    """Check if the face is a roof"""
    return (isinstance(face.type, RoofCeiling) and isinstance(face.boundary_condition, Outdoors))
