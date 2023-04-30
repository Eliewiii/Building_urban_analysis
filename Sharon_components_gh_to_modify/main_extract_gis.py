"""
Extract the GIS file and convert it into a hb model that can be read and plotted by Grasshopper.
"""
from Sharon_components_gh_to_modify.utils_gh import *
from Sharon_components_gh_to_modify.main_common_methods import *


def updtae_Grasshopper_input_parameter():
    global path_folder_simulation, path_additional_gis_attribute_key_dict, \
        path_gis, move_buildings_to_origin, unit
    args = parser.parse_args()
    path_gis = args.gis
    unit = args.unit
    path_folder_simulation = args.folder
    path_additional_gis_attribute_key_dict = args.dic
    move_buildings_to_origin = bool(args.mov)



      # logging.getLogger('name of the package').setLevel(logging.CRITICAL) todo for later


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
    UrbanCanopy.make_HB_model_envelops_from_buildings(path_folder=path_folder_simulation)
    logging.info("HB model for the building envelop created successfully")


def main():
    CommonMethods.get_user_parameters()
    CommonMethods.updtae_Grasshopper_input_parameter()
    CommonMethods.create_folder()
    CommonMethods.configurate_and_make_logfile()
    CommonMethods.create_or_load_urban_canopy_object()
    get_building_id_key_gis()
    add_2D_GIS_to_urban_canopy()
    move_buildings_to_origin()
    generate_hb_model_contains_all_building_envelopes_to_plot_Grasshopper()
    CommonMethods.save_urban_canopy_object_to_pickle()

if __name__ == "__main__":
    main()
