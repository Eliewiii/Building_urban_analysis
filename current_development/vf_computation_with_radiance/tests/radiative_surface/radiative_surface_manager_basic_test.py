"""
Test functions for the RadiativeSurface class.
"""
import os
import pytest

from pyvista import PolyData

from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

from ...vf_computation_with_radiance import RadiativeSurfaceManager
from ...vf_computation_with_radiance.utils import create_folder

from .radiative_surface_test import radiative_surface_instance

test_file_dir = os.path.dirname(os.path.abspath(__file__))


@pytest.fixture(scope='function')
def radiative_surface_manager_instance():
    radiative_surface_manager_instance = RadiativeSurfaceManager()
    return radiative_surface_manager_instance


num_ref_rectangles = 10
num_random_rectangle = 10


@pytest.fixture(scope='function')
def radiative_surface_manager_instance_with_random_rectangles():
    radiative_surface_manager_instance = RadiativeSurfaceManager.from_random_rectangles(
        num_ref_rectangles=num_ref_rectangles,
        num_random_rectangle=num_random_rectangle,
        min_size=0.1, max_size=10,
        max_distance_factor=10,
        parallel_coaxial_squares=False
    )
    return radiative_surface_manager_instance


class TestRadiativeSurfaceManagerBasic:
    """
    Tests for basic functionalities of the RadiativeSurfaceManager class.
    """

    def test_init_radiative_surface_manager(self):
        """
        Test the initialization of the RadiativeSurfaceManager class.
        """
        radiative_surface_manager = RadiativeSurfaceManager()
        assert radiative_surface_manager.radiative_surface_dict == {}
        assert radiative_surface_manager.context_octree is None
        assert radiative_surface_manager.radiance_argument_list == []

    @pytest.mark.parametrize('radiative_surface_instance', [3], indirect=True)
    def test_add_radiative_surface(self, radiative_surface_manager_instance, radiative_surface_instance):
        """
        Test the add_radiative_surface method of the RadiativeSurfaceManager class.
        """
        radiative_surface_list = radiative_surface_instance
        radiative_surface_manager_instance.add_radiative_surfaces(radiative_surface_list)
        for radiative_surface in radiative_surface_list:
            assert radiative_surface.identifier in radiative_surface_manager_instance.radiative_surface_dict

    def test_init_radiative_surface_manager_with_random_rectangles(
            self,
            radiative_surface_manager_instance_with_random_rectangles
    ):
        """
        Test the initialization of the RadiativeSurfaceManager class with random rectangles.
        """
        radiative_surface_manager = radiative_surface_manager_instance_with_random_rectangles
        assert len(
            radiative_surface_manager.radiative_surface_dict) == num_random_rectangle * num_ref_rectangles + num_ref_rectangles
        for identifier, radiative_surface in radiative_surface_manager.radiative_surface_dict.items():
            assert radiative_surface.identifier == identifier
            if identifier.startswith("ref"):
                assert len(radiative_surface.viewed_surfaces_id_list) == num_random_rectangle


class TestRadiativeSurfaceManagerRadianceInputGeneration:
    """
    Tests for the generation of Radiance input files by the RadiativeSurfaceManager class.
    """

    @staticmethod
    def set_up_folders_for_radiance_files():
        # Create a temp folder for all the radiance files
        radiance_test_files_dir = os.path.join(test_file_dir, "radiance_test_files")
        create_folder(radiance_test_files_dir, overwrite=True)
        # Paths to emitter, receiver and output directory
        path_emitter_folder = os.path.join(radiance_test_files_dir, "emitter")
        path_receiver_folder = os.path.join(radiance_test_files_dir, "receiver")
        path_output_folder = os.path.join(radiance_test_files_dir, "output")
        return path_emitter_folder, path_receiver_folder, path_output_folder

    def test_generate_radiance_files(self, radiative_surface_manager_instance_with_random_rectangles):
        """
        Test the generate_radiance_files method of the RadiativeSurfaceManager class.
        """
        path_emitter_folder, path_receiver_folder, path_output_folder = self.set_up_folders_for_radiance_files()
        radiative_surface_manager = radiative_surface_manager_instance_with_random_rectangles
        nb_receiver_per_batch = 5
        radiative_surface_manager.generate_radiance_inputs_for_all_surfaces(
            path_emitter_folder=path_emitter_folder,
            path_receiver_folder=path_receiver_folder,
            path_output_folder=path_output_folder,
            nb_receiver_per_batch=nb_receiver_per_batch
        )
        # Check the number of files
        num_emitter = len(
            [identifier for identifier, rad_surface_obj in
             radiative_surface_manager.radiative_surface_dict.items() if
             len(rad_surface_obj.get_viewed_surfaces_id_list()) > 0])
        num_emitter_files = len(os.listdir(path_emitter_folder))
        assert num_emitter == num_emitter_files

    def test_generate_radiance_files_in_parallel(self,
                                                 radiative_surface_manager_instance_with_random_rectangles):
        """
        Test the generate_radiance_files method of the RadiativeSurfaceManager class.
        """
        path_emitter_folder, path_receiver_folder, path_output_folder = self.set_up_folders_for_radiance_files()
        radiative_surface_manager = radiative_surface_manager_instance_with_random_rectangles
        nb_receiver_per_batch = 5
        radiative_surface_manager.generate_radiance_inputs_for_all_surfaces_in_parallel(
            path_emitter_folder=path_emitter_folder,
            path_receiver_folder=path_receiver_folder,
            path_output_folder=path_output_folder,
            nb_receiver_per_batch=nb_receiver_per_batch,
            num_workers=4,
            batch_size=10,
            executor_type=ThreadPoolExecutor
        )
        # Check the number of files
        num_emitter = len(
            [identifier for identifier, rad_surface_obj in
             radiative_surface_manager.radiative_surface_dict.items() if
             len(rad_surface_obj.get_viewed_surfaces_id_list()) > 0])
        num_emitter_files = len(os.listdir(path_emitter_folder))
        assert num_emitter == num_emitter_files
