"""Provides a scripting component.
    Inputs:
        x: The x script variable
        y: The y script variable
    Output:
        a: The a output variable"""

__author__ = "elie-medioni"
__version__ = "2023.03.20"

gis_attribute_keys_dict = {}

if _name_ is not None:
    gis_attribute_keys_dict["name"] = _name_

    # same for the rest