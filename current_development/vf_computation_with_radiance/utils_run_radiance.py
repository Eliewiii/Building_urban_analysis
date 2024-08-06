"""

"""

import os
import subprocess

from pyvista import PolyData
import numpy as np
from typing import List

from .utils_folder_manipulation import check_parent_folder_exist, check_file_exist


def run_radiant_vf_computation_in_batches(path_emitter_rad_file_list: List[str],
                                          path_receiver_rad_file_list: List[str],
                                          path_output_file_list: List[str],
                                          path_octree_context_list: List[str] = None,
                                          nb_rays: int = 10000, command_batch_size: int = 1):
    """
    Compute the view factor between multiple emitter and receiver with Radiance in batches.
    :param path_emitter_rad_file_list: [str], the list of paths of the emitter Radiance files.

    """
    # Generate the commands
    command_list = []
    for path_emitter_rad_file, path_receiver_rad_file, path_output_file, path_octree_context in zip(
            path_emitter_rad_file_list, path_receiver_rad_file_list, path_output_file_list, path_octree_context_list):
        write_radiance_command_for_vf_computation(path_emitter_rad_file, path_receiver_rad_file, path_output_file,
                                                  path_octree_context, nb_rays)
    # Run the commands in batches
    run_command_in_batches(command_list, command_batch_size)


def run_command_in_batches(command_list: List[str], command_batch_size: int):
    """
    Run a list of commands in batches.
    :param command_list: [str], the list of commands to run.
    :param command_batch_size: int, the size of the batch.
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
                                              path_output_file: str, path_octree_context: str = None,
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


def compute_vf_between_emitter_and_receivers_radiance(path_emitter_rad_file: str,
                                                      path_receiver_rad_file: str,
                                                      path_output_file: str,
                                                      path_octree_context: str = "",
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
