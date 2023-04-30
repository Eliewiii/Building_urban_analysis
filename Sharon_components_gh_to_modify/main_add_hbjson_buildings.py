"""
Extract add buildings to the urban canopy from hbjson files.
"""
from Sharon_components_gh_to_modify.utils_gh import *
from Sharon_components_gh_to_modify.main_common_methods import *

def updtae_Grasshopper_input_parameter():
    global path_folder_simulation, make_hb_model_envelops, path_folder_hbjson
    args = parser.parse_args()
    path_folder_simulation = args.folder
    path_folder_hbjson = os.path.join(path_folder_simulation, name_hbjson_directory)
    make_hb_model_envelops = bool(args.hbenv)
def add_buildings_in_hbjson_to_urban_canopy():
    UrbanCanopy.add_buildings_from_hbjson_to_dict(path_directory_hbjson=path_folder_hbjson)
    logging.info("Building(s) from hbjson added to the urban canopy successfully")
def generate_hb_model_contains_building_envelopes_to_plot_Grasshopper():
    if make_hb_model_envelops:
        UrbanCanopy.make_HB_model_envelops_from_buildings(path_folder=path_folder_simulation)
        logging.info("HB model for the building envelop created successfully")


def main():
    CommonMethods.get_user_parameters()
    CommonMethods.updtae_Grasshopper_input_parameter()
    CommonMethods.create_folder()
    CommonMethods.configurate_and_make_logfile()
    CommonMethods.create_or_load_urban_canopy_object()
    add_buildings_in_hbjson_to_urban_canopy()
    generate_hb_model_contains_building_envelopes_to_plot_Grasshopper()
    CommonMethods.save_urban_canopy_object_to_pickle()

if __name__ == "__main__":
    main()

