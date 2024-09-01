"""
We'll see, we need same first pass context filtering, with a different mvfc value, but the second filtering
will be much different
todo @Elie
"""
from building.context_filter.building_context import BuildingContextFilter


class BuildingLWRContextFilter(BuildingContextFilter):
    """ todo """

    def __init__(self):
        """ todo """
        super().__init__()  # inherit from all the attributes of the super class
        # Parameters
        self.surface_dict = {}




    def select_context_surfaces_for_lwr_computation(self,building_surfaces_dict,urban_canopy_pyvista_mesh):
        """

        """







    def add_skyand_ground_surface(self):
        """ todo """