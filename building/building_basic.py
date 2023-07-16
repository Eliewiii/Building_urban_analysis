"""
BuildingBasic class, representing one building in an urban canopy.
"""


import logging
import shapely
from math import isnan

from ladybug_geometry.geometry3d import Vector3D
from libraries_addons.lb_face_addons import make_LB_polyface3D_oriented_bounding_box_from_LB_face3D_footprint, \
    LB_face_footprint_to_lB_polyface3D_extruded_footprint
from libraries_addons.hb_rooms_addons import RoomsAddons
from libraries_addons.function_for_gis_extraction_to_sort import polygon_to_LB_footprint,add_additional_attribute_keys_to_dict


user_logger = logging.getLogger("user")  # f"{__name__} user"
dev_logger = logging.getLogger("dev")  # f"{__name__} dev"

default_gis_attribute_key_dict = {
    "building_id_key_gis": "none",
    "name": ["name", "full_name_"],
    "age": ["age", "date", "year"],
    "typology": ["typo", "typology", "type", "Typology"],
    "elevation": ["minheight"],
    "height": ["height", "Height", "govasimple"],
    "number of floor": ["number_floor", "nb_floor", "mskomot"],
    "group": ["group"]
}


class BuildingBasic:
    """BuildingBasic class, representing one building in an urban canopy."""

    def __init__(self, identifier, LB_face_footprint, urban_canopy=None, building_index_in_GIS=None):
        """Initialize a building obj"""
        # urban canopy and key to access to the object from building_dict
        self.urban_canopy = urban_canopy
        self.id = identifier  # id of the building in the urban canopy building_dict
        # GIS specific
        self.index_in_GIS = building_index_in_GIS  # id in the shp file
        # Properties
        self.name = None  # name of the building (if available in the GIS)
        self.group = None  # group/neighbourhood of the building (if available in the GIS)
        self.age = None  # year the building was built
        self.typology = None  # typology of the building
        self.height = None  # height of the building in meter
        self.num_floor = None  # number of floor of the building
        self.elevation = 0  # elevation of the building in meter
        self.floor_height = None  # height of the floors in meter
        # Geometry
        self.LB_face_footprint = LB_face_footprint  # footprint of the building, including the holes in the LB geometry face format
        # Context filter algorithm
        self.LB_polyface3d_oriented_bounding_box = None  # oriented bounding box of the building
        self.LB_polyface3d_extruded_footprint = None  # extruded footprint of the building
        # Position
        self.moved_to_origin = False  # boolean to know if the building has been moved

    def load_HB_attributes(self):
        """ Load the attributes that cannot be pickled from equivalent attribute dict. """
        # for BuildingBasic not relevant yet, so nothing to do
        None

    def pickle_HB_attributes(self):
        """ Pickle the attributes that cannot be pickled. """
        # for BuildingBasic not relevant yet, so nothing to do
        None

    @classmethod
    def make_buildingbasic_from_LB_footprint(cls, LB_face_footprint, identifier, urban_canopy=None,
                                             building_index_in_GIS=None):
        """Generate a BuildingBasic from a Ladybug footprint."""
        return cls(identifier, LB_face_footprint, urban_canopy, building_index_in_GIS)

    @classmethod
    def make_buildingbasic_from_shapely_polygon(cls, polygon, identifier, unit, urban_canopy=None,
                                                building_index_in_GIS=None):
        """Generate a BuildingBasic from a shapely polygon."""
        LB_face_footprint = polygon_to_LB_footprint(polygon, unit)
        if LB_face_footprint is not None:
            return cls(identifier, LB_face_footprint, urban_canopy, building_index_in_GIS)
        else:
            return None

    @classmethod
    def make_buildingbasic_from_GIS(cls, urban_canopy, GIS_file, building_index_in_GIS, building_id_key_gis, unit):
        """
            Generate a building from a shp file.
            Can Eventually return multiple buildings if the footprint is a multipolygon.

            :param urban_canopy:
            :param GIS_file: GIS file
            :param building_index_in_GIS: id of the building in the shp file
            :param building_id_key_gis: key of the building id in the shp file
            :param unit: unit of the shp file
            :return: list of building ids and list of building objects
        """
        # Initialize the outputs
        building_id_list, building_obj_list = [], []
        # get the building id
        if building_id_key_gis is None:
            # if the building identifier is not specified in the shp file, use the index of the building in the shp file
            # todo: maybe convert into a string, the results are weird in GH, but not problematic
            building_id = building_index_in_GIS
        else:
            building_id = GIS_file[building_id_key_gis][building_index_in_GIS]
        # get the footprint of the building
        footprint = GIS_file['geometry'][building_index_in_GIS]

        # if the building footprint is a multipolygon
        if isinstance(footprint, shapely.geometry.polygon.Polygon):
            try:
                polygon_to_LB_footprint(footprint, unit)

            except:
                user_logger.warning("The footprint of the building id {building_id} in the GIS file could not be converted"
                                " to a Ladybug footprint. The building will be ignored.")
                dev_logger.warning("The footprint of the building id {building_id} in the GIS file could not be converted"
                                " to a Ladybug footprint. The building will be ignored.")
            else:
                building_obj = cls.make_buildingbasic_from_shapely_polygon(polygon=footprint, identifier=building_id,
                                                                           unit=unit,
                                                                           urban_canopy=urban_canopy,
                                                                           building_index_in_GIS=building_index_in_GIS)
                if building_obj is not None:
                    building_id_list.append(building_id)
                    building_obj_list.append(building_obj)


        # if the building footprint is a multipolygon
        elif isinstance(footprint, shapely.geometry.multipolygon.MultiPolygon):
            for i, polygon in enumerate(footprint.geoms):
                sub_building_id = "{building_id}_{i}"
                try:
                    polygon_to_LB_footprint(polygon, unit)
                except:
                    user_logger.warning(
                        "The footprint of the building id {sub_building_id} in the GIS file could not be converted"
                        " to a Ladybug footprint. The building will be ignored.")
                    dev_logger.warning(
                        "The footprint of the building id {sub_building_id} in the GIS file could not be converted"
                        " to a Ladybug footprint. The building will be ignored.")
                else:
                    building_obj = cls.make_buildingbasic_from_shapely_polygon(polygon=footprint,
                                                                               identifier=sub_building_id,
                                                                               urban_canopy=urban_canopy,
                                                                               building_index_in_GIS=building_index_in_GIS)
                    if building_obj is not None:
                        building_id_list.append(sub_building_id)
                        building_obj_list.append(building_obj)

        return building_id_list, building_obj_list

    def extract_building_attributes_from_GIS(self, GIS_file, additional_gis_attribute_key_dict=None):
        """
        Affect the properties of the building from a shp file.
        :param GIS_file: shp file
        :param additional_gis_attribute_key_dict: dictionary of additional keys to look for in the shp file
        """
        gis_attribute_key_dict = add_additional_attribute_keys_to_dict(default_gis_attribute_key_dict,
                                                                       additional_gis_attribute_key_dict)

        ## age ##
        for attribute_key in gis_attribute_key_dict["age"]:  # loop on all the possible name
            try:  # check if the property name exist
                int(GIS_file[attribute_key][self.index_in_GIS])
            except:  # if it doesn't, don't do anything
                None
            else:  # if it does, assign the information to the building_zon then break = get out of the loop
                if not isnan(int(GIS_file[attribute_key][self.index_in_GIS])):
                    self.age = int(GIS_file[attribute_key][self.index_in_GIS])
                    break
        ## name ##
        for attribute_key in gis_attribute_key_dict["name"]:
            try:
                str(GIS_file[attribute_key][self.index_in_GIS])
            except:
                None
            else:
                self.name = str(GIS_file[attribute_key][self.index_in_GIS])
                break
        ## group ##
        for attribute_key in gis_attribute_key_dict["group"]:
            try:
                str(GIS_file[attribute_key][self.index_in_GIS])
            except:
                None
            else:
                self.group = str(GIS_file[attribute_key][self.index_in_GIS])
                break
        ## height ##
        for attribute_key in gis_attribute_key_dict["height"]:
            try:
                float(GIS_file[attribute_key][self.index_in_GIS])
            except:
                None
            else:
                if not isnan(float(GIS_file[attribute_key][self.index_in_GIS])):
                    self.height = float(GIS_file[attribute_key][self.index_in_GIS])
                    break
        ## elevation ##
        for attribute_key in gis_attribute_key_dict["elevation"]:
            try:
                float(GIS_file[attribute_key][self.index_in_GIS])
            except:
                None
            else:
                if not isnan(float(GIS_file[attribute_key][self.index_in_GIS])):
                    self.elevation = float(GIS_file[attribute_key][self.index_in_GIS])

                    break
        ## number of floor ##
        for attribute_key in gis_attribute_key_dict["number of floor"]:
            try:
                int(GIS_file[attribute_key][self.index_in_GIS])
            except:
                None
            else:
                if not isnan(int(GIS_file[attribute_key][self.index_in_GIS])):
                    self.num_floor = int(GIS_file[attribute_key][self.index_in_GIS])
                    break

        ## typology ##
        for attribute_key in gis_attribute_key_dict["typology"]:
            try:
                str(GIS_file[attribute_key][self.index_in_GIS])
            except:
                None
            else:
                self.typology = str(GIS_file[attribute_key][self.index_in_GIS])
                break

        # check the property of the building, correct and assign default value if needed
        self.check_and_correct_property()

    def check_and_correct_property(self):
        """ check if there is enough information about the building"""
        # no valid height and no valid number of floor
        if ((type(self.height) != int or type(self.height) != float) or (
                self.height < 3)) and (type(self.num_floor) != int or self.num_floor < 1):
            self.height = 9.
            self.num_floor = 3
            self.floor_height = 3.
        # no valid height but valid number of floor
        elif ((type(self.height) != int or type(self.height) != float) or (
                self.height < 3)) and type(self.num_floor) == int and self.num_floor > 0:  # assume 3m floor height
            self.height = 3. * self.num_floor
            self.floor_height = 3.
        # no number of floor but valid height
        elif (type(self.num_floor) != int or self.num_floor < 1) and (
                type(self.height) == int or type(self.height) == float) and self.height >= 3:
            # assume approximately 3m floor height
            self.num_floor = self.height // 3.
            self.floor_height = self.height / float(self.num_floor)
        # both height and number of floor
        elif (type(self.height) == int or type(self.height) == float) and (type(
                self.num_floor) == int and self.num_floor > 0):  # both height and number of floor
            if 5. <= self.height / float(self.num_floor) <= 2.5:  # then ok
                self.floor_height = self.height / float(self.num_floor)
            else:  # prioritize the height
                self.num_floor = self.height // 3.
                self.floor_height = self.height / float(self.num_floor)
        else:  # not the proper format
            self.height = 9.
            self.num_floor = 3
            self.floor_height = 3.

    def make_LB_polyface3d_extruded_footprint(self, overwrite=False):
        """ make the oriented bounding box of the building
        :param overwrite: if True, overwrite the existing LB_polyface3d_oriented_bounding_box
        :return: LB_polyface3d_oriented_bounding_box, a LB Polyface3D object
        """
        if overwrite or self.LB_polyface3d_extruded_footprint is None:
            self.LB_polyface3d_extruded_footprint = LB_face_footprint_to_lB_polyface3D_extruded_footprint(
                LB_face_footprint=self.LB_face_footprint, height=self.height, elevation=self.elevation)

    def make_LB_polyface3d_oriented_bounding_box(self, overwrite=False):
        """ make the oriented bounding box of the building
        :param overwrite: if True, overwrite the existing LB_polyface3d_oriented_bounding_box
        :return: LB_polyface3d_oriented_bounding_box, a LB Polyface3D object
        """
        if overwrite or self.LB_polyface3d_oriented_bounding_box is None:
            self.LB_polyface3d_oriented_bounding_box = make_LB_polyface3D_oriented_bounding_box_from_LB_face3D_footprint(
                LB_face_footprint=self.LB_face_footprint, height=self.height, elevation=self.elevation)

    def move(self, vector):
        """
        Move the building to a new location
        :param vector: [x,y,z]
        """
        # move the LB footprint
        self.LB_face_footprint = self.LB_face_footprint.move(Vector3D(vector[0], vector[1], 0))
        # move the oriented bounding box if it exists
        if self.LB_polyface3d_oriented_bounding_box:
            self.LB_polyface3d_oriented_bounding_box = self.LB_polyface3d_oriented_bounding_box.move(
                Vector3D(vector[0], vector[1], 0))
        # adjust the elevation
        self.elevation = self.elevation + vector[2]
        # make it moved
        self.moved_to_origin = True

    def export_building_to_elevated_HB_room_envelop(self):
        """
        Convert the building to HB Room object showing the envelope of the building for plotting purposes
        or for context filtering
        :return: HB Room envelop
        """
        # convert the envelop of the building to a HB Room
        HB_room_envelop = RoomsAddons.LB_face_footprint_to_elevated_HB_room_envelop(LB_face_footprint=self.LB_face_footprint,
                                                                                    building_id=self.id,
                                                                                    height=self.height,
                                                                                    elevation=self.elevation)
        return HB_room_envelop

    def to_HB_model(self, layout_from_typology=False, automatic_subdivision=True, properties_from_typology=True):
        """ Convert the building to HB model
        :param properties_from_typology: If True, the properties of the building will be assigned based on the typology
        :param layout_from_typology: If True, the layout of the building will be assigned based on the typology
        :param automatic_subdivision: If True, and if the layout is not taken from the typology, footprint of
        the building will be subdivided automatically into apartments and cores based on the typology"""
        # todo: under construction @Elie
        if layout_from_typology:
            # todo: develop this feature later on,
            #  we'll only have one Room per floor or the automatic subdivision for now
            None
            # todo: maybe have it in a separate function
            # Load and copy the layout (footprint,apartment and cores) from the typology

            # move them to the location of the building (match the center of the footprints)

            # resize the layout to the size of the building footprint

            # rotate the layout to the orientation of the building centered on the centroid
            # (use a criteria with maximum intersection between the two footprints)

            # update the new footprint of the building

            # make the HB model with the new layout (windows,HVAC,etc.)
            # todo: consider building on pillars or with unconditioned ground floor if mentioned in the typology.
            #  in the future
        else:

            if automatic_subdivision:  # then divide the footprint into apartments and cores with Dragonfly
                None  # todo @Elie, not top priority
            else:  # then just create one room per floor with the actual LB_face_footprint
                None  # todo @Elie

        if properties_from_typology:  # Apply all the properties from the self.typology to the HB model
            None
        else:  # Apply the default properties to the HB model from the Typology "default"
            None  # todo @Elie

        HB_model = None  # todo @Elie: remove later, just not to show an error
        return HB_model


