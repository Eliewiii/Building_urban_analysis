"""
    Have common methods of building  to the urban canopy from hbjson files.
"""

from Sharon_components_gh_to_modify.utils_gh import *

class CommonMethods:
    global path_folder_simulation, path_additional_gis_attribute_key_dict, \
            path_gis, move_buildings_to_origin, unit, make_hb_model_envelops, path_folder_hbjson, parser
    def get_user_parameters(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("-f", "--folder", help="path to the simulation folder", nargs='?',
                            default = default_path_folder_simulation)
        parser.add_argument("-e", "--hbenv",
                            help="Boolean telling if a HB Model containing the envelop of all buildings should be generated",
                            nargs='?',
                            default=default_make_hb_model_envelops)
        parser.add_argument("-t", "--tool",
                            help="Boolean telling if the code is run from an editor or externally by the batch file",
                            nargs='?',
                            )
        parser.add_argument("-g", "--gis", help="path to gis file", nargs='?', default=default_path_gis)
        parser.add_argument("-u", "--unit", help="unit of the GIS", nargs='?', default=default_unit)
        parser.add_argument("-d", "--dic", help="path to the additional key dictionary", nargs='?',
                            default=default_additional_gis_attribute_key_dict)
        parser.add_argument("-m", "--mov", help="Boolean telling if building should be moved to the origin", nargs='?',
                            default=default_move_buildings_to_origin)



    def create_folder(self):
        os.makedirs(path_folder_simulation, exist_ok=True)
    def configurate_and_make_logfile(self):
        path_logger = os.path.join(path_folder_simulation, "log_report.log")
        logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s",
                            handlers=[logging.FileHandler(path_logger), logging.StreamHandler(sys.stdout)])
    def create_or_load_urban_canopy_object(self):
        path_urban_canopy_pkl = os.path.join(path_folder_simulation, "urban_canopy.pkl")
        if os.path.isfile(path_urban_canopy_pkl):
            urban_canopy = UrbanCanopy.make_urban_canopy_from_pkl(path_urban_canopy_pkl)
            logging.info("An urban canopy already exist in the simulation folder, the input GIS will be added to it")
        else:
            urban_canopy = UrbanCanopy()
            logging.info("New urban canopy object was created")

    def save_urban_canopy_object_to_pickle(self):
        UrbanCanopy.export_urban_canopy_to_pkl(path_folder=path_folder_simulation)
        logging.info("Urban canopy object saved successfully")
