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
        parser.add_argument("-f", "--folder", help="path to the simulation folder", nargs='?',
                            default=default_path_folder_simulation)
        parser.add_argument("-e", "--hbenv",
                            help="Boolean telling if a HB Model containing the envelop of all buildings should be generated",
                            nargs='?',default=default_make_hb_model_envelops)
        parser.add_argument("-g", "--gis", help="path to gis file", nargs='?', default=default_path_gis)
        parser.add_argument("-u", "--unit", help="unit of the GIS", nargs='?', default=default_unit_gis)
        parser.add_argument("-d", "--dic", help="path to the additional key dictionary", nargs='?',
                            default=default_additional_gis_attribute_key_dict)


    @staticmethod
    def load_user_simulation_steps(parser):
        """
        Get the simulation steps to run from the command line
        :param parser:
        :return:
        """
        parser.add_argument("-s1", "--step1", help="Boolean telling if step 1 should be executed or not", nargs='?',
                            default=False)
        parser.add_argument("-s2", "--step2", help="Boolean telling if step 2 should be executed or not", nargs='?',
                            default=False)
        # same for the others...
        # the names/tags are of course not final, just for the example, we'll discuss it later


    @staticmethod
    def parse_arguments(parser):
        """
        Parse the arguments
        :param parser:
        :return:
        """
        args = parser.parse_args()
        path_folder_simulation_para = args.folder
        #the rest todo
        return args
