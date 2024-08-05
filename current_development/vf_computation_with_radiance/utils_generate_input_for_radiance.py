"""

"""
import os
import subprocess

from pyvista import PolyData
import numpy as np

from .utils_folder_manipulation import check_parent_folder_exist


def spl

def from_polydata_to_rad_file(polydata: PolyData, path_rad_file: str, identifier: str):
    """
    Convert a PolyData to a Radiance file.
    :param polydata: PolyData, the polydata to convert.
    :param path_rad_file: str, the path of the Radiance file.
    :param identifier: str, the identifier of the object.
    """
    # Check if the folder of the output file exists
    check_parent_folder_exist(path_rad_file)
    # Convert the PolyData to a Radiance file
    rad_file_content = r"#@rfluxmtx h=u" + "\n"
    rad_file_content += from_polydata_to_dot_rad_str(polydata, identifier)
    with open(path_rad_file, "w") as f:
        f.write(rad_file_content)


def from_polydata_list_to_rad_file(polydata_list: [PolyData], identifier_list: [str], path_rad_file: str):
    """
    Convert a list of PolyData to a Radiance file.
    :param polydata_list: [PolyData], the list of polydata to convert.
    :param identifier_list: [str], the list of identifiers of the objects.
    :param path_rad_file: str, the path of the Radiance file.
    """
    # Check if the folder of the output file exists
    check_parent_folder_exist(path_rad_file)
    # Convert the PolyData to a Radiance file
    rad_file_content = r"#@rfluxmtx h=u" + "\n"
    for polydata, identifier in zip(polydata_list, identifier_list):
        rad_file_content += from_polydata_to_dot_rad_str(polydata, identifier)
    with open(path_rad_file, "w") as f:
        f.write(rad_file_content)


def from_polydata_to_dot_rad_str(polydata: PolyData, identifier: str) -> str:
    """
    Convert a PolyData to a Radiance string to be saved in a .rad file.
    :param polydata: PolyData, the polydata to convert.
    :param identifier: str, the identifier of the object.
    :return: str, the Radiance string.
    """
    rad_file_content = ""
    vertices = polydata.points
    rad_file_content += f"void glow sur_{identifier}" + "\n"
    rad_file_content += f"0" + "\n"
    rad_file_content += f"0" + "\n"
    rad_file_content += f"4 1 1 1 0" + "\n"
    rad_file_content += f"sur_{identifier} polygon surface.{identifier}" + "\n"
    rad_file_content += f"0" + "\n"
    rad_file_content += f"0" + "\n"
    nb_coords = len(vertices) * 3
    rad_file_content += (f"{nb_coords}")
    for v in vertices:
        rad_file_content += f" {v[0]} {v[1]} {v[2]}\n"

    return rad_file_content


