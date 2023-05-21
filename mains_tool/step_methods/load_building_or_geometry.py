"""

"""
from mains_tool.utils_general import *


class SimulationLoadBuildingOrGeometry:

    @staticmethod
    def add_2D_GIS_to_urban_canopy(urban_canopy, path_gis, path_additional_gis_attribute_key_dict, unit):
        """
        Add buildings in a 2D GIS to the urban canopy
        :param urban_canopy:
        :return:
        """
        # get the building_id_key_gis if it is given in the additional_gis_attribute_key_dict
        # if not it will use the default value
        building_id_key_gis = SimulationLoadBuildingOrGeometry.get_id_key_of_buildings_in_gis(
            path_additional_gis_attribute_key_dict)
        # Add the buildings from the GIS to the urban canopy
        urban_canopy.add_buildings_from_2D_GIS_to_dict(path_gis, building_id_key_gis, unit,
                                                       path_additional_gis_attribute_key_dict)
        logging.info("Builing geometries extracted from the GIS file successfully")

    @classmethod
    def get_id_key_of_buildings_in_gis(cls, path_additional_gis_attribute_key_dict):
        """ Get the building_id_key_gis if it is given in the additional_gis_attribute_key_dict """
        # Initialize with default value
        building_id_key_gis = default_building_id_key_gis
        # Check if given in the additional_gis_attribute_key_dict
        if os.path.isfile(path_additional_gis_attribute_key_dict):
            # check if the file exist, it's not a mandatory input for the user
            with open(path_additional_gis_attribute_key_dict, "r") as f:
                additional_gis_attribute_key_dict = json.load(f)
                if "building_id_key_gis" in additional_gis_attribute_key_dict:
                    building_id_key_gis = additional_gis_attribute_key_dict["building_id_key_gis"]
        return building_id_key_gis

    @staticmethod
    def add_buildings_from_hbjson_to_urban_canopy(urban_canopy, path_folder_hbjson):
        urban_canopy.add_buildings_from_hbjson_to_dict(path_directory_hbjson=path_folder_hbjson)
        logging.info("Building(s) from hbjson added to the urban canopy successfully")
