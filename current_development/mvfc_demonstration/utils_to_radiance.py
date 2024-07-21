"""
Functions to convert data from pyvista to the Radiance model.
"""

import os
import subprocess

from pyvista import Rectangle


def compute_vf_between_2_rectangles_with_radiance(rectangle_emitter: Rectangle, rectangle_receiver: Rectangle,
                                                  path_temp_folder: str, nb_rays: int = 10000):
    """
    Compute the view factor between 2 rectangles with Radiance.
    :param rectangle_emitter: Rectangle, the emitter rectangle.
    :param rectangle_receiver: Rectangle, the receiver rectangle.
    :param path_temp_folder: str, the path of the folder to save the Radiance files.
    :param nb_rays: int, the number of rays to use.
    """

    # Save the rectangles as Radiance files
    path_emitter_rad_file = os.path.join(path_temp_folder, "emitter.rad")
    path_receiver_rad_file = os.path.join(path_temp_folder, "receiver.rad")
    from_rectangle_to_rad_file(rectangle_emitter,path_emitter_rad_file, id_rectangle=1)
    from_rectangle_to_rad_file(rectangle_receiver,path_receiver_rad_file, id_rectangle=2)
    # Compute the view factor
    out_file = os.path.join(path_temp_folder, "output.txt")
    command = f'rfluxmtx -h- -ab 0 -c {nb_rays} ' + f'"!xform -I "{path_emitter_rad_file}"" ' + f'"{path_receiver_rad_file}" > "{out_file}"'
    subprocess.run(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    return read_ruflumtx_output_file(out_file)


def from_rectangle_to_rad_file(rectangle: Rectangle, path_rad_file: str, id_rectangle: int):
    """
    Convert a rectangle to a Radiance file.
    :param rectangle: Rectangle, the rectangle to convert.
    :param path_rad_file: str, the path of the Radiance file to save.
    """
    v = rectangle.points
    with open(path_rad_file, "w") as file:
        rad_file_content = r"#@rfluxmtx h=u" + "\n"
        rad_file_content += f"void glow sur_{id_rectangle}" + "\n"
        rad_file_content += f"0" + "\n"
        rad_file_content += f"0" + "\n"
        rad_file_content += f"4 1 1 1 0" + "\n"
        rad_file_content += f"sur_{id_rectangle} polygon surface.{id_rectangle}" + "\n"
        rad_file_content += f"0" + "\n"
        rad_file_content += f"0" + "\n"
        rad_file_content += f"12 {v[0][0]} {v[0][1]} {v[0][2]}" + "\n"
        rad_file_content += f" {v[1][0]} {v[1][1]} {v[1][2]}" + "\n"
        rad_file_content += f" {v[2][0]} {v[2][1]} {v[2][2]}" + "\n"
        rad_file_content += f" {v[3][0]} {v[3][1]} {v[3][2]}" + "\n"
        file.write(rad_file_content)

def read_ruflumtx_output_file(path_output_file:str):
    """
    Read the output file of rfluxmtx.
    :param path_output_file: str, the path of the output file.
    :return: dict, the view factor between the 2 rectangles.
    """
    with open(path_output_file, "r") as file_rad:
        data = file_rad.read().split("\t")
        return float(data[0])