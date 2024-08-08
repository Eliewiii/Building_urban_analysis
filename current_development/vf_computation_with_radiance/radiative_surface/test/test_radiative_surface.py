"""
Test functions for the RadiativeSurface class.
"""


from current_development.vf_computation_with_radiance.radiative_surface.radiative_surface_class import RadiativeSurface

def test_init_radiative_surface():
    """
    Test the initialization of the RadiativeSurface class.
    """
    radiative_surface = RadiativeSurface("identifier")
    assert radiative_surface.identifier == None
    assert radiative_surface.hb_identifier == None
    assert radiative_surface.polydata_geometry == None
    assert radiative_surface.viewed_surfaces_id_list == []
    assert radiative_surface.viewed_surfaces_view_factor_list == []
    assert radiative_surface.emissivity == None
    assert radiative_surface.reflectivity == None
    assert radiative_surface.transmissivity == None
    assert radiative_surface.rad_file_content == None