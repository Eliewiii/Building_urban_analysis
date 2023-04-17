from building.utils import *

path_gis = "D:\Elie\PhD\Simulation\Input_Data\GIS\gis_typo_id_extra_small"

def extract_gis(path_gis):
    """ Extract gis file and return the python shapefile object"""
    shape_file = gpd.read_file(path_gis)
    return shape_file

def main():
    shapefile = extract_gis(path_gis)
    print(shapefile["geometry"])
    for nb,id in enumerate(shapefile["oidmivne"]):
        print(nb,id)

if __name__=="__main__":
    main()