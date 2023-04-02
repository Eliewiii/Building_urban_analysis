"""
Urban canopy class, containing and managing collections of buildings in urban areas.
"""

import os
import logging
import pickle

#from honeybee.model import Model
from honeybee.room import Room
#this can be replaced with these:
#from libraries_addons.hb_model_addons import *
from building.building_basic import BuildingBasic
from building.building_modeled import BuildingModeled
from gis.extract_gis import extract_gis
from typology.typology import Typology


class UrbanCanopy:

    def __init__(self):
        """Initialize the Urban Canopy"""
        #
        self.building_dict = {}  # dictionary of the buildings in the urban canopy
        self.typology_dict = {}  # dictionary of the typologies loaded the urban canopy

        # Move
        self.moving_vector_to_origin = None  # moving vector of the urban canopy that moved the urban canopy to the origin

    def __len__(self):
        """ Return the number of buildings in the urban canopy """
        return len(self.building_dict)

    # def __str__(self):
    #     """ what you see when you print the urban canopy object """
    #     return (f"The urban canopy is composed of {len(self)} buildings")
    #
    # def __repr__(self):
    #     """ what you see when you type the urban canopy variable in the console """
    #     return (f"The urban canopy is composed of {len(self)} buildings")

    @classmethod
    def make_urban_canopy_from_pkl(cls, path_pkl):
        """ Load the urban canopy from a pickle file """
        with open(path_pkl, 'rb') as f:
            # Load pickle file
            urban_canopy = pickle.load(f)
            # Load the buildings objects that might have some properties stored into dict (ex HB_models)
            urban_canopy.load_building_HB_attributes()
        return urban_canopy

    def export_urban_canopy_to_pkl(self, path_folder):
        """ Save the urban canopy to a pickle file """
        with open(os.path.join(path_folder, "urban_canopy.pkl"), 'wb') as f:
            # todo
            self.pickle_building_HB_attributes()
            # todo
            pickle.dump(self, f)

    def load_typologies(self, typo_folder_path):
        """ Load the typologies from the folder
         :param typo_folder_path: path to the folder containing the typologies
         :return: None
         """
        # todo : to improve @Sharon
        # get the list of all the typology from the typology folder
        typo_folders = os.listdir(typo_folder_path)
        # loop through the typology folders
        for typo in typo_folders:
            path_to_typo = os.path.join(typo_folder_path, typo)  # path to the given typology
            typo_obj = Typology.from_json(path_to_typo)  # make the typology object from the json file in the folder
            # todo: have a tuple as a key, ex: (year, shape_type), and the year might even be an interval, so maybe have
            #  a global variable with values associated to the year, ex: 1900-1945, 1945-1970, 1970-2000, 2000-2020
            self.typology_dict[typo_obj.identifier] = typo_obj  # add the typology to the urban canopy dictionary

    def load_building_HB_attributes(self):
        """ Load the buildings objects that might have some properties stored into dict (ex HB_models) """
        # todo @Elie or @Sharon: here there is only one function that works for any type of building, but maybe we will
        #  have to make a specific function for each type of building (like this it's simpler but maybe more confusing)
        for building_id, building_obj in self.building_dict.items():
            building_obj.load_HB_attributes()

    def pickle_building_HB_attributes(self):
        """ Pickle the buildings objects that might have some properties stored into dict (ex HB_models) """
        # todo: same as above
        for building_id, building_obj in self.building_dict.items():
            building_obj.pickle_HB_attributes()

    def add_building_to_dict(self, building_id, building_obj):
        """ Add a building to the urban canopy"""
        # check if the building id is already in the urban canopy
        if building_id in self.building_dict.keys():
            logging.warning(f"The building id {building_id} is already in the urban canopy, it will not"
                            f" be added again to the urban canopy")
        else:
            # add the building to the urban canopy
            self.building_dict[building_id] = building_obj

    def add_list_of_buildings_to_dict(self, building_id_list, building_obj_list):
        """ Add a list of buildings to the urban canopy"""
        for i, building_id in enumerate(building_id_list):
            building_obj = building_obj_list[i]
            self.add_building_to_dict(building_id, building_obj)

    def remove_building_from_dict(self, building_id):
        """
        Remove a building from the urban canopy
        :param building_id: id of the building to remove
        :return:
        """
        # remove the building from urban canopy building_dict
        self.building_dict.pop(building_id)

    def add_buildings_from_2D_GIS_to_dict(self, path_gis, building_id_key_gis="idbinyan", unit="m",
                                          additional_gis_attribute_key_dict=None):
        """ Extract the data from a shp file and create the associated buildings objects"""
        # Read GIS file
        shape_file = extract_gis(path_gis)
        # Check if the building_id_key_gis is an attribute in the shape file
        try:
            shape_file[building_id_key_gis]
        except KeyError:
            logging.error(
                f"The key {building_id_key_gis} is not an attribute of the shape file, the id will be generated automatically")
            raise
            # if the key is not valid, set it to None, and the building will automatically be assigned an id
            building_id_key_gis = None

        ## loop to create a building_obj for each footprint in the shp file
        number_of_buildings_in_shp_file = len(shape_file['geometry'])  # number of buildings in the shp file
        for building_index_in_GIS in range(0, number_of_buildings_in_shp_file):
            # create the building object
            building_id_list, building_obj_list = BuildingBasic.make_buildingbasic_from_GIS(self, shape_file,
                                                                                            building_index_in_GIS,
                                                                                            building_id_key_gis, unit)
            # add the building to the urban canopy if it is valid
            if building_obj_list is not None:
                self.add_list_of_buildings_to_dict(building_id_list, building_obj_list)

        # Collect the attributes to the buildings from the shp file
        for building in self.building_dict.values():
            building.extract_building_attributes_from_GIS(shape_file, additional_gis_attribute_key_dict)

    # todo : New, to test
    def add_buildings_from_hbjson_to_dict(self, path_directory_hbjson):
        """ Add the buildings from the hb models in the folder
        :param path_directory_hbjson: path to the directory containing the hbjson files
        :return: None
        """
        # Get the list of the hbjson files
        hbjson_files = [f for f in os.listdir(path_directory_hbjson) if f.endswith(".hbjson")]
        # Loop through the hbjson files
        for hbjson_file in hbjson_files:
            # Get the path to the hbjson file
            path_hbjson = os.path.join(path_directory_hbjson, hbjson_file)
            # Create the building object
            building_HB_model_obj, identifier = BuildingModeled.make_buildingmodeled_from_hbjson(
                path_hbjson=path_hbjson)
            # Add the building to the urban canopy
            self.add_building_to_dict(identifier, building_HB_model_obj)
        # todo @Sharon or @Elie : check that the list of the building ids is not empty or invalid
        # Add the new buildings to the UrbanCanopy building dict

    def make_HB_model_envelops_from_buildings(self, path_folder=None):
        """ Make the hb model for the building envelop and save it to hbjson file if the path is provided """
        # List of the hb rooms representing the building envelops
        # HB_room_envelop_list = [building.export_building_to_elevated_HB_room_envelop() for building in self.building_dict.values()] todo:to delete if it works
        HB_room_envelop_list = []  # Initialize the list
        for building in self.building_dict.values():
            if type(building) is BuildingBasic:  # Make an HB room by extruding the footprint
                HB_room_envelop_list.append(building.export_building_to_elevated_HB_room_envelop())
            elif type(building) is BuildingModeled:  # Extract the rooms from the HB model attribute of the building
                for HB_room in building.HB_model_obj.rooms:
                    HB_room_envelop_list.append(HB_room)
        # additional cleaning of the colinear vertices, might not be necessary
        for room in HB_room_envelop_list:
            room.remove_colinear_vertices_envelope(tolerance=0.01, delete_degenerate=True)
        # Make the hb model
        HB_model = Model(identifier="urban_canopy_building_envelops", rooms=HB_room_envelop_list, tolerance=0.01)
        HB_dict = HB_model.to_dict()
        if path_folder is not None:
            HB_model.to_hbjson(name="buildings_envelops", folder=path_folder)
        return HB_dict, HB_model

    def make_oriented_bounding_boxes_of_buildings(self, path_folder=None, hbjson_name=None):
        """ Make the oriented bounding boxes of the buildings in the urban canopy
        and save it to hbjson file if the path is provided """
        for building in self.building_dict.values():
            building.make_oriented_bounding_box()
        if path_folder is not None:
            # List of the hb rooms representing the building envelops
            bounding_boxes_HB_room_list = [
                Room.from_polyface3d(identifier=str(building.id), polyface=building.oriented_bounding_box) for building in
                self.building_dict.values()]
            HB_model = Model(identifier="urban_canopy_bounding_boxes", rooms=bounding_boxes_HB_room_list,
                             tolerance=0.01)
            HB_model.to_hbjson(name=hbjson_name, folder=path_folder)

    def compute_moving_vector_to_origin(self):
        """ Make the moving vector to move the urban canopy to the origin """
        # get the center of mass (Point3D) of the urban canopy on the x,y plane
        list_of_centroid = [building.LB_face_footprint.centroid for building in self.building_dict.values()]
        center_of_mass_x = sum([centroid.x for centroid in list_of_centroid]) / len(list_of_centroid)
        center_of_mass_y = sum([centroid.y for centroid in list_of_centroid]) / len(list_of_centroid)
        # Find the minimum elevation of the buildings in the urban canopy
        # The elevation of all building will be rebased considering the minimum elevation to be z=0
        min_elevation = min([building.elevation for building in self.building_dict.values()])

        self.moving_vector_to_origin = [-center_of_mass_x, -center_of_mass_y, -min_elevation]

    def move_buildings_to_origin(self):
        """ Move the buildings to the origin """

        # Check if the the urban canopy has already been moved to the origin
        if self.moving_vector_to_origin is not None:
            logging.info("The urban canopy has already been moved to the origin, the building will be moved back and"
                         " then moved again to the origin with the new buildings")
            # Move back the buildings to their original position
            self.move_back_buildings()
        # Compute the moving vector
        self.compute_moving_vector_to_origin()
        # Move the buildings
        for building in self.building_dict.values():
            building.move(self.moving_vector_to_origin)

    def move_back_buildings(self):
        """ Move back the buildings to their original position (in general to move them back again to the origin) """
        for building in self.building_dict.values():
            # Check if the building has been moved to the origin already
            if building.moved_to_origin:
                # Move by the opposite vector
                building.move([-coordinate for coordinate in self.moving_vector_to_origin])
