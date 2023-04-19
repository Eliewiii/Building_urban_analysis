"""
Extract the GIS file and convert it into a hb model that can be read and plotted by Grasshopper.
"""
from mains_tool.utils_general import *

if __name__ == "__main__":
    def create_user_parameter_options():
        parser.add_argument("-g", "--gis", help="path to gis file", nargs='?', default=default_path_gis)
        parser.add_argument("-f", "--folder", help="path to the simulation folder", nargs='?',
                            default=default_folder_gis_extraction)
        parser.add_argument("-u", "--unit", help="unit of the GIS", nargs='?', default=default_unit)
        parser.add_argument("-d", "--dic", help="path to the additional key dictionary", nargs='?',
                            default=default_additional_gis_attribute_key_dict)
        parser.add_argument("-m", "--mov", help="Boolean telling if building should be moved to the origin", nargs='?',
                            default=default_move_buildings_to_origin)
        parser.add_argument("-t", "--tool",
                            help="Boolean telling if the code is run from an editor or externally by the batch file",
                            nargs='?',
                            default=default_run_by_the_tool)
    def Input_parameters_input_to_Grasshopper():
        #unit = args.unit
        path_folder_gis_extraction = args.folder
        path_additional_gis_attribute_key_dict = args.dic
        move_buildings_to_origin = bool(args.mov)
        run_by_the_tool = bool(args.tool)
        return run_by_the_tool
    def create_folder_if_not_exist():
        path_folder_gis_extraction = Input_parameters_input_to_Grasshopper(args)
        os.makedirs(path_folder_gis_extraction, exist_ok=True)
        return path_folder_gis_extraction
    def import_libraries_from_BUA():
        if run_by_the_tool:
            sys.path.append(os.path.join(path_tool, "Scripts"))
    def Create_load_urban_canopy_object():
        path_urban_canopy_pkl = os.path.join(path_folder_gis_extraction, "urban_canopy.pkl")
        if os.path.isfile(path_urban_canopy_pkl):
            urban_canopy = urban_canopy_methods.make_urban_canopy_from_pkl(path_urban_canopy_pkl)
            logging.info("An urban canopy already exist in the simulation folder, the input GIS will be added to it")
        else:
            #urban_canopy = UrbanCanopy()
            # we can create a new object only in a new function and we currentky in main method
            #TODO
            logging.info("New urban canopy object was created")
    def if_given_additional_gis_attribute_key_dict():
        if default_additional_gis_attribute_key_dict and os.path.isfile(path_additional_gis_attribute_key_dict):
            with open(path_additional_gis_attribute_key_dict, "r") as f:
                additional_gis_attribute_key_dict = json.load(f)
                if "building_id_key_gis" in additional_gis_attribute_key_dict:
                    building_id_key_gis = additional_gis_attribute_key_dict["building_id_key_gis"]
    def Add_2D_GIS_to_urban_canopy():
        urban_canopy_methods.add_buildings_from_2D_GIS_to_dict(path_gis, building_id_key_gis, unit, additional_gis_attribute_key_dict)
        logging.info("Builing geometries extracted from the GIS file successfully")
    def Move_the_buildings_to_the_origin():
        if move_buildings_to_origin or urban_canopy_methods.moving_vector_to_origin:
            urban_canopy_methods.move_buildings_to_origin()
    def generate_hb_model_contains_all_building_envelopes_to_plot_in_Grasshopper():
        urban_canopy_methods.make_HB_model_envelops_from_buildings(path_folder=path_folder_gis_extraction)
        logging.info("HB model for the building envelop created successfully")
    def save_urban_canopy_to_pickle_file():
        urban_canopy_methods.export_urban_canopy_to_pkl(path_folder=path_folder_gis_extraction)
        logging.info("Urban canopy object saved successfully")
    def create_log_file():
        Logspath = "/logs"
        isExist = os.path.exists(currentDirectory + Logspath)
        if not isExist:
            os.makedirs(currentDirectory + Logspath)

        LOG_FILENAME = datetime.now().strftime(currentDirectory + Logspath + '/logfile_%H_%M_%S_%d_%m_%Y.log')
        logging.basicConfig(filename=LOG_FILENAME, level=logging.INFO)


    create_user_parameter_options()
    run_by_the_tool = Input_parameters_input_to_Grasshopper()
    path_folder_gis_extraction = create_folder_if_not_exist()
    import_libraries_from_BUA()
    Create_load_urban_canopy_object()
    if_given_additional_gis_attribute_key_dict()
    Add_2D_GIS_to_urban_canopy()
    Move_the_buildings_to_the_origin()
    generate_hb_model_contains_all_building_envelopes_to_plot_in_Grasshopper()
    save_urban_canopy_to_pickle_file()

"""
#################Configurate and make the logfile########################
#def make_the_logfile():
    #path_logger = os.path.join(path_folder_gis_extraction, "log_report.log")
    #logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s",
    #                    handlers=[logging.FileHandler(path_logger), logging.StreamHandler(sys.stdout)])
    # logging.getLogger('name of the package').setLevel(logging.CRITICAL) todo for later
######################################################################
"""