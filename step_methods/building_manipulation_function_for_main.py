"""

"""
import logging

dev_logger = logging.getLogger("dev")
user_logger = logging.getLogger("user")


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
        user_logger.info("Buildings have been moved to origin successfully")
        dev_logger.info("Buildings have been moved to origin successfully")

    @staticmethod
    def remove_building_list_from_urban_canopy(urban_canopy_object, building_id_list=None):
        """
        Remove a list of buildings from the urban canopy
        :param urban_canopy:
        :param building_list:
        :return:
        """
        for building_id in building_id_list:
            urban_canopy_object.remove_building_from_dict(building_id)
        user_logger.info("Building(s) removed from the urban canopy successfully")
        dev_logger.info("Building(s) removed from the urban canopy successfully")

    @staticmethod
    def make_oriented_bounding_boxes_of_buildings_in_urban_canopy(urban_canopy_object, overwrite=False):
        """
        Make oriented bounding boxes of buildings in the urban canopy
        :param urban_canopy_object:
        :return:
        """
        urban_canopy_object.make_oriented_bounding_boxes_of_buildings(overwrite=overwrite)
        user_logger.info("Oriented bounding boxes of buildings in the urban canopy have been made successfully")
        dev_logger.info("Oriented bounding boxes of buildings in the urban canopy have been made successfully")

    @staticmethod
    def make_merged_face_of_buildings_in_urban_canopy(urban_canopy_object, building_id_list=None,
                                                      orient_roof_mesh_to_according_to_building_orientation=True,
                                                      north_angle=0):
        """
        Make oriented bounding boxes of buildings in the urban canopy
        :param urban_canopy_object: urban canopy object
        :param building_id_list: list of building id to be considered
        :param orient_roof_mesh_to_according_to_building_orientation: bool: default=True if True, the roof mesh will be oriented according to the building orientation
        :param north_angle: number: default=0: number of degrees to rotate the roof mesh
        """

        urban_canopy_object.make_merged_faces_hb_model_of_buildings(building_id_list=building_id_list,
                                                                    orient_roof_mesh_to_according_to_building_orientation=orient_roof_mesh_to_according_to_building_orientation,
                                                                    north_angle=north_angle)
        user_logger.info("Honeybee models with merges faces of the buildings have been generated successfully")
        dev_logger.info("Honeybee models with merges faces of the buildings have been generated successfully")
