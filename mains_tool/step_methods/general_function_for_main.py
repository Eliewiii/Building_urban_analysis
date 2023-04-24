"""

"""

def load_user_parameter_options():
    """

    :return:
    """
    parser.add_argument("-g", "--gis", help="path to gis file", nargs='?', default=default_path_gis)
    parser.add_argument("-f", "--folder", help="path to the simulation folder", nargs='?',
                        default=default_folder_gis_extraction)
    parser.add_argument("-u", "--unit", help="unit of the GIS", nargs='?', default=default_unit)
    parser.add_argument("-d", "--dic", help="path to the additional key dictionary", nargs='?',
                        default=default_additional_gis_attribute_key_dict)
    parser.add_argument("-m", "--mov", help="Boolean telling if building should be moved to the origin", nargs='?',
                        default=default_move_buildings_to_origin)
    parser.add_argument("-f", "--folder", help="path to the simulation folder", nargs='?',
                        default=default_path_folder_simulation)
    parser.add_argument("-e", "--hbenv",
                        help="Boolean telling if a HB Model containing the envelop of all buildings should be generated",
                        nargs='?',
                        default=default_make_hb_model_envelops)



def load_or_create_UrbanCanopy_object():
    """

    :return:
    """
    path_urban_canopy_pkl = os.path.join(path_folder_gis_extraction, "urban_canopy.pkl")
    if os.path.isfile(path_urban_canopy_pkl):
        urban_canopy = urban_canopy_methods.make_urban_canopy_from_pkl(path_urban_canopy_pkl)
        logging.info("An urban canopy already exist in the simulation folder, the input GIS will be added to it")
    else:
        # urban_canopy = UrbanCanopy()
        # we can create a new object only in a new function and we currentky in main method
        # TODO
        logging.info("New urban canopy object was created")