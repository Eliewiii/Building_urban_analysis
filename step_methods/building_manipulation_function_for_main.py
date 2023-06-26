"""

"""
from mains_tool.utils_general import *

class SimulationBuildingManipulationFunctions:
    @staticmethod
    def move_buildings_to_origin(urban_canopy_object):
        """
        Move buildings to the origin of the plan (put the average elevation to 0)
        :param move_buildings_to_origin:
        :param urban_canopy_object:
        :return:
        """
        urban_canopy_object.move_buildings_to_origin()
        logging.info("Buildings have been moved to origin successfully")

    @staticmethod
    def remove_building_list_from_urban_canopy(urban_canopy_object,building_id_list):
        """
        Remove a list of buildings from the urban canopy
        :param urban_canopy:
        :param building_list:
        :return:
        """
        for building_id in building_id_list:
            urban_canopy_object.remove_building_from_dict(building_id)
        logging.info("Building(s) removed from the urban canopy successfully")

    @staticmethod
    def make_oriented_bounding_boxes_of_buildings_in_urban_canopy(urban_canopy_object, overwrite=False):
        """
        Make oriented bounding boxes of buildings in the urban canopy
        :param urban_canopy_object:
        :return:
        """
        urban_canopy_object.make_oriented_bounding_boxes_of_buildings(overwrite=overwrite)
        logging.info("Oriented bounding boxes of buildings in the urban canopy have been made successfully")