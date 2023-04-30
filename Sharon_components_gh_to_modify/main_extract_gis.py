"""
Extract the GIS file and convert it into a hb model that can be read and plotted by Grasshopper.
"""
from Sharon_components_gh_to_modify.utils_gh import *


def get_user_parameters():
    global parser
    parser = argparse.ArgumentParser()
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
def updtae_Grasshopper_input_parameter():
    global path_folder_gis_extraction, run_by_the_tool, path_additional_gis_attribute_key_dict, \
        path_gis, move_buildings_to_origin, unit
    args = parser.parse_args()
    path_gis = args.gis
    unit = args.unit
    path_folder_gis_extraction = args.folder
    path_additional_gis_attribute_key_dict = args.dic
    move_buildings_to_origin = bool(args.mov)
    run_by_the_tool = bool(args.tool)
def create_folder():
    os.makedirs(path_folder_gis_extraction, exist_ok=True)
def configurate_and_make_logfile():
    path_logger = os.path.join(path_folder_gis_extraction, "log_report.log")
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s",
                        handlers=[logging.FileHandler(path_logger), logging.StreamHandler(sys.stdout)])
      # logging.getLogger('name of the package').setLevel(logging.CRITICAL) todo for later
def add_path_scripts_in_the_tool():
    if run_by_the_tool:
        sys.path.append(os.path.join(path_tool, "Scripts"))
def create_or_load_urban_canopy_object():
    path_urban_canopy_pkl = os.path.join(path_folder_gis_extraction, "urban_canopy.pkl")
    if os.path.isfile(path_urban_canopy_pkl):
        urban_canopy = UrbanCanopy.make_urban_canopy_from_pkl(path_urban_canopy_pkl)
        logging.info("An urban canopy already exist in the simulation folder, the input GIS will be added to it")
    else:
        urban_canopy = UrbanCanopy()
        logging.info("New urban canopy object was created")
def get_building_id_key_gis():
    '''
      Get the building_id_key_gis if it is given in the additional_gis_attribute_key_dict
    '''
    global building_id_key_gis, additional_gis_attribute_key_dict
    building_id_key_gis = "idbinyan"  # default value, todo: take it as an argument as well
    additional_gis_attribute_key_dict = None
    # check if given in the additional_gis_attribute_key_dict
    if default_additional_gis_attribute_key_dict and os.path.isfile(path_additional_gis_attribute_key_dict):
        with open(path_additional_gis_attribute_key_dict, "r") as f:
            additional_gis_attribute_key_dict = json.load(f)
            if "building_id_key_gis" in additional_gis_attribute_key_dict:
                building_id_key_gis = additional_gis_attribute_key_dict["building_id_key_gis"]
def add_2D_GIS_to_urban_canopy():
    UrbanCanopy.add_buildings_from_2D_GIS_to_dict(path_gis, building_id_key_gis, unit, additional_gis_attribute_key_dict)
    logging.info("Builing geometries extracted from the GIS file successfully")
def move_buildings_to_origin():
    if move_buildings_to_origin or UrbanCanopy.moving_vector_to_origin is not None:
        UrbanCanopy.move_buildings_to_origin()
        logging.info("Buildings have been moved to origin successfully")
def generate_hb_model_contains_all_building_envelopes_to_plot_Grasshopper():
    UrbanCanopy.make_HB_model_envelops_from_buildings(path_folder=path_folder_gis_extraction)
    logging.info("HB model for the building envelop created successfully")
def save_urban_canopy_object_to_pickle():
    UrbanCanopy.export_urban_canopy_to_pkl(path_folder=path_folder_gis_extraction)
    logging.info("Urban canopy object saved successfully")

def main():
    get_user_parameters()
    updtae_Grasshopper_input_parameter()
    create_folder()
    configurate_and_make_logfile()
    add_path_scripts_in_the_tool()
    create_or_load_urban_canopy_object()
    get_building_id_key_gis()
    add_2D_GIS_to_urban_canopy()
    move_buildings_to_origin()
    generate_hb_model_contains_all_building_envelopes_to_plot_Grasshopper()
    save_urban_canopy_object_to_pickle()

if __name__ == "__main__":
    main()
