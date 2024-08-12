"""
Test functions for the method and initialization of the RadiativeSurfaceManager class.
"""

from ...vf_computation_with_radiance import RadiativeSurfaceManager


def test_init_radiative_surface_manager():
    """
    Test the initialization of the RadiativeSurfaceManager class.
    """
    radiative_surface_manager = RadiativeSurfaceManager()
    assert radiative_surface_manager.radiative_surface_dict == {}
    assert radiative_surface_manager.context_octree == None
    assert radiative_surface_manager.radiance_argument_list == []


if __name__ == "__main__":
    None
