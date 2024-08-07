"""
Class of surfaces for radiative simulations
"""

from pyvista import PolyData

from .utils_generate_input_for_radiance import from_polydata_to_dot_rad_str


class RadiativeSurface:
    """
    Class of surfaces for radiative simulations
    """

    def __init__(self, identifier: str):
        self.identifier = None
        self.hb_identifier = None
        self.polydata_geometry = None
        self.viewed_surfaces_id_list = []
        self.viewed_surfaces_view_factor_list = []
        # Radiative properties
        self.emissivity = None
        self.reflectivity = None
        self.transmissivity = None
        # Preprocessed data for Radiance
        self.rad_file_content = None

    @classmethod
    def from_hb_face_object(cls, hb_face_object):
        """
        Convert a Honeybee face object to a RadiativeSurface object.
        :param hb_face_object: Honeybee face object.
        """
        # Get the identifier

        # Create the RadiativeSurface object

        # Convert the Honeybee face object to a PolyData

        # Set the geometry and radiative properties

        # Make the Radiance string

    @classmethod
    def from_polydata(cls, identifier: str, polydata: PolyData):
        """
        Convert a PolyData to a RadiativeSurface object.
        :param identifier: str, the identifier of the object.
        :param polydata: PolyData, the polydata to convert.
        """
        radiative_surface_obj = cls(identifier)
        radiative_surface_obj.polydata_geometry = polydata
        radiative_surface_obj.rad_file_content = from_polydata_to_dot_rad_str(polydata, identifier)

        return radiative_surface_obj

    def get_viewed_surfaces_id_list(self):
        """
        Get the list of identifiers of the surfaces viewed by the current surface.
        """
        return self.viewed_surfaces_id_list
