"""
BuildingHBModel class, representing one building in an urban canopy that will be converted in HB models
as they will be simulated
"""

import logging

import dragonfly

from honeybee.model import Model
from ladybug_geometry.geometry3d import Vector3D

from building_ubem.building import Building

from libraries_addons.hb_model_addons import elevation_and_height_from_hb_model


class BuildingHBModel(Building):
    """Building class, representing one building in an urban canopy."""

    # todo :make the lb_footprint optional in the Building class
    def __init__(self, identifier, lb_footprint=None, urban_canopy=None, building_id_shp=None, **kwargs):
        # Initialize with the inherited attributes from the Building parent class
        super().__init__(identifier, lb_footprint, urban_canopy, building_id_shp)
        # get the values from the original Building object (if there is one) through **kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)

        self.hb_model_obj = None
        self.hb_model_dict = None

    def load_hb_attributes(self):
        """
        Load the attributes that cannot be pickled from equivalent attribute dict.
        """
        # Convert the hb_model_dict to hb_model_obj
        self.hb_model_obj = Model.from_dict(self.hb_model_dict)  # todo: test if it works
        self.hb_model_dict = None

    def pickle_hb_attributes(self):
        """
        Convert the hb_model_obj to hb_model_dict to be able to pickle it.
        """
        # Convert the hb_model_obj to hb_model_dict
        self.hb_model_dict = self.hb_model_obj.to_dict()  # todo: test if it works
        self.hb_model_obj = None
        # todo : maybe add more properties to modify before pickling to avoid locked class issue

    @classmethod
    def from_building(cls, building_obj, layout_from_typology=False, automatic_subdivision=True,
                      properties_from_typology=True):
        """
        Create a BuildingHBModel object from a Building object
        :return: building_hb_model : BuildingHBModel object
        """
        # Make the HB model from the building object
        # todo @Sharon : how to try to make the model ? and if it work we go further ? otherwise we return None ?
        hb_model = building_obj.to_hb_model(layout_from_typology=layout_from_typology,
                                            automatic_subdivision=automatic_subdivision,
                                            properties_from_typology=properties_from_typology)
        # get the attributes of the building_obj (it extract all attributes, even the ones that are used
        # to create the object), but it doesn't matter, it is just a bit redundant
        kwargs = {attr: getattr(building_obj, attr) for attr in dir(building_obj) if not attr.startswith('__')}
        # create the BuildingHBModel object from the Building object
        building_hb_model = cls(building_obj.id, building_obj.lb_footprint, building_obj.urban_canopy,
                                building_obj.shp_id, **kwargs)
        # todo : @Sharon, check if the code is correct to create object from super class, should it be that way or though a to_buildinghbmodel function in the Building class?

        return building_hb_model
        # todo : change if needed where the dictionnary of the urban canopy is pointing, to point to the new object

    @classmethod
    def from_hbjson(cls, path_hbjson, urban_canopy=None):
        """
        Create a BuildingHBModel object from a HBJSON file
        :return: building_hb_model : BuildingHBModel object
        """
        # Load the hb model from the hbjson file
        hb_model = Model.from_hbjson(path_hbjson)
        # get the identifier the
        identifier = hb_model.identifier
        # Try to extract certain characteristics of the model from the hb_model
        elevation, height = elevation_and_height_from_hb_model(hb_model)
        # create the BuildingHBModel object from the HB model
        building_hb_model = cls(identifier)
        # set the attributes of the BuildingHBModel object
        building_hb_model.hb_model = hb_model
        building_hb_model.urban_canopy = urban_canopy
        building_hb_model.elevation = elevation
        building_hb_model.height = height

        return building_hb_model

    def move(self, vector):
        """
        Move the building
        :param vector:
        :return:
        """
        # move the lb footprint
        if self.lb_footprint is not None:
            self.lb_footprint = self.lb_footprint.move(
                Vector3D(vector[0], vector[1], 0))  # the footprint is moved only in the x and y directions
        # adjust the elevation
        if self.elevation is not None:
            self.elevation = self.elevation + vector[2]
        # make it moved
        self.hb_model_obj.move(Vector3D(vector[0], vector[1], vector[2]))  # the model is moved fully
        self.moved_to_origin = True


def height_from_hb_model(hb_model):
    """
    Extract the height of the building from the hb model
    :param hb_model: honeybee model
    :return: height : float
    """
    # Get the height of the building from the hb model
    height = None  # todo
    return height


def elevation_from_hb_model(hb_model):
    """
    Extract the elevation of the building from the hb model
    :param hb_model:
    :return:
    """
    # todo : There is a high chance that the elevation will not be necessary,
    #  because the hb model is already at the right elevation, so wew might keep it at 0
    None


def lb_footprint_from_hb_model(hb_model):
    """
    Extract the footprint of the building from the hb model
    :param hb_model:
    :return:
    """

    # turn into dragonfly building
    dragonfly_building = dragonfly.Building.from_honeybee(hb_model)
    # get the footprint
    lb_footprint_list = dragonfly_building.footprint
    # merge LB footprint


def lb_faces_ground_bc_from_hb_model(hb_model):
    """
    Extract LB geometry faces 3D that have ground boundary condition from the HB model
    todo: not relevant if the building is on pillar...
    :param hb_model:
    :return:
    """
    # Init the list of LB geometry faces 3D that have ground boundary condition
    lb_face_ground_bc_list = []
    # Loop through the rooms of the HB model
    for room in hb_model.rooms:
        for face in room.faces:
            if face.boundary_condition.boundary_condition == "Ground":
                lb_face_ground_bc_list.append(face.geometry)

    return lb_face_ground_bc_list
