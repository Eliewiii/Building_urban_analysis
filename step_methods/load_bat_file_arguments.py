"""

"""

from mains_tool.utils_general import *


class LoadArguments:
    """ """

    @staticmethod
    def add_user_parameters_to_parser(parser):
        """
        Get the user parameters from the command line
        :param parser: parser object containing the user parameters
        :return parser: parser object with the argument added
        """
        # General user parameters
        parser.add_argument("-f", "--path_simulation_folder", help="path to the simulation folder", nargs='?',
                            default=default_path_folder_simulation)

        # Grasshopper parameters
        parser.add_argument("-c", "--gh_component_name", help="name of the component in gh that execute the code",
                            nargs='?',
                            default=None)

        # Geometry parameters
        parser.add_argument("-g", "--path_gis_folder", help="path to gis folder containing all the sub gis files",
                            nargs='?', default=default_path_gis)
        parser.add_argument("-u", "--gis_unit", help="unit of the GIS", nargs='?', default=default_unit_gis)
        parser.add_argument("-d", "--path_dic_additional_gis_attribute_keys",
                            help="path to the additional key dictionary of the attributes in the GIS file", nargs='?',
                            default=None)
        parser.add_argument("--path_folder",
                            help="path to a folder that will be useful for the simulation", nargs='?', default=None)
        parser.add_argument("--path_file",
                            help="path to a single file taht will be useful for the simuation", nargs='?', default=None)

        # Building manipulation parameters
        parser.add_argument("-l", "--building_id_list", help="path to the additional key dictionary", nargs='?',
                            default=None)
        parser.add_argument("-t", "--are_buildings_target",
                            help="boolean (here '0' or '1') telling if the buildings inputed in the component are "
                                 "target ", nargs='?', default=False)  # as no list can be sent through command line,
        # it will be a string,
        # with each id seperate by a space that will be parsed in the main script
        parser.add_argument("-w", "--path_weather_file", help="path to the weather file used",
                            default=default_path_weather_file)
        # Solar radiation parameters
        parser.add_argument("--list_id", help="list of the names of the buildings in the urban canopy we want to run "
                                              "the simulation on", default=default_list_id)
        parser.add_argument("--grid_size", help="size of the grid of the mesh for the buildings, it should be about "
                                                "the size of a panel + BOS", default=default_grid_size)
        parser.add_argument("--offset_dist", help="Number for the distance to move points from the surfaces of the "
                                                  "geometry of the model", default=default_offset_dist)
        parser.add_argument("--on_roof", help="True if the simulation is to be run on the roof, else False",
                            default=default_on_roof)
        parser.add_argument("--on_facades", help="True if the simulation is to be run on the facades, else False",
                            default=default_on_facades)
        # Panel simulation parameters
        parser.add_argument("--path_pv_tech_dictionary", help="path to the json containing the PVPanelTechnologies",
                            default=default_path_pv_tech_dictionary)
        parser.add_argument("--id_pv_tech_roof", help="name of the pv tech used on the roof",
                            default=default_id_pv_tech_roof)
        parser.add_argument("--id_pv_tech_facades", help="name of the pv tech used on the facades",
                            default=default_id_pv_tech_facades)
        parser.add_argument("--study_duration_years", help="duration of the study in years",
                            default=default_study_duration_years)
        parser.add_argument("--replacement_scenario", help="replacement scenario chosen for the failed panels",
                            default=default_replacement_scenario)
        parser.add_argument("--every_x_years", help="replacement every x years scenario", default=default_evey_X_years)

    @staticmethod
    def add_user_simulation_features_to_parser(parser):
        """
        Get the simulation steps to run from the command line
        :param parser:
        :return:
        """
        # General features
        parser.add_argument("--make_simulation_folder", help="create the simulation folder if it doesn't exist",
                            nargs='?',
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
        parser.add_argument("--extract_buildings_from_hbjson_models",
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
                            help="Make a HB model containing the envelop of all the buildings in the urban canopy "
                                 "object that will be stored in the json dic of the urban canopy object",
                            nargs='?', default=False)

        # Run the simulations
        parser.add_argument("--do_radiation_simulation", help="On each building targeted in the urban canopy, "
                                                              "run the solar simulation", default=False)
        parser.add_argument("--do_panel_simulation", help="On each building targeted in the urban canopy, run the "
                                                          "panel simulation", default=False)
        # Post-processing
        parser.add_argument("--generate_panels_results_in_csv", help="Generate the csv file containing all the useful "
                                                                     "data calculated by the simulation", default=False)

    @staticmethod
    def parse_arguments_and_add_them_to_variable_dict(parser):
        """
        Parse the arguments
        :param parser:
        :return:
        """
        # Parse the parser with the added arguments
        args = parser.parse_args()

        # post process of some arguments
        buildings_id_list = parse_and_clean_building_id_list_from_argument_parser(args.building_id_list)
        are_buildings_target = bool(int(args.are_buildings_target))  # to convert the string ("0" or "1") to a boolean

        # Create a dictionary with the arguments and the name of their variable that will be imported in the main script
        # todo @Elie, complete the dictionary with the new arguments through the development
        arguments_dictionary = {
            "path_folder_simulation": args.path_simulation_folder,
            "path_gis": args.path_gis_folder,
            "unit_gis": args.gis_unit,
            "path_additional_gis_attribute_key_dict": args.path_dic_additional_gis_attribute_keys,
            "gh_component_name": args.gh_component_name,
            "path_folder": args.path_folder,
            "path_file": args.path_file,
            "building_id_list": args.building_id_list,
            "are_buildings_target": bool(int(args.are_buildings_target)),
            "path_weather_file": args.path_weather_file,
            "list_id": args.list_id,
            "grid_size": args.grid_size,
            "offset_dist": args.offset_dist,
            "on_roof": args.on_roof,
            "on_facades": args.on_facades,
            "path_pv_tech_dictionary": args.path_pv_tech_dictionary,
            "id_pv_tech_roof": args.id_pv_tech_roof,
            "id_pv_tech_facades": args.id_pv_tech_facades,
            "study_duration_years": args.study_duration_years,
            "replacement_scenario": args.replacement_scenario,
            "every_X_years": args.every_x_years
        }

        # Create a dictionary with the arguments and the name of their variable that will be imported in the main script
        # # todo @Elie, complete the dictionary with the new arguments through the development
        step_dictionary = {
            "run_make_simulation_folder": bool(int(args.make_simulation_folder)),
            "run_create_or_load_urban_canopy_object": bool(int(args.create_or_load_urban_canopy_object)),
            "run_save_urban_canopy_object_to_pickle": bool(int(args.save_urban_canopy_object_to_pickle)),
            "run_save_urban_canopy_object_to_json": bool(int(args.save_urban_canopy_object_to_json)),
            "run_extract_gis": bool(int(args.extract_gis)),
            "run_extract_buildings_from_hbjson_models": bool(int(args.extract_buildings_from_hbjson_models)),
            "run_move_buildings_to_origin": bool(int(args.move_buildings_to_origin)),
            "run_remove_building_list_from_urban_canopy": bool(int(args.remove_building_list_from_urban_canopy)),
            "run_generate_bounding_boxes": bool(int(args.generate_bounding_boxes)),
            "run_perform_context_filtering": bool(int(args.perform_context_filtering)),
            "run_generate_model_with_building_envelop": bool(int(args.generate_model_with_building_envelop)),
            "run_radiation_simulation": bool(int(args.do_radiation_simulation)),
            "run_panel_simulation": bool(int(args.do_panel_simulation)),
            "generate_panels_results_in_csv": bool(int(args.generate_panels_results_in_csv))
        }

        # the rest todo

        return arguments_dictionary, step_dictionary


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
