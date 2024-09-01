"""
We'll see, we need same first pass context filtering, with a different mvfc value, but the second filtering
will be much different
todo @Elie
"""
from bua.building.context_filter.building_context import BuildingContextFilter
from honeybee.model import Model


class BuildingLWRContextFilter(BuildingContextFilter):
    """ todo """

    def __init__(self):
        """ todo """
        super().__init__()  # inherit from all the attributes of the super class
        # Parameters
        self.surface_dict = {}

    def select_context_surfaces_for_lwr_computation(self, building_surfaces_dict: dict, urban_canopy_pyvista_mesh,
                                                    ray_arg):
        """ todo """


    def add_sky_and_ground_surface(self):
        """ todo """

    def generate_radiative_surface_dict_from_hb_model(self):
        """ todo """
        pass


    @staticmethod
    def _generate_radiative_surface_objects_from_hb_model(hb_model:Model):
        """ todo """

        def get_outdoor_faces_and_apertures_geometry_arrays(hb_model):
            None  # define in additionnal package

        hb_face_aperture_array_tuple_list = get_outdoor_faces_and_apertures_geometry_arrays(hb_model)

        radiative_surface_object_list = []
        for




        pass



