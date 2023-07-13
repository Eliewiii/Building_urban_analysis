"""

"""
from mains_tool.utils_general import *

user_logger = logging.getLogger("user")  # f"{__name__} user"
dev_logger = logging.getLogger("dev")  # f"{__name__} dev"


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
        user_logger.info("Building geometries extracted from the GIS file successfully")
        dev_logger.info("Building geometries extracted from the GIS file successfully")

    @classmethod
    def get_id_key_of_buildings_in_gis(cls, path_additional_gis_attribute_key_dict):
        """ Get the building_id_key_gis if it is given in the additional_gis_attribute_key_dict """
        # Initialize with default value
        building_id_key_gis = default_building_id_key_gis
        # Check if given in the additional_gis_attribute_key_dict
        if path_additional_gis_attribute_key_dict is not None and os.path.isfile(path_additional_gis_attribute_key_dict):
            # check if the file exist, it's not a mandatory input for the user
            with open(path_additional_gis_attribute_key_dict, "r") as f:
                additional_gis_attribute_key_dict = json.load(f)
                if "building_id_key_gis" in additional_gis_attribute_key_dict:
                    building_id_key_gis = additional_gis_attribute_key_dict["building_id_key_gis"]
        return building_id_key_gis

    @staticmethod
    def add_buildings_from_hbjson_to_urban_canopy(urban_canopy_object, path_folder_hbjson, path_file_hbjson, are_buildings_targets):
        """
        Add buildings from a folder of hbjson files to the urban canopy
        :param urban_canopy_object:
        :param path_folder_hbjson: path to the folder containing the hbjson files
        """
        urban_canopy_object.add_buildings_from_hbjson_to_dict(path_directory_hbjson=path_folder_hbjson,path_file_hbjson=path_file_hbjson,are_buildings_targets=are_buildings_targets)
        user_logger.info("Building(s) from hbjson added to the urban canopy successfully")
        dev_logger.info("Building(s) from hbjson added to the urban canopy successfully")
