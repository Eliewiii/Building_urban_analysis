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
    def transform_buildingbasic_into_buildingmodeled_in_urban_canopy(urban_canopy_object, building_id_list=None,
                                                                     use_typology=True, typology_identification=False,
                                                                     are_simulated=False, are_target=False, **kwargs):
        """
        Transform a BuildingBasic objects into a BuildingModel object.
        If
        :param urban_canopy_object: urban canopy object
        :param building_id_list: list of building id to be considered
        :param use_typology: bool: default=True: if True, the typology will be used to define the properties of the BuildingModel object
        :param typology_identification: bool: default=False: if True, the typology identifier will be used to identify
            the typology of the BuildingModel object, the properties of the BuildingModel object will be defined
            according to the typology. (default=False)
        :param are_simulated: bool: default=False: if True, the BuildingModel object will be simulated
        :param are_target: bool: default=False: if True, the BuildingModel object will be a target
        :param kwargs: dict: additional parameters for the generation of the BuildingModel object
            autozoner: bool: default=False: if True, the thermal zones will be automatically generated
            use_layout_from_typology: bool: default=False: if True, the layout will be defined according to the typology
            use_properties_from_typology: bool: default=True: if True, the new building model will be generated according
            to the properties of the typology, especially the construction material and the window to wall ratio
        :return:
        """
        urban_canopy_object.transform_buildingbasic_into_building_model(building_id_list=building_id_list,
                                                                        use_typology=use_typology,
                                                                        typology_identification=typology_identification,
                                                                        are_simulated=are_simulated,
                                                                        are_target=are_target, **kwargs)
        # todo @Elie: add the logs
        # user_logger.info("Oriented bounding boxes of buildings in the urban canopy have been made successfully")
        # dev_logger.info("Oriented bounding boxes of buildings in the urban canopy have been made successfully")

    @staticmethod
    def make_lb_polyface3d_extruded_footprint_of_buildings_in_urban_canopy(urban_canopy_object, overwrite=False):
        """
        Make extruded footprints of buildings in the urban canopy in the Ladybug Polyface3D format
        :param urban_canopy_object: urban canopy object
        :param overwrite: bool: default=False: if True, the existing extruded footprints will be overwritten
        """

        urban_canopy_object.make_lb_polyface3d_extruded_footprint_of_buildings(overwrite=overwrite)

        user_logger.info("Extruded footprints of buildings in the urban canopy have been made successfully")
        dev_logger.info("Extruded footprints of buildings in the urban canopy have been made successfully")


    @staticmethod
    def make_oriented_bounding_boxes_of_buildings_in_urban_canopy(urban_canopy_object, overwrite=False):
        """
        Make oriented bounding boxes of buildings in the urban canopy
        :param urban_canopy_object:
        :param overwrite: bool: default=False: if True, the existing oriented bounding boxes will be overwritten
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
