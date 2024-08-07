"""
Class that manages the whole LWR simulation, especially the RadiativeSurface objects.
"""

import os

from typing import List

from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

from .radiative_surface import RadiativeSurface
from .utils_generate_input_for_radiance import from_emitter_receiver_rad_str_to_rad_files
from .utils_batches import split_into_batches
from .utils_folder_manipulation import create_folder
from .utils_parallel_computing_with_return import parallel_computation_in_batches_with_return


class RadiativeSurfaceManager:
    """
    Class that manages the whole RadiativeSurface objects.
    """

    def __init__(self):
        self.radiative_surface_dict = {}
        self.context_octree = None
        self.radiance_argument_list = []

    def add_radiative_surfaces(self, *args):
        """
        Add multiple RadiativeSurface objects to the manager.
        """
        for radiative_surface_element_or_list in args:
            if isinstance(radiative_surface_element_or_list, list):
                for radiative_surface_obj in radiative_surface_element_or_list:
                    self.add_radiative_surface(radiative_surface_obj)
            elif isinstance(radiative_surface_element_or_list, RadiativeSurface):
                self.add_radiative_surface(radiative_surface_element_or_list)
            else:
                raise ValueError(
                    "The input object is not a RadiativeSurface object nor a list of RadiativeSurface objects.")

    def add_radiative_surface(self, radiative_surface: RadiativeSurface):
        """
        Add a RadiativeSurface object to the manager.
        :param radiative_surface: RadiativeSurface, the RadiativeSurface object to add.
        """
        if not isinstance(radiative_surface, RadiativeSurface):
            raise ValueError("The input object is not a RadiativeSurface object.")
        if radiative_surface.identifier in self.radiative_surface_dict:
            raise ValueError(
                f"The RadiativeSurface id {radiative_surface.identifier} object already exists in the surface manager.")
        self.radiative_surface_dict[radiative_surface.identifier] = radiative_surface

    def get_radiative_surface(self, identifier: str) -> RadiativeSurface:
        """
        Get a RadiativeSurface object from the manager.
        :param identifier: str, the identifier of the RadiativeSurface object.
        :return: RadiativeSurface, the RadiativeSurface object.
        """
        if identifier not in self.radiative_surface_dict:
            raise ValueError(f"The RadiativeSurface id {identifier} object does not exist in the surface manager.")
        return self.radiative_surface_dict[identifier]

    def make_context_octree(self):
        """
        Make the context octree for the Radiance simulation.
        """
        # todo: implement this method

    def add_argument_to_radiance_argument_list(self, arugument_list: List[List[str]]):
        """
        Add an argument to the Radiance argument list.
        :param args: the arguments to add.
        """
        self.radiance_argument_list.extend(arugument_list)

    def reinitialize_radiance_argument_list(self):
        """
        Reinitialize the Radiance argument list.
        """
        self.radiance_argument_list = []

    def generate_radiance_inputs_for_all_surfaces(self, path_folder_emitter: str, path_folder_receiver: str,
                                                  path_folder_output: str, nb_receiver_per_batch: int = 1):
        """
        Generate the Radiance input files for all the RadiativeSurface objects.
        :param path_folder_emitter: str, the folder path where the emitter Radiance files will be saved.
        :param path_folder_receiver: str, the folder path where the receiver Radiance files will be saved.
        :param path_folder_output: str, the folder path where the output Radiance files will be saved.
        :param nb_receiver_per_batch: int, the number of receivers in the receiver rad file per batch.
        """
        # Generate the folder if they don't exist
        create_folder(path_folder_emitter, path_folder_emitter, path_folder_output, overwrite=True)

        argument_list_to_add = []
        # Generate the Radiance files for each surface
        for radiative_surface_obj in self.radiative_surface_dict.values():
            argument_list_to_add.extend(
                self.generate_radiance_inputs_for_one_surface(radiative_surface_obj, path_folder_emitter,
                                                              path_folder_receiver, path_folder_output,
                                                              nb_receiver_per_batch))

        self.add_argument_to_radiance_argument_list(argument_list_to_add)

    def generate_radiance_inputs_for_all_surfaces_in_parallel(self, path_folder_emitter: str,
                                                              path_folder_receiver: str,
                                                              path_folder_output: str, nb_receiver_per_batch: int = 1,
                                                              num_workers=1, batch_size=1,
                                                              executor_type=ThreadPoolExecutor):
        """
        Generate the Radiance input files for all the RadiativeSurface objects in parallel.
        :param path_folder_emitter: str, the folder path where the emitter Radiance files will be saved.
        :param path_folder_emitter: str, the folder path where the emitter Radiance files will be saved.
        :param path_folder_receiver: str, the folder path where the receiver Radiance files will be saved.
        :param path_folder_output: str, the folder path where the output Radiance files will be saved.
        :param nb_receiver_per_batch: int, the number of receivers in the receiver rad file per batch.
        :param num_workers: int, the number of workers to use for the parallelization
        :param batch_size: int, the size of the batch of surfaces to process in parallel.
        :param executor_type: the type of executor to use for the parallelization.
        """
        # Generate the folder if they don't exist
        create_folder(path_folder_emitter, path_folder_receiver, path_folder_output, overwrite=False)
        # Split t
        argument_list_to_add = parallel_computation_in_batches_with_return(
            func=self.generate_radiance_inputs_for_one_surface,
            input_tables=list(self.radiative_surface_dict.values()),
            executor_type=executor_type,
            batch_size=batch_size,
            num_workers=num_workers,
            path_folder_emitter=path_folder_emitter,
            path_folder_receiver=path_folder_receiver,
            path_folder_output=path_folder_output,
            nb_receiver_per_batch=nb_receiver_per_batch)

        self.add_argument_to_radiance_argument_list(argument_list_to_add)

    def generate_radiance_inputs_for_one_surface(self, radiative_surface_obj: RadiativeSurface,
                                                 path_folder_emitter: str, path_folder_receiver: str,
                                                 path_folder_output: str, nb_receiver_per_batch: int = 1):
        """
        Generate the Radiance input files for one RadiativeSurface object.
        :param radiative_surface_obj: RadiativeSurface, the RadiativeSurface object.
        :param path_folder_emitter: str, the folder path where the emitter Radiance files will be saved.
        :param path_folder_receiver: str, the folder path where the receiver Radiance files will be saved.
        :param path_folder_output: str, the folder path where the output Radiance files will be saved.
        :param nb_receiver_per_batch: int, the number of receivers in the receiver rad file per batch. Each batch is
            simulated the with separate calls of Radiance and generate results in different files.
        """
        # Check if the surface has viewed surfaces aka simulation is needed
        if len(radiative_surface_obj.get_viewed_surfaces_id_list()) == 0:
            return
        # Get the rad_str of the emitter and receivers
        emitter_rad_str = radiative_surface_obj.rad_file_content
        receiver_rad_str_list = [self.get_radiative_surface[receiver_id].rad_file_content for receiver_id in
                                 radiative_surface_obj.get_viewed_surfaces_id_list()]
        receiver_rad_str_list_batches = split_into_batches(receiver_rad_str_list, nb_receiver_per_batch)
        # Generate the paths of the Radiance files
        name_emitter_rad_file, name_receiver_rad_file, name_output_file = radiative_surface_obj.generate_rad_file_name()
        path_emitter_rad_file = os.path.join(path_folder_emitter, name_emitter_rad_file + ".rad")
        #
        argument_list_to_add = []
        # Generate the Radiance files for each batch
        for i, batch in enumerate(receiver_rad_str_list_batches):
            path_receiver_rad_file = os.path.join(path_folder_receiver, name_receiver_rad_file + f"{i}.rad")
            path_output_file = os.path.join(path_folder_output, name_output_file + f"{i}.txt")
            # Generate the files
            from_emitter_receiver_rad_str_to_rad_files(emitter_rad_str=emitter_rad_str,
                                                       receiver_rad_str_list=batch,
                                                       path_emitter_rad_file=path_emitter_rad_file,
                                                       path_receiver_rad_file=path_receiver_rad_file,
                                                       path_output_file=path_output_file)

            # Add the Radiance argument to the list
            argument_list_to_add.append([path_emitter_rad_file, path_receiver_rad_file, path_output_file])

        return argument_list_to_add
