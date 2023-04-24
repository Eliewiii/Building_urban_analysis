"""
Extract add buildings to the urban canopy from hbjson files.
"""
from Sharon_components_gh_to_modify.utils_gh import *


if __name__ == "__main__":
    def get_user_parmeters():
        global parser
        parser = argparse.ArgumentParser()
        parser.add_argument("-f", "--folder", help="path to the simulation folder", nargs='?',
                            default=default_path_folder_simulation)
        parser.add_argument("-t", "--tool",
                            help="Boolean telling if the code is run from an editor or externally by the batch file",
                            nargs='?',
                            default=default_run_by_the_tool)
    def updtae_Grasshopper_input_parameter():
        global path_folder_simulation, run_by_the_tool
        args = parser.parse_args()
        path_folder_simulation = args.folder
        run_by_the_tool = bool(args.tool)
    def create_folder():
        os.makedirs(path_folder_simulation, exist_ok=True)
    def configurate_and_make_logfile():
        path_logger = os.path.join(path_folder_simulation, "log_report.log")
        logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s",
                            handlers=[logging.FileHandler(path_logger), logging.StreamHandler(sys.stdout)])
    def add_path_scripts_in_the_tool():
        if run_by_the_tool:
            sys.path.append(os.path.join(path_tool, "Scripts"))
    def create_or_load_urban_canopy_object():
        path_urban_canopy_pkl = os.path.join(path_folder_simulation, "urban_canopy.pkl")
        if os.path.isfile(path_urban_canopy_pkl):
            urban_canopy = UrbanCanopy.make_urban_canopy_from_pkl(path_urban_canopy_pkl)
            logging.info("An urban canopy already exist in the simulation folder, the input GIS will be added to it")
        else:
            urban_canopy = UrbanCanopy()
            logging.info("New urban canopy object was created")
    def add_buildings_in_hbjson_files_to_urban_canopy():
        UrbanCanopy.make_oriented_bounding_boxes_of_buildings(path_folder=path_folder_simulation,
                                                               hbjson_name=name_bounding_box_hbjson)
        logging.info("The bounding boxes of the buildings were created successfully")
    def save_urban_canopy_object_to_pickle():
        UrbanCanopy.export_urban_canopy_to_pkl(path_folder=path_folder_simulation)
        logging.info("Urban canopy object saved successfully")

    get_user_parmeters()
    updtae_Grasshopper_input_parameter()
    create_folder()
    configurate_and_make_logfile()
    add_path_scripts_in_the_tool()
    create_or_load_urban_canopy_object()
    add_buildings_in_hbjson_files_to_urban_canopy()
    save_urban_canopy_object_to_pickle()