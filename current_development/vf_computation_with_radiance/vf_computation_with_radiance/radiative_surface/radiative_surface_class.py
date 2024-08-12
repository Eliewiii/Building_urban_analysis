"""
Class of surfaces for radiative simulations
"""

from pyvista import PolyData

from typing import List

from current_development.vf_computation_with_radiance.vf_computation_with_radiance.utils import from_polydata_to_dot_rad_str


class RadiativeSurface:
    """
    Class of surfaces for radiative simulations
    """

    def __init__(self, identifier: str):
        self.identifier = identifier
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
