"""Add  additional keys to load GIS attributes. GIS files can use different keys to store the same information (height, elevation...). This component allows you to add additional keys to the GIS attributes. Not all attributes need to be added as default value will be used if they cannot be extracted from the GIS, but certain attributes, such as the elevation, the height or the number can have a significant impact on the simulation results and it is recommended to add teh proper keys to extract them. It is mandatory to provide the key to identify the building ID in the GIS file. If this attribute does not exist add one manually in the GIS file with the QGIS software for instance. Only use GIS that use attributes keys and values with latin alphabet characters. Using other alphabets can lead to errors.
     Inputs:
        _building_id_key_gis: Key to identify the building ID in the GIS file.
        name_: List of keys to identify the name of the building in the GIS file. Keys already included: ["name", "full_name_"]
        age_: List of keys to identify the age of the building in the GIS file. Keys already included: ["age", "date", "year"]
        typology_: List of keys to identify the typology of the building in the GIS file. Keys already included: ["typo","typology","type","Typology"]
        elevation_: List of keys to identify the elevation of the building in the GIS file. Keys already included: ["minheight"]
        height_: List of keys to identify the height of the building in the GIS file. Keys already included: ["height", "Height","govasimple"]
        number_of_floor_: List of keys to identify the number of floors of the building in the GIS file. Keys already included: ["number_floor", "nb_floor", "mskomot"]
        group_: List of keys to identify the group of the building in the GIS file. Keys already included: ["group"]
    Output:
        gis_attribute_key_dict: Dictionary containing the additional keys to load GIS attributes.
"""

__author__ = "elie-medioni"
__version__ = "2024.03.31"

ghenv.Component.Name = "BUA Add GIS Attribute Keys"
ghenv.Component.NickName = 'AddGISAttributeKeys'
ghenv.Component.Message = '1.0.0'
ghenv.Component.Category = 'BUA'
ghenv.Component.SubCategory = '1 :: Load Buildings'
ghenv.Component.AdditionalHelpFromDocStrings = "1"

import json

# Initialize the replacement scenario parameter dictionary
gis_attribute_key_dict = {
    "building_id_key_gis": None,
    "name": [],
    "age": [],
    "typology": [],
    "elevation": [],
    "height": [],
    "number of floor": [],
    "group": []
}

# Check the _building_id_key_gis
if _building_id_key_gis is not None:
    gis_attribute_key_dict["building_id_key_gis"] = _building_id_key_gis
# Check the name_
if name_ is not None:
    gis_attribute_key_dict["name"] = name_
# Check the age_
if age_ is not None:
    gis_attribute_key_dict["age"] = age_
# Check the typology_
if typology_ is not None:
    gis_attribute_key_dict["typology"] = typology_
# Check the elevation_
if elevation_ is not None:
    gis_attribute_key_dict["elevation"] = elevation_
# Check the height_
if height_ is not None:
    gis_attribute_key_dict["height"] = height_
# Check the number_of_floor_
if number_of_floor_ is not None:
    gis_attribute_key_dict["number of floor"] = number_of_floor_
# Check the group_
if group_ is not None:
    gis_attribute_key_dict["group"] = group_

gis_attribute_key_dict = json.dumps(gis_attribute_key_dict)
