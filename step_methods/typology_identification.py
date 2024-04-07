"""
 Fucntions for identifying the typology of buildings.
"""
import logging

dev_logger = logging.getLogger("dev")
user_logger = logging.getLogger("user")


class TypologyIdentificationFunctions:
    """

    """

    @staticmethod
    def identify_typology_of_buildings_in_urban_canopy(urban_canopy_object, building_id_list=None):
        """
        Identify the typology of buildings in the urban canopy
        :param urban_canopy_object:
        :param building_id_list:
        :return:
        """
        # todo @Elie: the stats are the identification accuracy
        stats = urban_canopy_object.identify_typology_of_buildings(building_id_list=building_id_list)

        user_logger.info("Typology of buildings identified successfully")
        dev_logger.info("Typology of buildings identified successfully")

        return stats
