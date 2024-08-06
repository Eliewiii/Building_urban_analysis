"""

"""

from time import time

from .utils_parallel_computing import parallel_computation_in_batches
from .utils_run_radiance import run_command_in_batches

from current_development.mvfc_demonstration.utils_random_rectangle_generation import \
    generate_random_rectangles


def compute_vf_with_radiance_in_parallel(nb_emitters_rectangles: int, nb_random_rectangles, nb_rays: int,
                                         path_folder_radiance_simulation: str, nb_batches: int = 1,
                                         nb_command_batch: int = 1, nb_workers: int = 1):
    """

    """

    # Generate the random rectangles
    random_polydata_emitters = []
    random_polydata_receivers_list = []
    for i in range(nb_emitters_rectangles):
        random_polydata_emitter, random_polydata_receivers = generate_random_rectangles(nb_random_rectangles,
                                                                                        path_folder_radiance_simulation)
        random_polydata_emitters.append(random_polydata_emitter)
        random_polydata_receivers_list.append(random_polydata_receivers)
    # Write the Radiance files and the list/tuples of imputs for the Radiance commands


    # Run the Radiance commands in parallel
