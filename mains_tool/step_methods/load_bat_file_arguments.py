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

        # Geometry parameters
        parser.add_argument("-g", "--gis", help="path to gis file", nargs='?', default=default_path_gis)
        parser.add_argument("-u", "--unit", help="unit of the GIS", nargs='?', default=default_unit_gis)
        parser.add_argument("-d", "--dic", help="path to the additional key dictionary", nargs='?',
                            default=default_additional_gis_attribute_key_dict)
        # Building manipulation parameters

        # Solar radiation parameters

        # Parse the parser with the added arguments
        args = parser.parse_args()
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
    def load_user_simulation_steps(parser):
        """
        Get the simulation steps to run from the command line
        :param parser:
        :return:
        """
        # General steps
        parser.add_argument("-s1", "--load_or", help="Boolean telling if step 1 should be executed or not", nargs='?',
                            default=False)
        parser.add_argument("-s2", "--step2", help="Boolean telling if step 2 should be executed or not", nargs='?',
                            default=False)
        # geometry extraction steps

        # Building manipulation steps

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

        #the rest todo

        return args


