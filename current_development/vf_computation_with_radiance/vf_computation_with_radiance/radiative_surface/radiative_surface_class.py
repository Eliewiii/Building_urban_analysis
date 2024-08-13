"""
Class of surfaces for radiative simulations
"""

from copy import deepcopy

from pyvista import PolyData
from typing import List

from ..utils import from_polydata_to_dot_rad_str


class RadiativeSurface:
    """
    Class of surfaces for radiative simulations
    """

    def __init__(self, identifier: str):
        self.identifier: str = identifier
        self.hb_identifier: str = None
        self.polydata_geometry: PolyData = None
        self.viewed_surfaces_id_list: List = []
        self.viewed_surfaces_view_factor_list: List = []
        # Radiative properties
        self.emissivity: float = None
        self.reflectivity: float = None
        self.transmissivity: float = None
        # Preprocessed data for Radiance
        self.rad_file_content: str = None

    def __deepcopy__(self, memo={}):
        """
        Make a deepcopy of the RadiativeSurface object.
        """
        new_radiative_surface = RadiativeSurface(self.identifier)
        new_radiative_surface.hb_identifier = self.hb_identifier
        new_radiative_surface.polydata_geometry = deepcopy(self.polydata_geometry, memo)
        new_radiative_surface.viewed_surfaces_id_list = deepcopy(self.viewed_surfaces_id_list, memo)
        new_radiative_surface.viewed_surfaces_view_factor_list = deepcopy(self.viewed_surfaces_view_factor_list, memo)
        new_radiative_surface.emissivity = self.emissivity
        new_radiative_surface.reflectivity = self.reflectivity
        new_radiative_surface.transmissivity = self.transmissivity
        new_radiative_surface.rad_file_content = self.rad_file_content

        return new_radiative_surface

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
        if not isinstance(polydata, PolyData):
            raise ValueError(f"The polydata must be a PolyData object, not {type(polydata)}.")
        radiative_surface_obj = cls(identifier)
        radiative_surface_obj.polydata_geometry = polydata
        radiative_surface_obj.rad_file_content = from_polydata_to_dot_rad_str(polydata, identifier)

        return radiative_surface_obj

    def add_viewed_surfaces(self, viewed_surface_id_list: List[str]):
        """
        Add a viewed surface to the current surface.
        :param viewed_surface_id_list: str or [str], the identifier of the viewed surface.
        """
        for viewed_surface_id in viewed_surface_id_list:
            if viewed_surface_id not in self.viewed_surfaces_id_list:
                self.viewed_surfaces_id_list.append(viewed_surface_id)
            else:
                raise ValueError(f"The surface {viewed_surface_id} is already in the viewed surfaces list.")

    def get_viewed_surfaces_id_list(self):
        """
        Get the list of identifiers of the surfaces viewed by the current surface.
        """
        return self.viewed_surfaces_id_list

    def generate_rad_file_name(self) -> (str, str, str):
        """
        Generate the name of the Radiance file from the identifier without the extension and batch number.
        :return: str, the name of the emitter Radiance file.
        :return: str, the name of the receiver Radiance file.
        :return: str, the name of the output Radiance file.
        """
        name_emitter_rad_file = f"emitter_{self.identifier}"
        name_receiver_rad_file = f"receiver_{self.identifier}_batch_"
        name_output_file = f"output_{self.identifier}_batch_"
        return name_emitter_rad_file, name_receiver_rad_file, name_output_file