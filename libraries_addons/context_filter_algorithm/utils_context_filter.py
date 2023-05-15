"""
todo
"""
from honeybee.face import Face
from ladybug_geometry.geometry3d import Face3D


def is_vector3D_vertical(Vector3D):
    if Vector3D.x == 0 and Vector3D.y == 0:
        return True
    else:
        return False


def convert_Point3D_to_list(Point3D):
    # todo @Elie move this function to utils_libraries_addons in a adequate file
    return [Point3D.x, Point3D.y, Point3D.z]
