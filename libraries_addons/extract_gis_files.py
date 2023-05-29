"""

"""

from libraries_addons.utils_libraries_addons import *

def extract_gis(path_gis):
    """ Extract gis file and return the python shapefile object"""
    shape_file = gpd.read_file(path_gis)
    return shape_file