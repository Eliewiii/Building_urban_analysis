"""
Functions to load buildings or geometries from a 2D GIS, hbjson files or json files
"""

import os
import logging
import json

from utils.utils_default_values_user_parameters import default_path_gis, default_unit_gis, \
    default_building_id_key_gis

user_logger = logging.getLogger("user")  # f"{__name__} user"
dev_logger = logging.getLogger("dev")  # f"{__name__} dev"


class SimulationLoadBuildingOrGeometry:

    @staticmethod
    def add_2D_GIS_to_urban_canopy(urban_canopy, path_gis=default_path_gis,
                                   path_additional_gis_attribute_key_dict=None, unit=default_unit_gis):
        """
        Add buildings in a 2D GIS to the urban canopy
        :param urban_canopy:
        :param path_gis:
        :param path_additional_gis_attribute_key_dict:
        :param unit:
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
        if path_additional_gis_attribute_key_dict is not None and os.path.isfile(
                path_additional_gis_attribute_key_dict):
            # check if the file exist, it's not a mandatory input for the user
            with open(path_additional_gis_attribute_key_dict, "r") as f:
                additional_gis_attribute_key_dict = json.load(f)
                if "building_id_key_gis" in additional_gis_attribute_key_dict and additional_gis_attribute_key_dict[
                    "building_id_key_gis"] is not None:
                    building_id_key_gis = additional_gis_attribute_key_dict["building_id_key_gis"]
        return building_id_key_gis

    @staticmethod
    def add_buildings_from_hbjson_to_urban_canopy(urban_canopy_object, path_folder_hbjson, path_file_hbjson,
                                                  are_buildings_targets=False, keep_context_from_hbjson=False):
        """
        Add buildings from a folder of hbjson files to the urban canopy
        :param urban_canopy_object:
        :param path_folder_hbjson: path to the folder containing the hbjson files
        :param path_file_hbjson: path to the hbjson file
        :param are_buildings_targets: if True, the buildings will be considered as targets
        :param keep_context_from_hbjson: if True, the context of the buildings will be kept
        """
        urban_canopy_object.add_buildings_from_hbjson_to_dict(path_directory_hbjson=path_folder_hbjson,
                                                              path_file_hbjson=path_file_hbjson,
                                                              are_buildings_targets=are_buildings_targets
                                                              , keep_context_from_hbjson=keep_context_from_hbjson)
        user_logger.info("Building(s) from hbjson added to the urban canopy successfully")
        dev_logger.info("Building(s) from hbjson added to the urban canopy successfully")

    @staticmethod
    def add_buildings_from_lb_polyface3d_json_in_urban_canopy(urban_canopy_object, path_lb_polyface3d_json_file,
                                                              typology=None,
                                                              other_options_to_generate_building=None):
        """
        Load buildings from a json file containing LB polyface3d objects. Use mostly to transfer Breps from Rhino to
        the urban canopy.
        :param urban_canopy_object: urban canopy object
        :param path_lb_polyface3d_json: path to the json file containing LB polyface3d objects
        :param typology: if None, it will use the default typology
        :param other_options_to_generate_building: other options to generate the building
        """
        urban_canopy_object.add_buildings_from_lb_polyface3d_json_to_dict(
            path_lb_polyface3d_json_file=path_lb_polyface3d_json_file, typology=typology,
            other_options_to_generate_building=other_options_to_generate_building)

        user_logger.info("Building(s) from lb polyface3d json added to the urban canopy successfully")
        dev_logger.info("Building(s) from lb polyface3d json added to the urban canopy successfully")
