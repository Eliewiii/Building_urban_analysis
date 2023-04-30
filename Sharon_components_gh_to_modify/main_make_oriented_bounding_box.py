"""
Extract add buildings to the urban canopy from hbjson files.
"""
from Sharon_components_gh_to_modify.utils_gh import *
from Sharon_components_gh_to_modify.main_common_methods import *
    
def updtae_Grasshopper_input_parameter():
    global path_folder_simulation
    args = parser.parse_args()
    path_folder_simulation = args.folder
def add_buildings_in_hbjson_to_urban_canopy():
    UrbanCanopy.make_oriented_bounding_boxes_of_buildings(path_folder=path_folder_simulation,
                                                           hbjson_name=name_bounding_box_hbjson)
    logging.info("The bounding boxes of the buildings were created successfully")


def main():
    CommonMethods.get_user_parameters()
    CommonMethods.updtae_Grasshopper_input_parameter()
    CommonMethods.create_folder()
    CommonMethods.configurate_and_make_logfile()
    CommonMethods.create_or_load_urban_canopy_object()
    add_buildings_in_hbjson_to_urban_canopy()
    CommonMethods.save_urban_canopy_object_to_pickle()

if __name__ == "__main__":
    main()
