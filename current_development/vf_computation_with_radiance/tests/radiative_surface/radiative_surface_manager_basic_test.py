"""
Test functions for the RadiativeSurface class.
"""
import pytest

from pyvista import PolyData

from ...vf_computation_with_radiance import RadiativeSurfaceManager

from .radiative_surface_test import radiative_surface_instance


@pytest.fixture(scope='function')
def radiative_surface_manager_instance():
    radiative_surface_manager_instance = RadiativeSurfaceManager()
    return radiative_surface_manager_instance


num_ref_rectangles = 10
num_random_rectangle = 10


@pytest.fixture(scope='function')
def radiative_surface_manager_instance_with_radnom_rectangles():
    radiative_surface_manager_instance = RadiativeSurfaceManager.from_random_rectangles(
        num_ref_rectangles=num_ref_rectangles,
        num_random_rectangle=num_random_rectangle,
        min_size=0.1, max_size=10,
        max_distance_factor=10,
        parallel_coaxial_squares=False
    )
    return radiative_surface_manager_instance


class TestRadiativeSurfaceManagerBasic:

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
            radiative_surface_manager_instance_with_radnom_rectangles
    ):
        """
        Test the initialization of the RadiativeSurfaceManager class with random rectangles.
        """
        radiative_surface_manager = radiative_surface_manager_instance_with_radnom_rectangles
        assert len(radiative_surface_manager.radiative_surface_dict) == num_random_rectangle * num_ref_rectangles +num_ref_rectangles
        for identifier, radiative_surface in radiative_surface_manager.radiative_surface_dict.items():
            assert radiative_surface.identifier == identifier
            if identifier.startswith("ref"):
                assert len(radiative_surface.viewed_surfaces_id_list) == num_random_rectangle
