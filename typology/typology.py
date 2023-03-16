"""
todo: adapt the code to the new structure of the tool
"""

import os
import logging

import json
from enum import Enum
from honeybee_energy.lib.constructionsets import construction_set_by_identifier
from honeybee_energy.lib.programtypes import program_type_by_identifier
from honeybee_energy.lib.materials import window_material_by_identifier
from honeybee_energy.lib.schedules import schedule_by_identifier
from honeybee_energy.lib.constructions import opaque_construction_by_identifier


class BuildingShapeType(Enum):
    square = 1
    L = 2
    H = 3
    rectangle = 4
    reference_BER = 5

    # more in the future


class BuildingUse(Enum):
    residential = 1
    office = 2
    # more in the future


class ShadeType(Enum):
    no_shade = 1  # does not apply shades (eventually remove the shades from the window material
    roller = 2  # the roller shade is applied automatically as it is consider in the window shaded material
    blinds = 3  # add manually blinds with a given slat angles and a schedules


class Typology:
    """
    Building Typology class
    Contains all the information to model buildings (except the one specific to each buildings (name, age, height)
    """

    def __init__(self, identifier, path_file_layout):

        # # # # # # # properties # # # # # # #
        self.identifier = identifier
        self.building_shape_type = None
        self.year = None
        self.nb_apartments_per_floor = None
        self.nb_cores_per_floor = None
        self.use = None
        self.first_floor_use = None
        ## HB sets ##
        self.constructions_set_id = None
        self.program_type_apartment_id = None
        self.program_type_core_id = None
        self.construction_int_wall_int_mass = None
        ## Windows ##
        self.window_floor_area_ratio_per_direction = None
        ## Internal Mass ##
        self.int_mass_surface_ratio = None  # in [m2/m2]
        # apartment footprint etc
        self.path_file_layout = path_file_layout
        # shadings
        self.shade_type = None
        self.blind_mat_and_sche = None

    #### Print and console ####
    def __str__(self):
        return ("Typology {}".format(self.identifier))

    def __repr__(self):
        return ("Typology {}".format(self.identifier))

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # #                      Properties             # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    @classmethod
    def from_json(cls, path):
        """
        Create typology object from json file.
        If some parameters are not available in the json file and are critical for the simulation, default values will be set
        * path      : path to the json file containing the typology details
        """
        logging.warning("extracting typology with path file :" + path)
        with open(path + "//typo_details.json", 'r') as f:
            # load json file
            json_dict = json.load(f)
            # create typology obj
            typo_obj = cls(identifier=json_dict["identifier"], path_file_layout=os.path.join(path, "layout"))

            # # # # # # # #  # # # # # # #         load each parameter individually         # # # # # # # # # # # # # #

            ### building_zon shape type ###
            try:
                json_dict["building_zon shape type"]
            except:
                logging.warning(
                    'Typology "{}" does not have building_zon type, it will be set as "residential" by default'.format(
                        typo_obj.identifier))
                typo_obj.building_shape_type = BuildingShapeType.square.name
            else:
                if json_dict["building_zon shape type"] in BuildingShapeType._member_names_:
                    typo_obj.building_shape_type = json_dict["building_zon shape type"]
                else:
                    logging.warning(
                        'Typology "{}" building_zon type is not correct, it will be set as "residential" by default'.format(
                            typo_obj.identifier))
                    typo_obj.building_shape_type = BuildingShapeType.square.name
            ### year ###
            try:
                json_dict["year"]
            except:
                logging.warning(
                    'Typology "{}" does not have a year, it will be set as 2000 by default'.format(typo_obj.identifier))
                typo_obj.year = 2000

            else:
                if (isinstance(json_dict["year"], int) or isinstance(json_dict["year"], float)) and json_dict[
                    "year"] > 0:
                    typo_obj.year = json_dict["year"]
                elif isinstance(json_dict["year"], list) and len(json_dict["year"]) == 2 and json_dict["year"][
                    0] > 0 and json_dict["year"][0] > 0:
                    typo_obj.year = json_dict["year"]
                else:
                    logging.warning('Typology "{}" year is not correct, it will be set as 2000 by default'.format(
                        typo_obj.identifier))
                    typo_obj.year = 2000

            ### number of apartment per floor ###
            try:
                json_dict["nb apartments per floor"]
            except:
                logging.warning(
                    'Typology "{}" does not have number of apartment per floor, it will be set as None by default'.format(
                        typo_obj.identifier))
                typo_obj.nb_apartments_per_floor = None
            else:
                if isinstance(json_dict["nb apartments per floor"], int) and json_dict["nb apartments per floor"] >= 0:
                    typo_obj.nb_apartments_per_floor = json_dict["nb apartments per floor"]
                else:
                    logging.warning(
                        'Typology "{}" number of apartment per floor is not correct, it will be set as None by default'.format(
                            typo_obj.identifier))
                    typo_obj.nb_apartments_per_floor = None
            ### nb_cores_per_floor ###
            try:
                json_dict["nb cores per floor"]
            except:
                logging.warning(
                    'Typology "{}" does not have a nb_cores_per_floor, it will be set as None by default'.format(
                        typo_obj.identifier))
                typo_obj.nb_cores_per_floor = None
            else:
                if isinstance(json_dict["nb cores per floor"], int) and json_dict["nb cores per floor"] >= 0:
                    typo_obj.nb_cores_per_floor = json_dict["nb cores per floor"]
                else:
                    logging.warning(
                        'Typology "{}" nb_cores_per_floor is not correct, it will be set as None by default'.format(
                            typo_obj.identifier))
                    typo_obj.nb_cores_per_floor = None
            ### use ###
            try:
                json_dict["use"]
            except:
                logging.warning(
                    'Typology "{}" does not have building_zon type, it will be set as "residential" by default'.format(
                        typo_obj.identifier))
                typo_obj.use = BuildingUse.residential.name
            else:
                if json_dict["use"] in BuildingUse._member_names_:
                    typo_obj.use = json_dict["use"]
                else:
                    logging.warning(
                        'Typology "{}" building_zon type is not correct, it will be set as "residential" by default'.format(
                            typo_obj.identifier))
                    typo_obj.use = BuildingUse.residential.name
            ### HB_sets ###
            try:
                json_dict["HB sets"]
            except:
                logging.warning(
                    'Typology "{}" does not have HB sets, it will be set with the defaults values for building_zon in Israel by default'.format(
                        typo_obj.identifier))
                typo_obj.constructions_set_id = "constructions set identifier"  # to add
                typo_obj.program_type_apartment_id = "IS_Residential_5282_Program"
                typo_obj.program_type_core_id = "IS_Residential_5282_Program"  # to modify with schedules without loads
            else:
                # constructions_set_id
                try:
                    construction_set_by_identifier(json_dict["HB sets"]["constructions set identifier"])
                except:
                    logging.warning(
                        'Typology "{}" constructions set is not in the HB library, it will be set with the default value fpr building_zon in Israel'.format(
                            typo_obj.identifier))
                    typo_obj.constructions_set_id = "constructions set identifier"  # to add
                else:
                    typo_obj.constructions_set_id = json_dict["HB sets"]["constructions set identifier"]
                # program_type_apartment_id
                try:
                    program_type_by_identifier(json_dict["HB sets"]["program type apartment identifier"])
                except:
                    logging.warning(
                        'Typology "{}" constructions set is not in the HB library, it will be set with the default value fpr building_zon in Israel'.format(
                            typo_obj.identifier))
                    typo_obj.program_type_apartment_id = "constructions set identifier"  # to add
                else:
                    typo_obj.program_type_apartment_id = json_dict["HB sets"]["program type apartment identifier"]
                # program_type_core_id
                try:
                    program_type_by_identifier(json_dict["HB sets"]["program type core identifier"])
                except:
                    logging.warning(
                        'Typology "{}" constructions set is not in the HB library, it will be set with the default value fpr building_zon in Israel'.format(
                            typo_obj.identifier))
                    typo_obj.program_type_core_id = "constructions set identifier"  # to add
                else:
                    typo_obj.program_type_core_id = json_dict["HB sets"]["program type core identifier"]

            ### window_floor_area_ratio_per_direction ###
            try:
                json_dict["window/floor area per direction"]
            except:
                logging.warning(
                    'Typology "{}" does not have window_floor_area_ratio_per_direction, it will be set as [0,0,0.1,0] by default'.format(
                        typo_obj.identifier))
                typo_obj.window_floor_area_ratio_per_direction = {"north": 0, "east": 0.2, "south": 0, "west": 0}
            else:
                try:
                    json_dict["window/floor area per direction"]["north"]
                    json_dict["window/floor area per direction"]["east"]
                    json_dict["window/floor area per direction"]["south"]
                    json_dict["window/floor area per direction"]["west"]
                except:
                    logging.warning(
                        'Typology "{}" window_floor_area_ratio_per_direction is not correct, it will be set as [0,0,0.1,0] by default'.format(
                            typo_obj.identifier))
                    typo_obj.window_floor_area_ratio_per_direction = {"north": 0, "east": 0.2, "south": 0, "west": 0}
                else:
                    if json_dict["window/floor area per direction"]["north"] >= 0 and \
                            json_dict["window/floor area per direction"]["east"] >= 0 and \
                            json_dict["window/floor area per direction"]["south"] >= 0 and \
                            json_dict["window/floor area per direction"]["west"] >= 0:
                        typo_obj.window_floor_area_ratio_per_direction = json_dict["window/floor area per direction"]
                    else:
                        logging.warning(
                            'Typology "{}" window_floor_area_ratio_per_direction is not correct, it will be set as [0,0,0.1,0] by default'.format(
                                typo_obj.identifier))
                        typo_obj.window_floor_area_ratio_per_direction = {"north": 0, "east": 0.2, "south": 0,
                                                                          "west": 0}

            ### internal mass ###
            try:
                json_dict["internal mass"]
            except:
                logging.warning(
                    'Typology "{}" does not have internal, it will be set with the defaults values for building_zon in Israel by default'.format(
                        typo_obj.identifier))
                typo_obj.construction_int_wall_int_mass = "IS_InternalWall_Residential+OfficeRef"
                typo_obj.int_mass_surface_ratio = 1.5
            else:
                # internal mass internal wall construction id
                try:
                    opaque_construction_by_identifier(
                        json_dict["internal mass"]["internal mass internal wall construction id"])
                except:
                    logging.warning(
                        'Typology "{}" internal mass construction is not in the library or is not mentioned, it will be set with the default value fpr building_zon in Israel'.format(
                            typo_obj.identifier))
                    typo_obj.construction_int_wall_int_mass = "IS_InternalWall_Residential+OfficeRef"
                else:
                    typo_obj.construction_int_wall_int_mass = json_dict["internal mass"][
                        "internal mass internal wall construction id"]
                # internal mass internal wall/floor surface ratio
                try:
                    json_dict["internal mass"]["internal mass internal wall/floor surface ratio"]
                except:
                    logging.warning(
                        'Typology "{}" does not have internal mass surface ratio, it will be set with the default value fpr building_zon in Israel'.format(
                            typo_obj.identifier))
                    typo_obj.int_mass_surface_ratio = 1.5
                else:
                    if (isinstance(json_dict["internal mass"]["internal mass internal wall/floor surface ratio"],
                                   float) or isinstance(
                        json_dict["internal mass"]["internal mass internal wall/floor surface ratio"], int)) and \
                            json_dict["internal mass"]["internal mass internal wall/floor surface ratio"] > 0:
                        typo_obj.int_mass_surface_ratio = json_dict["internal mass"][
                            "internal mass internal wall/floor surface ratio"]
                    else:
                        logging.warning(
                            'Typology "{}" internal mass surface ratio format is not correct, it will be set with the default value fpr building_zon in Israel'.format(
                                typo_obj.identifier))
                        typo_obj.int_mass_surface_ratio = 1.5

            ### shade parameters ###
            try:
                json_dict["shade parameters"]
            except:
                None
            else:
                # shading type
                try:
                    json_dict["shade parameters"]["shading type"]
                except:
                    logging.warning(
                        'Typology "{}" does not have shading type, it will be set as "no_shading" by default'.format(
                            typo_obj.identifier))
                    typo_obj.use = ShadeType.no_shade.name
                else:
                    if json_dict["shade parameters"]["shading type"] in ShadeType._member_names_:
                        typo_obj.use = json_dict["shade parameters"]["shading type"]
                    else:
                        logging.warning(
                            'Typology "{}" shading type is not correct, it will be set as "no_shading" by default'.format(
                                typo_obj.identifier))
                        typo_obj.use = ShadeType.no_shade.name
                    # blind material and schedule
                    if typo_obj.use == ShadeType.blinds.name:
                        try:
                            for position in json_dict["shade parameters"][
                                "blind material and schedule"]:  # if the loop doesn't fail it means that the materials and schedules exist
                                window_material_by_identifier(position["material"])
                                schedule_by_identifier(position["schedule"])
                        except:
                            logging.warning(
                                'Typology "{}" blinds are not defined properly or not in the library, it will be set with the default value fpr building_zon in Israel'.format(
                                    typo_obj.identifier))
                            # typo_obj.construction_int_wall_int_mass = "IS_InternalWall_Residential+OfficeRef"
                            # to do
                        else:
                            typo_obj.blind_mat_and_sche = json_dict["shade parameters"]["blind material and schedule"]

            # # first floor use
            # try :
            #     json_dict["first_floor_use"]
            # except:
            #     print('Typology "{}" does not have a first_floor_use, it will be set as None by default'.format(typo_obj.identifier) )
            #     typo_obj.first_floor_use = None
            #
            # else :
            #     if json_dict["building_zon shape type"] in BuildingFirstFloorUse._member_names_:
            #         typo_obj.building_shape_type = json_dict["building_zon shape type"]
            #         else:
            #         print('Typology "{}" first_floor_use is not correct, it will be set as "residential" by default'.format(typo_obj.identifier))
            #         typo_obj.building_type = 2000

            return (typo_obj)
