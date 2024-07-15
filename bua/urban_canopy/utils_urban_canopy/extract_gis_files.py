"""
Extraction of GIS files
"""
import geopandas as gpd


def extract_gis(path_gis):
    """ Extract gis file and return the python shapefile object"""
    shape_file = gpd.read_file(path_gis)
    return shape_file
