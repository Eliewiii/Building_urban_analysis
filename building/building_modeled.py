"""
BuildingModeled class, representing one building in an urban canopy that will be converted in HB models
as they will be simulated
"""


from building.utils_building import *
from building.building_basic import BuildingBasic  # todo: cannot be imported from building.utils because of circular import (building.building_basic import utils)


class BuildingModeled(BuildingBasic):
    """BuildingBasic class, representing one building in an urban canopy."""
    # todo :make the LB_face_footprint optional in the BuildingBasic class
    def __init__(self, identifier, LB_face_footprint=None, urban_canopy=None, building_index_in_GIS=None, **kwargs):
        # Initialize with the inherited attributes from the BuildingBasic parent class
        super().__init__(identifier, LB_face_footprint, urban_canopy, building_index_in_GIS)
        # get the values from the original BuildingBasic object (if there is one) through **kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)

        self.HB_model_obj = None
        self.HB_model_dict = None
        self.to_simulate = False
        self.is_target = False

    def load_HB_attributes(self):
        """
        Load the attributes that cannot be pickled from equivalent attribute dict.
        """
        # Convert the HB_model_dict to HB_model_obj
        self.HB_model_obj = Model.from_dict(self.HB_model_dict)  # todo: test if it works
        self.HB_model_dict = None

    def pickle_HB_attributes(self):
        """
        Convert the HB_model_obj to HB_model_dict to be able to pickle it.
        """
        # Convert the HB_model_obj to HB_model_dict
        self.HB_model_dict = self.HB_model_obj.to_dict()  # todo: test if it works
        self.HB_model_obj = None
        # todo : maybe add more properties to modify before pickling to avoid locked class issue

    @classmethod
    def convert_buildingbasic_to_buildingmodeled(cls, building_obj, layout_from_typology=False,
                                                 automatic_subdivision=True,
                                                 properties_from_typology=True):
        """
        Create a BuildingModeled object from a BuildingBasic object
        :return: building_HB_model : BuildingModeled object
        """
        # Make the HB model from the building object
        # todo @Sharon : how to try to make the model ? and if it work we go further ? otherwise we return None ?
        HB_model = building_obj.to_HB_model(layout_from_typology=layout_from_typology,
                                            automatic_subdivision=automatic_subdivision,
                                            properties_from_typology=properties_from_typology)
        # get the attributes of the building_obj (it extract all attributes, even the ones that are used
        # to create the object), but it doesn't matter, it is just a bit redundant
        kwargs = {attr: getattr(building_obj, attr) for attr in dir(building_obj) if not attr.startswith('__')}
        # create the BuildingModeled object from the BuildingBasic object
        building_HB_model = cls(building_obj.id, building_obj.LB_face_footprint, building_obj.urban_canopy,
                                building_obj.index_in_GIS, **kwargs)
        # todo : @Sharon, check if the code is correct to create object from super class, should it be that way or though a to_buildingHBmodel function in the BuildingBasic class?

        return building_HB_model
        # todo : change if needed where the dictionary of the urban canopy is pointing, to point to the new object

    @classmethod
    def make_buildingmodeled_from_hbjson(cls, path_hbjson, urban_canopy=None):
        """
        Create a BuildingModeled object from a HBJSON file
        :return: building_HB_model : BuildingModeled object
        """
        # Load the HB model from the hbjson file
        HB_model = Model.from_hbjson(path_hbjson)
        # get the identifier the
        identifier = HB_model.identifier
        # create the BuildingModeled object from the HB model
        building_modeled_obj = cls(identifier)
        # Try to extract certain characteristics of the model from the HB_model
        elevation, height = HbAddons.elevation_and_height_from_HB_model(HB_model)
        # # set the attributes of the BuildingModeled object
        building_modeled_obj.HB_model_obj = HB_model
        building_modeled_obj.urban_canopy = urban_canopy
        building_modeled_obj.elevation = elevation
        building_modeled_obj.height = height
        # todo @Elie : make the LB_face_footprint from the HB_model
        building_modeled_obj.LB_face_footprint = HbAddons.make_LB_face_footprint_from_HB_model(HB_model=HB_model)
        # todo @Elie : finish the function (and check if it works)
        building_modeled_obj.moved_to_origin = True  # we assumed that the HB model is already in the proper place within the urban canopy

        return building_modeled_obj, identifier

    def select_context_surfaces_for_shading_computation(self, context_building_list,full_urban_canopy_Pyvista_mesh, minimum_vf_criterion):
        """ Select the context surfaces that will be used for the shading simulation of the current building.
        :param context_building_list: list of BuildingModeled objects
        :param minimum_vf_criterion: minimum view factor between surfaces to be considered as context surfaces
        in the first pass of the algorithm
        """
        # todo @ Elie: finish the function
        # Initialize variables
        list_building_kept_first_pass = []
        HB_Face_surfaces_kept_second_pass = []
        # First pass
        for context_building_obj in context_building_list:
            if context_building_obj.id != self.id: # does not take itself into account
                if is_bounding_box_context_using_mvfc_criterion(
                        target_LB_polyface3d_extruded_footprint=self.LB_polyface3d_extruded_footprint,
                        context_LB_polyface3d_oriented_bounding_box=context_building_obj.LB_polyface3d_oriented_bounding_box,
                        minimum_vf_criterion=minimum_vf_criterion):
                    None
                    # todo @Elie : add the buoiliding to the list of building kept in the first pass
                    # add the building to the list of building for the second path

                    # convert the buildingbasics into buildingmodeled (with typo identifier when it will work, put an empty function for now
                    # use the honeybee model to have the proper caracteristics of the surfsace

        # Second pass

        # for context_building_obj in list_building_kept_first_pass:
        #      for HB_face_surface in context_building_obj.HB_model_obj:
        #          if not is_HB_Face_context_surface_obstructed_for_target_LB_polyface3d(target_LB_polyface3d_extruded_footprint=self.LB_polyface3d_extruded_footprint , context_HB_Face_surface=HB_face_surface):
        #              None
        #             #todo



    def move(self, vector):
        """
        Move the building
        :param vector:
        :return:
        """
        # move the LB footprint
        if self.LB_face_footprint is not None:
            self.LB_face_footprint = self.LB_face_footprint.move(
                Vector3D(vector[0], vector[1], 0))  # the footprint is moved only in the x and y directions
        # adjust the elevation
        if self.elevation is not None:
            self.elevation = self.elevation + vector[2]
        # make it moved
        self.HB_model_obj.move(Vector3D(vector[0], vector[1], vector[2]))  # the model is moved fully
        self.moved_to_origin = True
