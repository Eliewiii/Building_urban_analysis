"""
We'll see, we need same first pass context filtering, with a different mvfc value, but the second filtering
will be much different
"""
from building.context_filter.building_context import BuildingContext


class BuildingLWRContext(BuildingContext):
    """ todo """

    def __init__(self):
        """ todo """
        super().__init__()  # inherit from all the attributes of the super class
