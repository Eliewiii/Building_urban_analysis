"""

"""
from mains_tool.utils_general import *

class SimulationLoadBuildingOrGeometry:

    @staticmethod
    def add_2D_GIS_to_urban_canopy(urban_canopy,path_gis,building_id_key_gis,unit,additional_gis_attribute_key_dict):
        """
        Add buildings in a 2D GIS to the urban canopy
        :param urban_canopy:
        :return:
        """
        urban_canopy.add_buildings_from_2D_GIS_to_dict(path_gis, building_id_key_gis, unit, additional_gis_attribute_key_dict)
        logging.info("Builing geometries extracted from the GIS file successfully")

    @staticmethod
    def get_building_id_key_gis(path_additional_gis_attribute_key_dict):
        """ Get the building_id_key_gis if it is given in the additional_gis_attribute_key_dict """
        # global building_id_key_gis, additional_gis_attribute_key_dict # todo @Sharon,why global variales
        building_id_key_gis = "idbinyan"  # default value, todo: take it as an argument as well
        additional_gis_attribute_key_dict = None
        # check if given in the additional_gis_attribute_key_dict
        if default_additional_gis_attribute_key_dict and os.path.isfile(path_additional_gis_attribute_key_dict):
            with open(path_additional_gis_attribute_key_dict, "r") as f:
                additional_gis_attribute_key_dict = json.load(f)
                if "building_id_key_gis" in additional_gis_attribute_key_dict:
                    building_id_key_gis = additional_gis_attribute_key_dict["building_id_key_gis"]
        return building_id_key_gis

    @staticmethod
    def add_buildings_in_hbjson_to_urban_canopy(urban_canopy,path_folder_hbjson):
        urban_canopy.add_buildings_from_hbjson_to_dict(path_directory_hbjson=path_folder_hbjson)
        logging.info("Building(s) from hbjson added to the urban canopy successfully")