"""
Test functions for the RadiativeSurface class.
"""
import pytest

from pyvista import PolyData

from ...vf_computation_with_radiance import RadiativeSurface

# Sample Polydata for testing
point_a = [1., 0., 0.]
point_b = [1., 1., 0.]
point_c = [0., 1., 0.]
point_d = [0., 0., 0.]
polydata_obj_1 = PolyData([point_a, point_b, point_c, point_d])


def test_init_radiative_surface():
    """
    Test the initialization of the RadiativeSurface class.
    """
    radiative_surface = RadiativeSurface("identifier")
    assert radiative_surface.identifier == "identifier"
    assert radiative_surface.hb_identifier is None
    assert radiative_surface.polydata_geometry is None
    assert radiative_surface.viewed_surfaces_id_list == []
    assert radiative_surface.viewed_surfaces_view_factor_list == []
    assert radiative_surface.emissivity is None
    assert radiative_surface.reflectivity is None
    assert radiative_surface.transmissivity is None
    assert radiative_surface.rad_file_content is None


def test_from_polydata():
    """
    Test the from_polydata method of the RadiativeSurface class.
    """
    radiative_surface = RadiativeSurface.from_polydata("identifier", polydata_obj_1)
    assert radiative_surface.identifier == "identifier"
    assert radiative_surface.hb_identifier is None
    assert radiative_surface.polydata_geometry == polydata_obj_1
    assert radiative_surface.viewed_surfaces_id_list == []
    assert radiative_surface.viewed_surfaces_view_factor_list == []
    assert radiative_surface.emissivity is None
    assert radiative_surface.reflectivity is None
    assert radiative_surface.transmissivity is None
    assert radiative_surface.rad_file_content is not None

    # Check the content of the rad file
    assert "identifier" in radiative_surface.rad_file_content
    assert "polygon" in radiative_surface.rad_file_content
    assert "void glow" in radiative_surface.rad_file_content
    assert str(len([point_a, point_b, point_c, point_d]) * 3) in radiative_surface.rad_file_content


def test_add_viewed_face():
    """
    Test the add_viewed_face method of the RadiativeSurface class.
    """
    radiative_surface = RadiativeSurface("identifier")
    # Add 2 viewed surface
    radiative_surface.add_viewed_surfaces(["viewed_surface_1", "viewed_surface_2"])
    assert radiative_surface.get_viewed_surfaces_id_list() == ["viewed_surface_1", "viewed_surface_2"]
    assert radiative_surface.viewed_surfaces_view_factor_list == []
    # Try to add the same viewed surface
    with pytest.raises(ValueError):
        radiative_surface.add_viewed_surfaces(["viewed_surface_1"])


def test_generate_rad_file_name():
    """
    Test the generate_rad_file_name method of the RadiativeSurface class.
    """
    radiative_surface = RadiativeSurface("identifier")
    name_emitter_rad_file, name_receiver_rad_file, name_output_file = radiative_surface.generate_rad_file_name()
    assert name_emitter_rad_file == "emitter_identifier"
    assert name_receiver_rad_file == "receiver_identifier_batch_"
    assert name_output_file == "output_identifier_batch_"
