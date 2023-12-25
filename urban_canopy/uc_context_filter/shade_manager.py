"""
To manage the shade construction for the shade objects generated by the context filter
"""

import logging

from ladybug_geometry.geometry3d.face import Face3D
from honeybee.shade import Shade
from honeybee.face import Face
from honeybee.aperture import Aperture

from honeybee_energy.construction.shade import ShadeConstruction
from honeybee_energy.construction.window import WindowConstruction
from honeybee_energy.construction.windowshade import WindowConstructionShade
from honeybee_energy.construction.dynamic import WindowConstructionDynamic

user_logger = logging.getLogger("user")
dev_logger = logging.getLogger("dev")

default_solar_reflectance = 0.2
default_visible_reflectance = 0.2

class ShadeManager:
    """ Class to perform the context filtering on buildings """

    def __init__(self):
        # Parameter
        self.shade_construction_dict = {}
        # todo : make sure this can be pickeled, otherwise convert it to dict and unpack it at the end in the function
        #  in the urban canopy

    def from_hb_face_or_aperture_to_shade(self, hb_or_lb_object):
        """ Transform a HB Face or an Aperture (window) to a Shade object
        :param hb_or_lb_object: HB object, can be a HB Face or an Aperture (window)
        :return hb_shade-construction: ShadeConstruction
        """
        # Get the solar and visible reflectance of the HB object
        solar_reflectance, visible_reflectance = self.get_solar_and_visible_reflectance(hb_or_lb_object)
        # Get the shade construction from the dict if it exists, otherwise create it
        if (solar_reflectance, visible_reflectance) in self.shade_construction_dict:
            hb_shade_construction = self.shade_construction_dict[(solar_reflectance, visible_reflectance)]
        else:
            hb_shade_construction = self.create_shade_construction(solar_reflectance, visible_reflectance)
            self.shade_construction_dict[(solar_reflectance, visible_reflectance)] = hb_shade_construction

        # Create the shade object
        if isinstance(hb_or_lb_object, Face):
            hb_or_lb_object_geo = hb_or_lb_object.geometry
        elif isinstance(hb_or_lb_object, Aperture):
            # Move the aperture by 0.1m in the direction of the normal to avoid overlapping the facades
            hb_or_lb_object_geo = hb_or_lb_object.geometry  # copy of the geometry
            hb_or_lb_object_geo = hb_or_lb_object_geo.move(hb_or_lb_object_geo.normal, 0.01)
        elif isinstance(hb_or_lb_object, Face3D):
            hb_or_lb_object_geo = hb_or_lb_object
        else:
            raise ValueError("The object with the identifier {} is not a Honeybee Face or Aperture, it cannot be handled "
                             "by the context filter".format(hb_or_lb_object.identifier))
        hb_shade = Shade(
            identifier=hb_or_lb_object.identifer + "_shade",
            geometry=hb_or_lb_object_geo,
            is_detached=True,
            construction=hb_shade_construction
        )

        return hb_shade


    def get_solar_and_visible_reflectance(self, hb_or_lb_object):
        """
        Get the solar and visible reflectance of the HB object
        :param hb_or_lb_object: HB object, can be a HB Face or an Aperture (window)
        :return solar_reflectance: float
        :return visible_reflectance: float
        :return is_specular: boolean, true if the object is an Aperture/window

        """
        # If the object is a Honeybee Face
        if isinstance(hb_or_lb_object, Face):
            face_construction = hb_or_lb_object.properties.energy.construction
            solar_reflectance = face_construction.outside_solar_reflectance
            visible_reflectance = face_construction.outside_visible_reflectance
            is_specular = False

        # If the object is a Honeybee Aperture
        elif isinstance(hb_or_lb_object, Aperture):
            window_construction = hb_or_lb_object.properties.energy.construction
            if isinstance(window_construction, WindowConstruction):
                solar_reflectance = window_construction.outside_solar_reflectance
                visible_reflectance = window_construction.outside_visible_reflectance
            elif isinstance(window_construction, WindowConstructionShade):
                solar_reflectance = window_construction.window_construction.solar_reflectance
                visible_reflectance = window_construction.window_construction.visible_reflectance
                """
                Note that it is not possible to vary the reflectance through time (contrary the transmittance that can 
                have a schedule), so we assume that the reflectance are constant and have the values of the window, 
                not the shades. 
                """
            elif isinstance(window_construction, WindowConstructionDynamic):
                raise ValueError(
                    "One of the Aperture has WindowConstructionDynamic construction, which is not supported")
            else:
                raise ValueError("One of the Aperture has the {} construction, which is not supported".format(
                    window_construction.__class__.__name__))
            is_specular = True
        elif isinstance(hb_or_lb_object, Face3D):
            solar_reflectance = default_solar_reflectance
            visible_reflectance = default_visible_reflectance
        else:
            raise ValueError("The object with the identifier {} is not a Honeybee Face or Aperture, it cannot be handled "
                             "by the context filter".format(hb_or_lb_object.identifier))

        return solar_reflectance, visible_reflectance, is_specular


    def create_shade_construction(self, solar_reflectance, visible_reflectance):
        """ Create a shade construction with the solar and visible reflectance"""
        # Create the shade construction
        hb_shade_construction = ShadeConstruction(
            identifier="Context_filter_shade_construction_SR_{}_VR_{}".format(solar_reflectance, visible_reflectance),
            solar_reflectance=solar_reflectance,
            visible_reflectance=visible_reflectance
        )
        return hb_shade_construction
