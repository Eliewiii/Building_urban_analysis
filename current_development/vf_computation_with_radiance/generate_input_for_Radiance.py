"""

"""
import os
import subprocess

from pyvista import PolyData
import numpy as np


def run_command_in_batches(command_list: [str], command_batch_size: int):
    """
    Run a list of commands in batches.
    :param command_list: [str], the list of commands to run.
    :param batch_size: int, the size of the batch.
    """
    nb_commands = len(command_list)
    # Split the commands into batches
    if nb_commands < command_batch_size:
        command_batches = [command_list]
    # Create batches for each list
    else:
        command_batches = []
        for start in range(0, nb_commands, command_batch_size):
            end = min(start + command_batch_size, nb_commands)
            batch = command_list[start: end]
            command_batches.append(batch)

    for command_batch in command_batches:
        command = " & ".join(command_batch)
        subprocess.run(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def write_radiance_command_for_vf_computation(path_emitter_rad_file: str, path_receiver_rad_file: str,
                                              path_output_file: str, path_octree_context: str = "",
                                              nb_rays: int = 10000):
    """
    Compute the view factor between 2 rectangles with Radiance.
    :param path_emitter_rad_file: str, the path of the emitter Radiance file.
    :param path_receiver_rad_file: str, the path of the receiver Radiance file.
    :param path_output_file: str, the path of the output file.
    :param path_octree_context: str, the path of the octree file.
    :param nb_rays: int, the number of rays to use.
    """
    # Check if the paths of emitter and receiver files exist
    check_file_exist(path_emitter_rad_file)
    check_file_exist(path_receiver_rad_file)
    # Check if the folder of the output file exists
    check_parent_folder_exist(path_output_file)
    # Check if the octree file exists if provided
    if path_octree_context and not os.path.exists(path_octree_context):
        raise FileNotFoundError(f"File not found: {path_octree_context}")
    # Compute the view factor
    command = f'rfluxmtx -h- -ab 0 -c {nb_rays} ' + f'"!xform -I "{path_emitter_rad_file}"" ' + (
        f'"{path_receiver_rad_file}"')
    if path_octree_context:
        command += f' "{path_octree_context}"'
    command += f' > "{path_output_file}"'


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


def compute_vf_between_emitter_and_receivers_radiance(path_emitter_rad_file: str, path_receiver_rad_file: str,
                                                      path_output_file: str, path_octree_context: str = "",
                                                      nb_rays: int = 10000):
    """
    Compute the view factor between 2 rectangles with Radiance.
    :param path_emitter_rad_file: str, the path of the emitter Radiance file.
    :param path_receiver_rad_file: str, the path of the receiver Radiance file.
    :param path_output_file: str, the path of the output file.
    :param path_octree_context: str, the path of the octree file.
    :param nb_rays: int, the number of rays to use.
    """
    # Check if the paths of emitter and receiver files exist
    check_file_exist(path_emitter_rad_file)
    check_file_exist(path_receiver_rad_file)
    # Check if the folder of the output file exists
    check_parent_folder_exist(path_output_file)
    # Check if the octree file exists if provided
    if path_octree_context and not os.path.exists(path_octree_context):
        raise FileNotFoundError(f"File not found: {path_octree_context}")
    # Compute the view factor
    command = f'rfluxmtx -h- -ab 0 -c {nb_rays} ' + f'"!xform -I "{path_emitter_rad_file}"" ' + (
        f'"{path_receiver_rad_file}"')
    if path_octree_context:
        command += f' "{path_octree_context}"'
    command += f' > "{path_output_file}"'
    subprocess.run(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def check_file_exist(file_path: str):
    """
    Check if a file exists and raise an error if not.
    :param file_path: str, the path of the file.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")


def check_parent_folder_exist(file_path: str):
    """
    Check if the parent folder of a file path exists and raise an error if not.
    :param file_path: str, the path of the file.
    """
    parent_folder = os.path.dirname(file_path)
    if not os.path.exists(parent_folder):
        raise FileNotFoundError(f"Folder not found: {parent_folder}")
