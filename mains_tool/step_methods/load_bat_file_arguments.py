"""

"""

from mains_tool.utils_general import *


class LoadArguments:
    """ """

    @staticmethod
    def load_user_parameters(parser):
        """
        Get the user parameters from the command line
        :param parser: parser object containing the user parameters
        :return parser: parser object with the argument added
        """
        # General user parameters
        parser.add_argument("-f", "--folder", help="path to the simulation folder", nargs='?',
                            default=default_path_folder_simulation)

        # Grasshopper parameters
        parser.add_argument("-c", "--gh_component_name", help="name of the component in gh that execute the code",
                            nargs='?',
                            default=None)

        # Geometry parameters
        parser.add_argument("-g", "--path_gis_folder", help="path to gis folder containing all the sub gis files",
                            nargs='?', default=default_path_gis)
        parser.add_argument("-u", "--unit", help="unit of the GIS", nargs='?', default=default_unit_gis)
        parser.add_argument("-d", "--path_dic_additional_gis_attribute_keys",
                            help="path to the additional key dictionary of the attributes in the GIS file", nargs='?',
                            default=None)
        parser.add_argument("--path_folder_hbjson",
                            help="path to a folder containing several hbjson files", nargs='?',
                            default=None)
        parser.add_argument("--path_file_hbjson",
                            help="path to a single hbjson file", nargs='?',
                            default=None)

        # Building manipulation parameters
        parser.add_argument("-l", "--building_id_list", help="path to the additional key dictionary", nargs='?',
                            default=None)
        parser.add_argument("-t", "--are_buildings_target",
                            help="boolean (here '0' or '1') telling if the buildings inputed in the component are target ",
                            nargs='?',
                            default=None)  # as no list can be sent through command line, it will be a string, with each id seperate by a space that will be parsed in the main script

        # Solar radiation parameters

        # Parse the parser with the added arguments
        args = parser.parse_args()

        # post process of some arguments
        buildings_id_list = parse_and_clean_building_id_list_from_argument_parser(args.building_id_list)
        are_buildings_target = bool(int(args.are_buildings_target))  # to convert the string ("0" or "1") to a boolean

        # Create a dictionary with the arguments and the name of their variable that will be imported in the main script
        # todo @Elie, complete the dictionary with the new arguments through the development
        arguments_dictionary = {
            "path_folder_simulation_para": args.folder,
            "path_gis_para": args.gis,
            "unit_gis_para": args.unit,
            "path_additional_gis_attribute_key_dict_para": args.dic
        }

        return arguments_dictionary

    @staticmethod
    def load_user_simulation_features(parser):
        """
        Get the simulation steps to run from the command line
        :param parser:
        :return:
        """
        # General features
        parser.add_argument("--make_sim_folder", help="create the simulation folder if it doesn't exist", nargs='?',
                            default=False)
        parser.add_argument("--create_or_load_urban_canopy_object", help="Load or create urban canopy objects",
                            nargs='?', default=False)
        parser.add_argument("--save_urban_canopy_object_to_pickle", help="Save the urban canopy object to pickle file",
                            nargs='?', default=False)
        parser.add_argument("--save_urban_canopy_object_to_json",
                            help="Save some of the attributes of the urban canopy object to pickle file", nargs='?',
                            default=False)

        # geometry extraction features
        parser.add_argument("--extract_gis", help="Extract GIS file and add it to the urban canopy object",
                            nargs='?', default=False)
        parser.add_argument("--extract_buildings_from_models_hbjson",
                            help="Extract buildings from hbjson files and add them to the urban canopy object",
                            nargs='?', default=False)

        # Building manipulation features
        parser.add_argument("--move_buildings_to_origin", help="Move all the buildings to the origin of the plan",
                            nargs='?', default=False)
        parser.add_argument("--remove_building_list_from_urban_canopy",
                            help="Remove a list of building from the urban canopy object", nargs='?', default=False)

        # Context filtering features
        parser.add_argument("--generate_bounding_boxes", help="Generate bounding boxes for the buildings",
                            nargs='?', default=False)
        parser.add_argument("--perform_context_filtering", help="Perform context filtering for buildings",
                            nargs='?', default=False)

        # Generate objects for visualization
        parser.add_argument("--generate_model_with_building_envelop",
                            help="Make a HB model containing the envelop of all the buildings in the urban canopy object that will be stored in the json dic of the urban canopy object",
                            nargs='?', default=False)

        # Parse the parser with the added arguments
        args = parser.parse_args()
        # Create a dictionary with the arguments and the name of their variable that will be imported in the main script
        # # todo @Elie, complete the dictionary with the new arguments through the development
        # arguments_dictionary = {
        #     "path_folder_simulation_para": args.folder,
        #     "path_gis_para": args.gis,
        #     "unit_gis_para": args.unit,
        #     "path_additional_gis_attribute_key_dict_para": args.dic
        #                         }
        #
        # return arguments_dictionary

    @staticmethod
    def parse_arguments_and_add_them_to_variable_dict(parser):
        """
        Parse the arguments
        :param parser:
        :return:
        """

        args = parser.parse_args()
        path_folder_simulation_para = args.folder

        # the rest todo

        return args


# todo @Elie, this function is only used here, should it be moved somewhere else?
def parse_and_clean_building_id_list_from_argument_parser(building_id_list_form_argument_parser):
    """
    Parse the building id list from the argument parser
    :param building_id_list_form_argument_parser: str : list of building id seperated by spaces
    :return:
    """
    # return None if None
    if building_id_list_form_argument_parser is None:
        return None
    else:
        # return a list of id, ignore the empty string if there is any
        return [id for id in building_id_list_form_argument_parser.split(" ") if id != '']
