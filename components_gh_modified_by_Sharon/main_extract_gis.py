"""
Extract the GIS file and convert it into a hb model that can be read and plotted by Grasshopper.
"""

from building.utils import *
# Import libraries from the tool (after as we don't know it's run from the tool or PyCharm)
from urban_canopy.urban_canopy_methods import UrbanCanopy

# Get Appdata\local folder
local_appdata = os.environ['LOCALAPPDATA']
path_tool = os.path.join(local_appdata, "Building_urban_analysis")

# Default values
default_path_gis = os.path.join(path_tool, "Libraries", "GIS", "gis_typo_id_extra_small")
default_folder_gis_extraction = os.path.join(path_tool, "Simulation_temp")
default_unit = "m"
default_additional_gis_attribute_key_dict = None
default_move_buildings_to_origin = False
default_run_by_the_tool = False
additional_gis_attribute_key_dict = None
# Get the building_id_key_gis
building_id_key_gis = "idbinyan"  # default value, todo: take it as an argument as well

def main():
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



    # Input parameter that will be given by Grasshopper
    args = parser.parse_args()
    path_gis = args.gis
    unit = args.unit
    path_folder_gis_extraction = args.folder
    path_additional_gis_attribute_key_dict = args.dic
    move_buildings_to_origin = bool(args.mov)
    run_by_the_tool = bool(args.tool)

    os.makedirs(path_folder_gis_extraction, exist_ok=True)
    path_log_file = os.path.join(path_folder_gis_extraction, "log_report.log")

    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s",
                        handlers=[logging.FileHandler(path_log_file), logging.StreamHandler(sys.stdout)])

    # logging.getLogger('name of the package').setLevel(logging.CRITICAL) todo for later

    # Add the path of scripts in the tool to sys so that the lib can be used
    if run_by_the_tool:
        sys.path.append(os.path.join(path_tool, "Scripts"))
        # # Import libraries from the tool

    def Create_load_urban_canopy_object():
        path_urban_canopy_pkl = os.path.join(path_folder_gis_extraction, "urban_canopy.pkl")
        if os.path.isfile(path_urban_canopy_pkl):
            urban_canopy = UrbanCanopy.make_urban_canopy_from_pkl(path_urban_canopy_pkl)
            logging.info("An urban canopy already exist in the simulation folder, the input GIS will be added to it")
        else:
            urban_canopy = UrbanCanopy()
            logging.info("New urban canopy object was created")
    Create_load_urban_canopy_object()

    def additional_gis_attribute_key_dict_exists():
        if default_additional_gis_attribute_key_dict and os.path.isfile(path_additional_gis_attribute_key_dict):
            with open(path_additional_gis_attribute_key_dict, "r") as f:
                additional_gis_attribute_key_dict = json.load(f)
                if "building_id_key_gis" in additional_gis_attribute_key_dict:
                    building_id_key_gis = additional_gis_attribute_key_dict["building_id_key_gis"]
    additional_gis_attribute_key_dict_exists()

    def Add_2DGIS_to_urban_canopy():
        urban_canopy.add_buildings_from_2D_GIS_to_dict(path_gis, building_id_key_gis, unit, additional_gis_attribute_key_dict)
        logging.info("Builing geometries extracted from the GIS file successfully")
    Add_2DGIS_to_urban_canopy()

    def move_buildings_to_origin_if_asked():
        if move_buildings_to_origin or urban_canopy.moving_vector_to_origin is not None:
            urban_canopy.move_buildings_to_origin()
            logging.info("Buildings have been moved to origin successfully")
    move_buildings_to_origin_if_asked()

    def generate_hb_model_contains_all_building_to_Grasshopper():
        urban_canopy.make_HB_model_envelops_from_buildings(path_folder=path_folder_gis_extraction)
        logging.info("HB model for the building envelop created successfully")
    generate_hb_model_contains_all_building_to_Grasshopper()

    def save_urban_canopy_object_pickle():
        urban_canopy.export_urban_canopy_to_pkl(path_folder=path_folder_gis_extraction)
        logging.info("Urban canopy object saved successfully")
    save_urban_canopy_object_pickle()

if __name__ == "__main__":
    main()