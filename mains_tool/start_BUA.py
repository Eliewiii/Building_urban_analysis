from mains_tool.utils_general import *

def main():

    # Create the logs
    currentDirectory = os.getcwd()
    Logspath = "/logs"
    isExist = os.path.exists(currentDirectory + Logspath)
    if not isExist:
       os.makedirs(currentDirectory + Logspath)

    LOG_FILENAME = datetime.now().strftime(currentDirectory + Logspath + '/logfile_%H_%M_%S_%d_%m_%Y.log')
    logging.basicConfig(filename=LOG_FILENAME, level=logging.INFO)

    # Get the user parameters from the command line
    parser = argparse.ArgumentParser()



if __name__ == "__main__":
     main()
    # parser = argparse.ArgumentParser()  # create a parser object todo: move to main script and have parser (changed to parsed_args)
    # parser.add_argument("-gis", "--gis", help="extract a GIS file", nargs='?',
    #                     default=False)
    # parser.add_argument("-addbuilding", "--addbuilding", help="add building to urban canopy", nargs='?',
    #                     default=False)
    # args = parser.parse_args()
    #
    # do_gis_extraction = args.gis
    # add_building_to_urban_canopy = args.addbuilding
    #
    # from Sharon_components_gh_to_modify.main_common_methods import create_or_load_urban_canopy_object
    # from Sharon_components_gh_to_modify.main_add_hbjson_buildings import add_buildings_in_hbjson_to_urban_canopy
    # from Sharon_components_gh_to_modify.main_extract_gis import add_2D_GIS_to_urban_canopy
    #
    # urban_canopy=create_or_load_urban_canopy_object()
    #
    #
    # if do_gis_extraction==True:
    #     urban_canopy = add_2D_GIS_to_urban_canopy()
    #
    # if add_building_to_urban_canopy==True:
    #     urban_canopy = add_buildings_in_hbjson_to_urban_canopy()
