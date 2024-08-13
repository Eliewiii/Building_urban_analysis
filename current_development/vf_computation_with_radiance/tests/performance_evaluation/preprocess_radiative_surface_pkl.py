"""

"""
import os
from time import time

from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

from current_development.vf_computation_with_radiance.tests.performance_evaluation.utils_performance_evaluation import \
    generate_radiance_files_in_parallel, init_radiative_surface_manager, \
    init_radiative_surface_manager_in_parallel, run_vf_computation


def main(path_simulation_folder: str):
    """
    Main function to evaluate the performance of the VF computation
    :param path_simulation_folder: str, the path of the simulation folder.
    """
    # Input geometry
    num_ref_rectangles = 500
    num_random_rectangle = 500
    min_size = 0.1
    max_size = 10
    max_distance_factor = 10
    # input parallelization
    num_workers = 8
    worker_batch_size = 10
    executor_type = ProcessPoolExecutor
    print(f"start init.")

    dur = time()
    # Initialize the radiative surface manager
    radiative_surface_manager_obj = init_radiative_surface_manager_in_parallel(
        num_ref_rectangles=num_ref_rectangles,
        num_random_rectangle=num_random_rectangle,
        min_size=min_size, max_size=max_size,
        max_distance_factor=max_distance_factor,
        num_workers=num_workers,
        worker_batch_size=1,
        executor_type=executor_type
    )
    print(f"Duration init parallel process: {time() - dur}s.")



    # radiative_surface_manager_obj.to_pkl(path_simulation_folder, "radiative_surface_manager.pkl")


if __name__ == "__main__":
    path_simulation_folder = r"D:\Elie\PhD\vf_computation"
    main(path_simulation_folder)
