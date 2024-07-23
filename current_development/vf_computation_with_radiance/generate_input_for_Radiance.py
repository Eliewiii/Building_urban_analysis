"""

"""

from pyvista import PolyData
import numpy as np


def from_polydata_to_dot_rad_str(polydata: PolyData, identifier: str) -> str:
    """
    Convert a PolyData to a Radiance string to be saved in a .rad file.
    :param polydata: PolyData, the polydata to convert.
    :param identifier: str, the identifier of the object.
    :return: str, the Radiance string.
    """
    rad_file_content = ""
    v = polydata.points
    rad_file_content += f"void glow sur_{identifier}" + "\n"
    rad_file_content += f"0" + "\n"
    rad_file_content += f"0" + "\n"
    rad_file_content += f"4 1 1 1 0" + "\n"
    rad_file_content += f"sur_{identifier} polygon surface.{identifier}" + "\n"
    rad_file_content += f"0" + "\n"
    rad_file_content += f"0" + "\n"
    rad_file_content += f"12 {v[0][0]} {v[0][1]} {v[0][2]}" + "\n"
    rad_file_content += f" {v[1][0]} {v[1][1]} {v[1][2]}" + "\n"
    rad_file_content += f" {v[2][0]} {v[2][1]} {v[2][2]}" + "\n"
    rad_file_content += f" {v[3][0]} {v[3][1]} {v[3][2]}" + "\n"
