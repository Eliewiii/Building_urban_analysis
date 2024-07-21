"""
Urban canopy class, containing and managing collections of buildings in urban areas.
"""
import os
import pickle
import json
import logging
import shutil

from datetime import datetime

from honeybee.model import Model

from bua.urban_canopy.export_to_json import ExportUrbanCanopyToJson
from bua.urban_canopy.bipv_scenario_urban_canopy import BipvScenario
from bua.urban_canopy.uc_context_filter.shade_manager import ShadeManager
from bua.urban_canopy.ubes.uc_energy_simulation import UrbanBuildingEnergySimulation

from bua.building.building_basic import BuildingBasic
from bua.building.building_modeled import BuildingModeled
from bua.building.context_filter.utils_functions_context_filter import \
    make_pyvista_polydata_from_list_of_hb_model_and_lb_polyface3d
from bua.urban_canopy.utils_urban_canopy.extract_gis_files import extract_gis
from bua.typology.typology import Typology

from bua.bipv.bipv_technology import BipvTechnology
from bua.bipv.bipv_inverter import BipvInverter
from bua.bipv.bipv_transportation import BipvTransportation

from bua.utils.utils_configuration import name_urban_canopy_export_file_pkl, name_urban_canopy_export_file_json, \
    name_radiation_simulation_folder, name_temporary_files_folder, name_ubes_temp_simulation_folder, \
    name_ubes_simulation_result_folder, name_ubes_epw_file, \
    path_folder_default_bipv_parameters, \
    path_folder_user_bipv_parameters
from bua.utils.utils_constants import TOLERANCE_LBT

from bua.utils.utils_default_values_user_parameters import default_path_weather_file

dev_logger = logging.getLogger("dev")
user_logger = logging.getLogger("user")


class UrbanCanopy:

    def __init__(self):
        """Initialize the Urban Canopy"""
        self.building_dict = {}  # dictionary of the buildings in the urban canopy
        self.typology_dict = {}  # dictionary of the typologies loaded the urban canopy
        self.moving_vector_to_origin = None  # moving vector of the urban canopy that moved the urban canopy to the origin
        self.json_dict = {}  # dictionary containing relevant attributes of the urban canopy to be exported to json

        # Context filtering
        self.full_context_pyvista_mesh = None  # pyvista mesh of all the buildings within the urban canopy
        self.shade_manager = ShadeManager()  # Shade manager object

        # UBES
        self.ubes_obj = UrbanBuildingEnergySimulation()  # Urban Building Energy Simulation object

        # BIPV simulation
        self.bipv_scenario_dict = {}  # dictionary of the BIPV scenarios

    def __len__(self):
        """ Return the number of buildings in the urban canopy """
        return len(self.building_dict)

    @classmethod
    def make_urban_canopy_from_pkl(cls, path_pkl):
        """ Load the urban canopy from a pickle file """
        with open(path_pkl, 'rb') as pkl_file:
            # Load pickle file
            urban_canopy_object = pickle.load(pkl_file)
            # Load attributes from pickling
            urban_canopy_object.load_attributes_from_pkl()
            # Load the buildings objects that might have some properties stored into dict (ex HB_models)
            urban_canopy_object.load_building_HB_attributes()
            # Reinitialize the json dictionary
            urban_canopy_object.reinitialize_json_dict()

        return urban_canopy_object

    def to_pkl(self, path_simulation_folder):
        """ Save the urban canopy to a pickle file """
        # Turn certain attribute HB objects into dictionary to enable pickling (see the function)
        self.prepare_attributes_for_pkl()
        self.pickle_building_HB_attributes()

        # Write pkl file
        with open(os.path.join(path_simulation_folder, name_urban_canopy_export_file_pkl), 'wb') as pkl_file:
            pickle.dump(self, pkl_file)

    def to_json(self, path_simulation_folder):
        """ Save the urban canopy to a pickle json """
        # Transform the data from the urban canopy in the json dictionary
        ExportUrbanCanopyToJson.make_urban_canopy_json_dict(urban_canopy_obj=self)
        # Write json file
        with open(os.path.join(path_simulation_folder, name_urban_canopy_export_file_json), 'w') as json_file:
            json.dump(self.json_dict, json_file)

    def reinitialize_json_dict(self):
        """
        Reinitialize the json dict
        Not 100% necessary as te dictionary is written after the urban canopy is pickled, but some of
        """
        self.json_dict = {}

    def prepare_attributes_for_pkl(self):
        """ Prepare the object for pickling """
        self.full_context_pyvista_mesh = None
        self.shade_manager.prepare_for_pkl()

    def load_attributes_from_pkl(self):
        """ Load the object from pickling """
        self.shade_manager.load_from_pkl()

    def load_typologies(self, typology_folder_path):
        """ Load the typologies from the folder
         :param typology_folder_path: path to the folder containing the typologies
         :return: None
         """

        # get the list of all the typology from the typology folder
        typology_folders_list = os.listdir(typology_folder_path)
        # loop through the typology folders list
        for typology in typology_folders_list:
            path_to_typology = os.path.join(typology_folder_path, typology)  # path to the given typology
            typology_obj = Typology.from_json(
                path_to_typology)  # make typology object from the json file in the folder
            # todo: have a tuple as a key, ex: (year, shape_type), and the year might even be an interval,
            # key_tuple = (key, year)
            # where is the keys list or where can I get the value of the key
            # TODO cont.: so maybe have a global variable with values associated to the year,
            # TODO cont.: ex: 1900-1945, 1945-1970, 1970-2000, 2000-2020 : what else?
            # years_range_list = [1900-1945, 1945-1970, 1970-2000, 2000-2020]
            self.typology_dict[
                typology_obj.identifier] = typology_obj  # add the typology to the urban canopy dictionary

    def load_building_HB_attributes(self):
        """ Load the buildings objects that might have some properties stored into dict (ex HB_models) """
        for building_id, building_obj in self.building_dict.items():
            building_obj.load_HB_attributes()

    def pickle_building_HB_attributes(self):
        """ Pickle the buildings objects that might have some properties stored into dict (ex HB_models) """
        # todo: same as above
        for building_id, building_obj in self.building_dict.items():
            building_obj.pickle_HB_attributes()

    def add_building_to_dict(self, building_id, building_obj):
        """ Add a building to the urban canopy"""
        # check if the building id is already in the urban canopy
        if building_id in self.building_dict.keys():
            user_logger.warning("The building id {building_id} is already in the urban canopy, "
                                "it will not be added again to the urban canopy".format(
                building_id=building_id))
            dev_logger.warning("The building id {building_id} is already in the urban canopy, "
                               "it will not be added again to the urban canopy".format(
                building_id=building_id))
            return False
        else:
            # add the building to the urban canopy
            self.building_dict[building_id] = building_obj
            return True

    def add_list_of_buildings_to_dict(self, building_id_list, building_obj_list):
        """ Add a list of buildings to the urban canopy
        :param building_id_list: list of the building ids
        :param building_obj_list: list of the building objects
        :return added_building_id_list: list of the building ids that were added to the urban canopy
        """
        added_building_id_list = []
        for i, building_id in enumerate(building_id_list):
            building_obj = building_obj_list[i]
            is_added = self.add_building_to_dict(building_id, building_obj)
            if is_added:
                added_building_id_list.append(building_id)

        return added_building_id_list

    def remove_building_from_dict(self, building_id):
        """
        Remove a building from the urban canopy
        :param building_id: id of the building to remove
        :return:
        """
        self.building_dict.pop(building_id)

    def add_buildings_from_2D_GIS_to_dict(self, path_gis, building_id_key_gis="idbinyan", unit="m",
                                          path_additional_gis_attribute_key_dict=None):
        """ Extract the data from a shp file and create the associated buildings objects"""
        # Read GIS file
        shape_file = extract_gis(path_gis)
        # Check if the building_id_key_gis is an attribute of the shape file
        try:
            shape_file[building_id_key_gis]
        except KeyError:
            logging.error(
                f"The key {building_id_key_gis} is not an attribute of the shape file, the id will be generated automatically")
            raise
            building_id_key_gis = None

        # Load the additional gis attribute key dict
        if path_additional_gis_attribute_key_dict is not None:
            # check if it exists
            if os.path.exists(path_additional_gis_attribute_key_dict):
                with open(path_additional_gis_attribute_key_dict, 'r') as json_file:
                    additional_gis_attribute_key_dict = json.load(json_file)
            else:
                additional_gis_attribute_key_dict = None
        else:
            additional_gis_attribute_key_dict = None

        ## loop to create a building_obj for each footprint in the shp file
        collected_building_id_list = []
        number_of_buildings_in_shp_file = len(shape_file['geometry'])
        for building_index_in_gis in range(0, number_of_buildings_in_shp_file):
            # create the building object
            building_id_list, building_obj_list = BuildingBasic.make_buildingbasic_from_GIS(self, shape_file,
                                                                                            building_index_in_gis,
                                                                                            building_id_key_gis,
                                                                                            unit)
            # add the building to the urban canopy
            if building_obj_list is not None:
                added_building_id_list = self.add_list_of_buildings_to_dict(building_id_list,
                                                                            building_obj_list)
                collected_building_id_list.extend(added_building_id_list)

        # Collect the attributes to the buildings from the shp file
        for building_id in collected_building_id_list:
            (self.building_dict[building_id]
             .extract_building_attributes_from_GIS(shape_file, additional_gis_attribute_key_dict))

    def add_buildings_from_lb_polyface3d_json_to_dict(self, path_lb_polyface3d_json_file, typology=None,
                                                      other_options_to_generate_building=None):
        """
        Add the buildings from the lb polyface3d json dict to the urban canopy
        :param path_lb_polyface3d_json_file: path to the json file containing the lb polyface3d dict
        :param typology: typology object, if None, the typology will not be used
        :param other_options_to_generate_building: dict, other options to generate the building  todo: @Elie: to implement
        """
        # Load the json dict
        with open(path_lb_polyface3d_json_file, 'r') as json_file:
            lb_polyface3d_json_dict = json.load(json_file)

        # Loop over the buildings
        for identifier, lb_polyface3d_dict in lb_polyface3d_json_dict.items():
            if not (isinstance(lb_polyface3d_dict, dict) and (
                    isinstance(identifier, float) or isinstance(identifier, str))):
                raise TypeError(f"The json file is not valid, the identifier of the building should be "
                                f"a string or a floatand the values dictionaries dexcribing a LB Polyface3D")
            # Check if the building id is already in the urban canopy
            if identifier not in self.building_dict.keys():
                # Create the building object
                building_obj = BuildingBasic.make_buildingbasic_from_lb_polyface3d_json_dict(
                    identifier=identifier,
                    lb_polyface3d_dict=lb_polyface3d_dict,
                    typology=typology)
                if building_obj is not None:
                    # Add the building to the urban canopy
                    self.add_building_to_dict(identifier, building_obj)
            else:
                user_logger.warning("The building id {building_id} is already in the urban canopy, "
                                    "it will not be added again to the urban canopy. Please make sure you did not try "
                                    "to load the same file twice. Make sure that you did not use the same prefix to "
                                    "save the geometries".format(building_id=identifier))
                dev_logger.warning("The building id {building_id} is already in the urban canopy, "
                                   "it will not be added again to the urban canopy".format(
                    building_id=identifier))

    def add_buildings_from_hbjson_to_dict(self, path_directory_hbjson=None, path_file_hbjson=None,
                                          are_buildings_targets=False, keep_context_from_hbjson=False):
        """ Add the buildings from the hb models in the folder
        :param path_directory_hbjson: path to the directory containing the hbjson files
        :param path_file_hbjson: path to the hbjson file
        :param are_buildings_targets: boolean, True if the buildings are targets, False if they are not
        :return: None
        """
        if path_directory_hbjson is not None and os.path.isdir(path_directory_hbjson):
            # Get the list of the hbjson files
            hbjson_files_path_list = [os.path.join(path_directory_hbjson, hbjson_file) for hbjson_file in
                                      os.listdir(path_directory_hbjson) if hbjson_file.endswith(".hbjson")]
        elif path_file_hbjson is not None and os.path.isfile(path_file_hbjson):
            hbjson_files_path_list = [path_file_hbjson]
        else:
            logging.error(
                "The path to the hbjson file or the path to the directory containing the hbjson files are not valid")
            return
        # loop over the hbjson files
        for hbjson_file_path in hbjson_files_path_list:
            # Check if the file is not empty
            if os.path.getsize(hbjson_file_path) > 0:  # hbjson_file should be the fullpath of json
                # Create the building object
                building_HB_model_obj, identifier = BuildingModeled.make_buildingmodeled_from_hbjson(
                    path_hbjson=hbjson_file_path, is_target=are_buildings_targets,
                    keep_context=keep_context_from_hbjson)
                # Add the building to the urban canopy
                self.add_building_to_dict(identifier, building_HB_model_obj)
            else:
                logging.info("The file {} is empty".format(hbjson_file_path))

    def make_HB_model_envelops_from_buildings(self, path_folder=None):
        # todo @Elie: to be removed
        """ Make the hb model for the building envelop and save it to hbjson file if the path is provided """
        # List of the hb rooms representing the building envelops
        # HB_room_envelop_list = [building.export_building_to_elevated_HB_room_envelop() for building in self.building_dict.values()] todo:to delete if it works
        HB_room_envelop_list = []  # Initialize the list
        for building in self.building_dict.values():
            if type(building) is BuildingBasic:  # Make an HB room by extruding the footprint
                HB_room_envelop_list.append(building.export_building_to_elevated_HB_room_envelop())
            elif type(
                    building) is BuildingModeled:  # Extract the rooms from the HB model attribute of the building
                for HB_room in building.hb_model_obj.rooms:
                    HB_room_envelop_list.append(HB_room)
        # additional cleaning of the colinear vertices, might not be necessary
        for room in HB_room_envelop_list:
            room.remove_colinear_vertices_envelope(tolerance=TOLERANCE_LBT,
                                                   delete_degenerate=True)
        # Make the hb model
        HB_model = Model(identifier="urban_canopy_building_envelops", rooms=HB_room_envelop_list,
                         tolerance=TOLERANCE_LBT)
        HB_dict = HB_model.to_dict()
        if path_folder is not None:
            HB_model.to_hbjson(name="buildings_envelops", folder=path_folder)
        return HB_dict, HB_model

    def make_lb_polyface3d_extruded_footprint_of_buildings(self, overwrite=False):
        """
        Make the Ladybug polyface3d extruded footprints of the buildings in the urban canopy.
        :param overwrite: bool, if True, the polyface3d extruded footprints will be made even if they already exist
        """
        for building in self.building_dict.values():
            building.make_lb_polyface3d_extruded_footprint(overwrite=overwrite)

    def make_oriented_bounding_boxes_of_buildings(self, overwrite=False):
        """
        Make the oriented bounding boxes of the buildings in the urban canopy.
        param overwrite: bool, if True, the oriented bounding boxes will be made even if they already exist
        """
        for building in self.building_dict.values():
            building.make_lb_polyface3d_oriented_bounding_box(overwrite=overwrite)

    def transform_buildingbasic_into_building_model(self, building_id_list=None, use_typology=True,
                                                    typology_identification=False, are_simulated=False,
                                                    are_target=False, **kwargs):
        """
        Convert the buildings to BuildingModeled
        :param building_id_list: list of building id to be considered
        :param use_typology: bool: default=True: if True, the typology will be used to define the properties of the BuildingModel object
        :param typology_identification: bool: default=False: if True, the typology identifier will be used to identify
            the typology of the BuildingModel object, the properties of the BuildingModel object will be defined
            according to the typology. (default=False)
            :param are_simulated: bool: default=False: if True, the BuildingModel object will be simulated
        :param are_target: bool: default=False: if True, the BuildingModel object will be a target
        :param kwargs: dict: additional parameters to be passed to the building model object
            autozoner: bool: default=False: if True, the thermal zones will be automatically generated
            use_layout_from_typology: bool: default=False: if True, the layout will be defined according to the typology
            use_properties_from_typology: bool: default=True: if True, the new building model will be generated according
            to the properties of the typology, especially the construction material and the window to wall ratio
            typology_identifier_model_id: str: default=None: id of the machine learning model to be used to identify the typology
        :return:
        """

        # Load the Typology identifier ML model if needed
        if typology_identification:
            None
            # Typology.load_typology_identifier_model(path_ml_model_folder=path_ml_model_folder,typology_identifier_model_id=typology_identifier_model_id)
        else:
            typology_identifier_model = None

        # Convert the buildings to BuildingModeled
        for building_id in building_id_list:
            # Check if the building_id is in the urban canopy
            if building_id not in self.building_dict.keys():
                user_logger.info(
                    "The building id {building_id} is not in the urban canopy, it will not be converted "
                    "to BuildingModeled".format(building_id=building_id))
                dev_logger.info("{building_id} is not in the urban canopy, it will not be converted "
                                "to BuildingModeled".format(building_id=building_id))
                continue
            building_obj = self.building_dict[building_id]
            # If the building is already BuildingModeled do nothing and move on to the next building
            if isinstance(building_obj, BuildingModeled):
                continue
            try:
                # todo @Elie: add the typology identifier model if needed
                new_building_obj = building_obj.convert_building_to_BuildingModeled(
                    is_target=are_target, is_simulated=are_simulated, use_typology=use_typology,
                    typology_identification=typology_identification,
                    typology_identifier_model=typology_identifier_model, **kwargs)
                self.building_dict[building_id] = new_building_obj
            except:
                user_logger.info("The conversion of the building {building_id} to BuildingModeled failed, it "
                                 "will not be converted".format(building_id=building_id))
                dev_logger.info(
                    "The conversion of the building {building_id} to BuildingModeled failed".format(
                        building_id=building_id))

    def compute_moving_vector_to_origin(self):
        """ Make the moving vector to move the urban canopy to the origin """
        # get the center of mass (Point3D) of the urban canopy on the x,y plane
        list_of_centroid = [building.lb_face_footprint.centroid for building in self.building_dict.values()]
        center_of_mass_x = sum([centroid.x for centroid in list_of_centroid]) / len(list_of_centroid)
        center_of_mass_y = sum([centroid.y for centroid in list_of_centroid]) / len(list_of_centroid)
        # Find the minimum elevation of the buildings in the urban canopy
        # The elevation of all building will be rebased considering the minimum elevation to be z=0
        min_elevation = min([building.elevation for building in self.building_dict.values()])
        self.moving_vector_to_origin = [-center_of_mass_x, -center_of_mass_y, -min_elevation]

    def move_buildings_to_origin(self):
        """ Move the buildings to the origin if the urban canopy has not already been moved to the origin"""
       # Check if the the urban canopy has already been moved to the origin
        if self.moving_vector_to_origin is not None:
            # Check if a building has not been moved yet
            flag = False
            for building in self.building_dict.values():
                if not building.moved_to_origin:
                    flag = True
                    break
            if not flag:
                return  # The urban canopy has already been moved to the origin, no need to move the buildings
            logging.info(
                "The urban canopy has already been moved to the origin, the building will be moved back and"
                " then moved again to the origin with the new buildings")
            # Move back the buildings to their original position
            self.move_back_buildings()
        # Compute the moving vector
        self.compute_moving_vector_to_origin()
        # Move the buildings
        for building in self.building_dict.values():
            building.move(self.moving_vector_to_origin)

    def move_back_buildings(self):
        """ Move back the buildings to their original position by the opposite vector """
        for building in self.building_dict.values():
            # Check if the building has been moved to the origin already
            if building.moved_to_origin:
                # Move by the opposite vector
                building.move([-coordinate for coordinate in self.moving_vector_to_origin])

    def make_merged_faces_hb_model_of_buildings(self, building_id_list=None,
                                                orient_roof_mesh_to_according_to_building_orientation=True,
                                                north_angle=0, overwrite=False):
        """
        Make the merged faces hb model of the buildings in the urban canopy.
        :param building_id_list: list of the building id to make the merged faces hb model,
            if None or empty list, all the simulated and target buildings will be initialized.
        :param orient_roof_mesh_to_according_to_building_orientation: boolean, if True, the roof mesh will be oriented
            according to the building orientation.
        :param north_angle: float, angle of the north in degrees.
        """
        # Checks of the building_id_list parameter to give feedback to the user if there is an issue with an id
        if not (building_id_list is None or building_id_list is []):
            for building_id in building_id_list:
                if building_id not in self.building_dict.keys():
                    user_logger.warning(f"The building id {building_id} is not in the urban canopy")
                    dev_logger.info(
                        f"The building id {building_id} is not in the urban canopy, make sure you indicated "
                        f"the proper identifier in the input")
                elif not isinstance(self.building_dict[building_id], BuildingModeled):
                    user_logger.warning(
                        f"The building id {building_id} does not have a Honeybee model, it's not "
                        f"possible to merge the faces. You can upgrade the building {building_id} and"
                        f" generate a Honeybee model out of it  with the component xxx.")

        for building_obj in self.building_dict.values():
            if ((building_id_list is None or building_id_list is []) or building_obj.id in building_id_list) \
                    and isinstance(building_obj, BuildingModeled):
                building_obj.make_merged_faces_hb_model(
                    orient_roof_mesh_to_according_to_building_orientation=orient_roof_mesh_to_according_to_building_orientation,
                    north_angle=north_angle, overwrite=overwrite)

    def perform_first_pass_context_filtering_on_buildings(self, building_id_list=None,
                                                          on_building_to_simulate=False,
                                                          min_vf_criterion=0.01,
                                                          overwrite=False):
        """
        Perform the first pass context filtering on the BuildingModeled objects in the urban canopy that need
        to be simulated.
        By default, the first pass context filtering is performed on all the target buildings.

        :param building_id_list: list of str, the list of building id to perform the first pass context filtering on.
        :param on_building_to_simulate: bool, if True, perform the first pass context filtering on the buildings
            to simulate.
        :param min_vf_criterion: float, the minimum view factor criterion.
        :param overwrite: bool, if True, the existing context selection will be overwritten.
        :return: context_building_id_list: list of str, the list of building id that are in the context of the buildings
            to simulate
        :return: sim_duration_dict: dict, the dictionary of the simulation duration for each building
        """
        # Make oriented bounding boxes of the buildings in the urban canopy if they don't exist already
        self.make_oriented_bounding_boxes_of_buildings(overwrite=overwrite)
        # if we specify the building no need to do it on all the simulated buildings
        if building_id_list is not None and building_id_list != []:
            on_building_to_simulate = False
        # Checks of the building_id_list parameter to give feedback to the user if there is an issue with an id
        if not (building_id_list is None or building_id_list is []):
            for building_id in building_id_list:
                if building_id not in self.building_dict.keys():
                    user_logger.warning(f"The building id {building_id} is not in the urban canopy")
                    dev_logger.info(
                        f"The building id {building_id} is not in the urban canopy, make sure you indicated "
                        f"the proper identifier in the input")
                elif not isinstance(self.building_dict[building_id], BuildingModeled):
                    user_logger.warning(
                        f"The building id {building_id} is not a BuildingModeled type, it does not have Honeybee Model "
                        f"attribute, context filtering cannot be performed. "
                        f"You can use the adequate functions or components to convert the building{building_id} "
                        f"into BuildingModeled.")
        # Initialize the list of buildings that are in the context of the buildings to simulate
        selected_context_building_id_list = []  # Initialize the list
        # Put the building ids and the bounding boxes in lists to pass down to the building context filtering method
        uc_building_id_list = list(self.building_dict.keys())
        uc_building_bounding_box_list = [building_obj.lb_polyface3d_oriented_bounding_box for
                                         building_obj in self.building_dict.values()]
        # Dictionary of the simulation duration, to get the duration of the simulation for each building
        sim_duration_dict = {}
        # Loop over the buildings
        for i, (building_id, building_obj) in enumerate(self.building_dict.items()):
            if (isinstance(building_obj, BuildingModeled)
                    and (((
                                  building_id_list is not None and building_id_list is not []) and building_id in building_id_list)
                         or (on_building_to_simulate and building_obj.to_simulate)
                         or ((
                                     building_id_list is None or building_id_list is []) and building_obj.is_target))):
                # Perform the first pass context filtering
                current_building_selected_context_building_id_list, duration = building_obj. \
                    perform_first_pass_context_filtering(
                    uc_building_id_list=uc_building_id_list,
                    uc_building_bounding_box_list=uc_building_bounding_box_list,
                    min_vf_criterion=min_vf_criterion, overwrite=overwrite)
                selected_context_building_id_list += current_building_selected_context_building_id_list
                sim_duration_dict[building_id] = duration
        # Remove duplicates
        selected_context_building_id_list = list(set(selected_context_building_id_list))

        return selected_context_building_id_list, sim_duration_dict

    def perform_second_pass_context_filtering_on_buildings(self, building_id_list=None, number_of_rays=3,
                                                           on_building_to_simulate=False,
                                                           consider_windows=False,
                                                           keep_shades_from_user=False, no_ray_tracing=False,
                                                           overwrite=False, keep_discarded_faces=False):
        """
        Perform the second pass context filtering on BuildingModeled objects in the urban canopy.
        It uses ray-tracing to select the relevant context surfaces for shading computation.
        By default, the second pass context filtering is performed on all the simulated (and thus target buildings).
        If the no_ray_tracing parameter is set to True, the second pass context filtering will be performed
        without ray-tracing and will just consider all the surfaces in the context of the buildings to simulate.
        :param building_id_list: list of str, the list of building id to perform the second pass context filtering on.
        :param on_building_to_simulate: bool, if True, perform the second pass context filtering on the buildings
            to simulate.
        :param consider_windows: bool, if True, the windows will be considered in the context filtering.
        :param keep_shades_from_user: bool, if True, the shades from the user will be kept in the context filtering.
        :param no_ray_tracing: bool, if True, the second pass context filtering will be performed without ray-tracing.
        :param overwrite: bool, if True, the existing context selection will be overwritten.
        :param keep_discarded_faces: bool, if True, the discarded faces will be kept in the context filtering.
        :return: result_summary_dict: dict, the dictionary of the number of context faces for each building
            and the duration of the simulation for each building
        """
        # Make extruded footprints of the buildings in the LB polyface3d format if they don't exist already
        self.make_lb_polyface3d_extruded_footprint_of_buildings()
        # Generate the Pyvista mesh including all the buildings in the urban canopy
        if overwrite or self.full_context_pyvista_mesh is None:
            self.make_pyvista_polydata_mesh_of_all_buildings()  # todo @Elie: to be implemented and remove capital letters
        # If we specify the building no need to do it on all the simulated buildings
        if building_id_list is not None and building_id_list != []:
            on_building_to_simulate = False
        # Checks of the building_id_list parameter to give feedback to the user if there is an issue with an id
        if not (building_id_list is None or building_id_list is []):
            for building_id in building_id_list:
                if building_id not in self.building_dict.keys():
                    user_logger.warning(f"The building id {building_id} is not in the urban canopy")
                    dev_logger.info(
                        f"The building id {building_id} is not in the urban canopy, make sure you indicated "
                        f"the proper identifier in the input")
                elif not isinstance(self.building_dict[building_id], BuildingModeled):
                    user_logger.warning(
                        f"The building id {building_id} is not a BuildingModeled type, it does not have Honeybee Model "
                        f"attribute, context filtering cannot be performed. "
                        f"You can use the adequate functions or components to convert the building{building_id} "
                        f"into BuildingModeled.")
        # Dictionary of the simulation duration, to get the duration of the simulation for each building
        result_summary_dict = {}
        flag_use_envelop = False  # To return a message if at least one context building does not have a HB model
        # Loop over the buildings
        for i, (building_id, building_obj) in enumerate(self.building_dict.items()):
            if (isinstance(building_obj, BuildingModeled)
                    and (((
                                  building_id_list is not None and building_id_list is not []) and building_id in building_id_list)
                         or (on_building_to_simulate and building_obj.to_simulate)
                         or ((
                                     building_id_list is None or building_id_list is []) and building_obj.is_target))):
                # Perform the Second pass context filtering
                nb_context_faces, duration, flag_use_envelop = building_obj.perform_second_pass_context_filtering(
                    uc_shade_manager=self.shade_manager, uc_building_dictionary=self.building_dict,
                    full_urban_canopy_pyvista_mesh=self.full_context_pyvista_mesh,
                    number_of_rays=number_of_rays,
                    consider_windows=consider_windows, keep_shades_from_user=keep_shades_from_user,
                    no_ray_tracing=no_ray_tracing, overwrite=overwrite, flag_use_envelop=flag_use_envelop,
                    keep_discarded_faces=keep_discarded_faces)
                result_summary_dict[building_id] = {"nb_context_faces": nb_context_faces,
                                                    "duration": duration}

        return result_summary_dict

    def make_pyvista_polydata_mesh_of_all_buildings(self):
        """
        Make the Pyvista mesh of all the buildings in the urban canopy to be used for the second pass context filtering.
        That way, the mesh is generated once only and can be reused for all the buildings.
        """
        # Initialize the list of HB model and LB polyface3d to be used to make the full context mesh
        hb_model_and_lb_polyface3d_list = []

        for building in self.building_dict.values():
            if isinstance(building, BuildingBasic):
                # Use the LB Polyface3D extruded footprint for BuildingBasic,
                building.make_lb_polyface3d_extruded_footprint()  # Create it if it doen't exist
                hb_model_and_lb_polyface3d_list.append(building.lb_polyface3d_extruded_footprint)
            elif isinstance(building, BuildingModeled):
                # Use preferably the merged faces HB model of the building
                if building.merged_faces_hb_model_dict is not None:
                    hb_model_and_lb_polyface3d_list.append(
                        Model.from_dict(building.merged_faces_hb_model_dict))
                # Check if the building has a HB model
                elif building.hb_model_obj is not None:
                    # Make the HB model mesh
                    hb_model_and_lb_polyface3d_list.append(building.hb_model_obj.to_pyvista_mesh())
                else:
                    dev_logger.info(
                        f"The building {building.id} does not have a Honeybee model, it will not be included in the "
                        f"full context mesh")
            else:
                dev_logger.info(
                    f"The building {building.id} is not a BuildingBasic or a BuildingModeled type, it will not be "
                    f"included in the full context mesh")

        # Make the full context mesh
        self.full_context_pyvista_mesh = make_pyvista_polydata_from_list_of_hb_model_and_lb_polyface3d(
            hb_model_and_lb_polyface3d_list=hb_model_and_lb_polyface3d_list)

    def load_epw_and_hb_simulation_parameters_for_ubes(self, path_simulation_folder,
                                                       path_hbjson_simulation_parameter_file,
                                                       path_weather_file, ddy_file=None,
                                                       overwrite=False):
        """
        Load the HB simulation parameters from the json file, check if it is valid, correct it eventually and add to the
        UrbanCanopyEnergySimulation object.
        :param path_simulation_folder: string, path to the simulation folder.
        :param path_hbjson_simulation_parameter_file: string, path to the json file containing the HB simulation
            parameters.
        :param path_weather_file: string, path to the epw file.
        :param ddy_file: string, path to the ddy (design days) file.
        :param overwrite: bool, if True, the existing HB simulation parameters will be overwritten.
        """

        flag_re_initialize_building_bes = self.ubes_obj.load_epw_and_hb_simulation_parameters(
            path_hbjson_simulation_parameter_file=path_hbjson_simulation_parameter_file,
            path_weather_file=path_weather_file, ddy_file=ddy_file, overwrite=overwrite)

        # Re-initialize the UBES of the whole UrbanCanopy if needed
        if flag_re_initialize_building_bes:
            # Delete the BES temporary folder if it exists
            path_ubes_temp_folder = os.path.join(path_simulation_folder, name_temporary_files_folder,
                                                 name_ubes_temp_simulation_folder)
            if os.path.exists(path_ubes_temp_folder):
                shutil.rmtree(path_ubes_temp_folder)
            # Re-initialize the BES of the buildings
            for building_obj in self.building_dict.values():
                if isinstance(building_obj, BuildingModeled) and (
                        building_obj.is_target or building_obj.to_simulate):
                    building_obj.re_initialize_bes()

    def generate_idf_files_for_ubes_with_openstudio(self, path_simulation_folder, building_id_list=None,
                                                    overwrite=False, silent=False, run_in_parallel=False):
        """
        Generate the idf files for the buildings in the urban canopy.
        :param path_simulation_folder: string, path to the folder where the simulation will be performed.
        :param building_id_list: list of the building id to generate the idf files,
            if None or empty list, all the target buildings will be initialized.
        :param overwrite: bool, if True, the existing idf files will be overwritten.
        :param silent: bool, if True, the OpenStudio messages will not be printed.
        :param run_in_parallel: bool, if True, the idf files will be generated in parallel, not operational yet.
        """
        # Checks of the building_id_list parameter to give feedback to the user if there is an issue with an id
        if not (building_id_list is None or building_id_list is []):
            for building_id in building_id_list:
                if building_id not in self.building_dict.keys():
                    user_logger.warning(f"The building id {building_id} is not in the urban canopy")
                    dev_logger.info(
                        f"The building id {building_id} is not in the urban canopy, make sure you indicated "
                        f"the proper identifier in the input")
                elif not isinstance(self.building_dict[building_id], BuildingModeled) or (not \
                        self.building_dict[building_id].is_target or not self.building_dict[
                    building_id].to_simulate):
                    user_logger.warning(
                        f"The building id {building_id} is not a target building or is not set to be "
                        f"simulated, thus it cannot be simulated by with EnergyPlus")
        # Generate or clean the temporary folder for the ubes simulation files
        path_ubes_temp_sim_folder = os.path.join(path_simulation_folder, name_temporary_files_folder,
                                                 name_ubes_temp_simulation_folder)
        if os.path.isdir(path_ubes_temp_sim_folder):
            if overwrite:
                shutil.rmtree(path_ubes_temp_sim_folder)
                os.mkdir(path_ubes_temp_sim_folder)
        else:
            os.mkdir(path_ubes_temp_sim_folder)
        # Write the EPW and simulation parameters files in the temporary ubes folder
        path_epw_file, path_hbjson_simulation_parameters = self.ubes_obj.write_epw_and_hb_simulation_parameters(
            path_ubes_temp_sim_folder=path_ubes_temp_sim_folder)
        # Generate the idf files for the buildings
        for building_obj in self.building_dict.values():
            if ((building_id_list is None or building_id_list is []) or building_obj.id in building_id_list) \
                    and isinstance(building_obj, BuildingModeled) and (
                    building_obj.is_target or building_obj.to_simulate) :
                # Generate the hbjson then idf file for the building simulation
                building_obj.generate_idf_for_bes_with_openstudio(
                    path_ubes_temp_sim_folder=path_ubes_temp_sim_folder,
                    path_hbjson_simulation_parameters=path_hbjson_simulation_parameters,
                    path_epw_file=path_epw_file, overwrite=overwrite, silent=silent)

    def run_idf_files_for_ubes_with_energyplus(self, path_simulation_folder, building_id_list=None,
                                               overwrite=False, silent=False, run_in_parallel=False):
        """
        Run the idf files for the buildings in the urban canopy.
        :param path_simulation_folder: string, path to the folder where the simulation will be performed.
        :param building_id_list: list of the building id to generate the idf files,
            if None or empty list, all the target buildings will be initialized.
        :param overwrite: bool, if True, the existing idf files will be overwritten.
        :param silent: bool, if True, the OpenStudio messages will not be printed.
        """
        # Checks of the building_id_list parameter to give feedback to the user if there is an issue with an id
        if not (building_id_list is None or building_id_list is []):
            for building_id in building_id_list:
                if building_id not in self.building_dict.keys():
                    user_logger.warning(f"The building id {building_id} is not in the urban canopy")
                    dev_logger.info(
                        f"The building id {building_id} is not in the urban canopy, make sure you indicated "
                        f"the proper identifier in the input")
                elif not isinstance(self.building_dict[building_id], BuildingModeled) or (not \
                        self.building_dict[building_id].is_target or not self.building_dict[
                    building_id].to_simulate):
                    user_logger.warning(
                        f"The building id {building_id} is not a target building or is not set to be "
                        f"simulated, thus it cannot be simulated by with EnergyPlus")
        # Path to the temporary folder of the ubes simulation files
        path_ubes_temp_sim_folder = os.path.join(path_simulation_folder, name_temporary_files_folder,
                                                 name_ubes_temp_simulation_folder)

        path_epw_file = os.path.join(path_ubes_temp_sim_folder, name_ubes_epw_file)
        # Initialize the duration directory
        duration_dict = {}
        # run the idf files for the buildings
        for building_obj in self.building_dict.values():
            if ((building_id_list is None or building_id_list is []) or building_obj.id in building_id_list) \
                    and isinstance(building_obj, BuildingModeled) and (
                    building_obj.is_target or building_obj.to_simulate):
                # Run the idf file for the building simulation
                duration = building_obj.run_idf_with_energyplus_for_bes(
                    path_ubes_temp_sim_folder=path_ubes_temp_sim_folder,
                    path_epw_file=path_epw_file, overwrite=overwrite, silent=silent)
                if duration is not None:
                    duration_dict[building_obj.id] = duration
        # Make the UBES simulation result folder or overwrite it if necessary
        path_ubes_sim_result_folder = os.path.join(path_simulation_folder, name_ubes_simulation_result_folder)
        if os.path.isdir(path_ubes_sim_result_folder):
            if overwrite:
                shutil.rmtree(path_ubes_sim_result_folder)
                os.mkdir(path_ubes_sim_result_folder)
        else:
            os.mkdir(path_ubes_sim_result_folder)
        # Move the sql and err (=log) file to the UBES result folder
        for building_obj in self.building_dict.values():
            if isinstance(building_obj, BuildingModeled):  # no need for more checking
                building_obj.move_bes_result_files_from_temp_to_result_folder(
                    path_ubes_temp_sim_folder=path_ubes_temp_sim_folder,
                    path_ubes_sim_result_folder=path_ubes_sim_result_folder
                )

        if duration_dict.values() != []:
            self.ubes_obj.has_run = True

        return duration_dict

    def extract_ubes_results(self, path_simulation_folder, cop_heating, cop_cooling):
        """
        Read the UBES result files for the buildings in the urban canopy.
        :param path_simulation_folder: string, path to the simulation folder
        :param cop_heating: float, coefficient of performance for heating
        :param cop_cooling: float, coefficient of performance for cooling
        """
        if not self.ubes_obj.has_run:
            user_logger.warning("The UBES simulation has not been run yet, the result cannot be extracted")
            return
        path_ubes_sim_result_folder = os.path.join(path_simulation_folder, name_ubes_simulation_result_folder)
        bes_result_dict_list = []
        # Extract the UBES results for the buildings
        for building_obj in self.building_dict.values():
            if isinstance(building_obj,
                          BuildingModeled):  # no need for more checking, the building themselves
                # will check if they have been simulated
                bes_result_dict = building_obj.extract_bes_results(
                    path_ubes_sim_result_folder=path_ubes_sim_result_folder, cop_heating=cop_heating,
                    cop_cooling=cop_cooling)
                if bes_result_dict is not None:
                    bes_result_dict_list.append(bes_result_dict)
        # Compute the results at the urban canopy level
        self.ubes_obj.compute_ubes_results(
            bes_result_dict_list=bes_result_dict_list)  # todo @Elie: to be implemented
        # Export the results to csv
        """ The export is made at the end to make sure none of the buildings have failed to extract the results before 
        exporting the results at the urban canopy level."""
        self.ubes_obj.to_csv(path_ubes_sim_result_folder=path_ubes_sim_result_folder)
        for building_obj in self.building_dict.values():
            if isinstance(building_obj, BuildingModeled):
                building_obj.export_bes_results_to_csv(
                    path_ubes_sim_result_folder=path_ubes_sim_result_folder)

    def generate_sensor_grid_on_buildings(self, building_id_list=None, bipv_on_roof=True,
                                          bipv_on_facades=True, roof_grid_size_x=1,
                                          facades_grid_size_x=1,
                                          roof_grid_size_y=1, facades_grid_size_y=1, offset_dist=0.1,
                                          overwrite=False):
        """
        Generate the sensor grid for the buildings in the urban canopy.
        :param bipv_on_roof: Boolean to indicate if the simulation should be done on the roof
        :param bipv_on_facades: Boolean to indicate if the simulation should be done on the facades
        :param building_id_list: list of the building id to generate the sensor grid,
            if None or empty list, all the target buildings will be initialized.
        :param roof_grid_size_x: float, grid size of the sensor grid on the roof in the x direction.
        :param facades_grid_size_x: float, grid size of the sensor grid on the facades in the x direction.
        :param roof_grid_size_y: float, grid size of the sensor grid on the roof in the y direction.
        :param facades_grid_size_y: float, grid size of the sensor grid on the facades in the y direction.
        :param offset_dist: float, offset distance between the sensor grid and the building.
        :param overwrite: bool, if True, the existing sensor grid will be overwritten.
        """
        # Checks of the building_id_list parameter to give feedback to the user if there is an issue with an id
        if not (building_id_list is None or building_id_list is []):
            for building_id in building_id_list:
                if building_id not in self.building_dict.keys():
                    user_logger.warning(f"The building id {building_id} is not in the urban canopy")
                    dev_logger.info(
                        f"The building id {building_id} is not in the urban canopy, make sure you indicated "
                        f"the proper identifier in the input")
                elif not isinstance(self.building_dict[building_id], BuildingModeled) or not \
                        self.building_dict[building_id].is_target:
                    user_logger.warning(
                        f"The building id {building_id} is not a target building, a radiation analysis "
                        f"cannot be performed if the building is not a target. You can update "
                        f"the properties of the building {building_id} to make it a target building.")
        # Generate the sensor grid for the buildings
        for building_obj in self.building_dict.values():
            if ((building_id_list is None or building_id_list is []) or building_obj.id in building_id_list) \
                    and isinstance(building_obj, BuildingModeled) and building_obj.is_target:
                building_obj.generate_sensor_grid(bipv_on_roof=bipv_on_roof,
                                                  bipv_on_facades=bipv_on_facades,
                                                  roof_grid_size_x=roof_grid_size_x,
                                                  facades_grid_size_x=facades_grid_size_x,
                                                  roof_grid_size_y=roof_grid_size_y,
                                                  facades_grid_size_y=facades_grid_size_y,
                                                  offset_dist=offset_dist,
                                                  overwrite=overwrite)

    def run_annual_solar_irradiance_simulation_on_buildings(self, path_simulation_folder,
                                                            building_id_list=None,
                                                            path_weather_file=default_path_weather_file,
                                                            overwrite=False, north_angle=0, silent=False):
        """
        Run the solar radiation simulation for the buildings in the urban canopy.
        :param building_id_list: list of the building id to run the simulation, if None or empty list, all the target
        :param path_simulation_folder: string, path to the folder where the simulation will be performed.
        :param path_weather_file: string, path to the weather file.
        :param overwrite: boolean, if True, the simulation will be run again and the results will overwrite the
            existing ones.
        :param north_angle: float, angle of the north in degrees.
        :param silent: boolean, if True, the console outputs will be disabled.
        """

        # Todo @Elie : can add a progress bar

        # Checks of the building_id_list parameter to give feedback to the user if there is an issue with an id
        if not (building_id_list is None or building_id_list is []):
            for building_id in building_id_list:
                if building_id not in self.building_dict.keys():
                    user_logger.warning(f"The building id {building_id} is not in the urban canopy")
                    dev_logger.info(
                        f"The building id {building_id} is not in the urban canopy, make sure you indicated "
                        f"the proper identifier in the input")
                elif not isinstance(self.building_dict[building_id], BuildingModeled) or not \
                        self.building_dict[building_id].is_target:
                    user_logger.warning(
                        f"The building id {building_id} is not a target building, a radiation analysis "
                        f"cannot be performed if the building is not a target. You can update "
                        f"the properties of the building {building_id} to make it a target building.")
        # Run the simulation for the buildings
        for building_obj in self.building_dict.values():
            if ((building_id_list is None or building_id_list is []) or building_obj.id in building_id_list) \
                    and isinstance(building_obj, BuildingModeled) and building_obj.is_target:
                building_obj.run_annual_solar_irradiance_simulation(
                    path_simulation_folder=path_simulation_folder,
                    path_weather_file=path_weather_file,
                    overwrite=overwrite,
                    north_angle=north_angle, silent=silent)

    def run_bipv_panel_simulation_on_buildings(self, path_simulation_folder, bipv_scenario_identifier,
                                               building_id_list, roof_id_pv_tech, facades_id_pv_tech,
                                               roof_transport_id,
                                               facades_transport_id, roof_inverter_id, facades_inverter_id,
                                               roof_inverter_sizing_ratio=0.9,
                                               facades_inverter_sizing_ratio=0.9,
                                               efficiency_computation_method="yearly",
                                               minimum_panel_eroi=1.2, start_year=datetime.now().year,
                                               end_year=datetime.now().year + 50,
                                               replacement_scenario="replace_failed_panels_every_X_years",
                                               continue_simulation=False, **kwargs):
        """
        Run the panels simulation on the urban canopy
        :param path_simulation_folder: path to the simulation folder
        :param bipv_scenario_identifier: string: identifier of the BIPV scenario
        :param building_id_list: list of string: list of the building id to run the simulation on
        :param roof_id_pv_tech: string: id of the roof technology used
        :param facades_id_pv_tech: string: id of the facades technology used
        :param roof_transport_id: string: id of the roof transportation used
        :param facades_transport_id: string: id of the facades transportation used
        :param roof_inverter_id: string: id of the roof inverter used
        :param facades_inverter_id: string: id of the facades inverter used
        :param roof_inverter_sizing_ratio: float: sizing ratio of the roof inverter, default = 0.9
        :param facades_inverter_sizing_ratio: float: sizing ratio of the facades inverter, default = 0.9
        :param efficiency_computation_method: string: method used to compute the efficiency of the panels,
            default = "yearly"
        :param minimum_panel_eroi: float: minimum energy return on investment of the panels, default = 1.2
        :param start_year: int: start year of the simulation, default = datetime.now().year
        :param end_year: int: end year of the simulation, default = datetime.now().year + 50
        :param replacement_scenario: string: scenario of replacements for the panels, default = 'yearly'
        :param continue_simulation: bool: if True, continue the simulation, default = False
        :param kwargs: dict: additional arguments to be passed to the run_bipv_panel_simulation method of the
            BuildingModeled object
        """

        # If start_year is higher than end_year, raise an error
        if start_year >= end_year:
            raise ValueError(
                "The start year is higher than the end year, the simulation will not be performed")

        # Add a new scenario if it does not exist already
        if not continue_simulation or bipv_scenario_identifier not in self.bipv_scenario_dict.keys():
            self.bipv_scenario_dict[bipv_scenario_identifier] = BipvScenario(
                identifier=bipv_scenario_identifier,
                start_year=start_year,
                end_year=end_year)
        # Continue the simulation with the existing scenario
        else:
            self.bipv_scenario_dict[bipv_scenario_identifier].continue_simulation(start_year=start_year,
                                                                                  end_year=end_year)

        bipv_scenario_obj = self.bipv_scenario_dict[bipv_scenario_identifier]

        # Checks of the building_id_list parameter to give feedback to the user if there is an issue with an id
        if not (building_id_list is None or building_id_list is []):
            for building_id in building_id_list:
                if building_id not in self.building_dict.keys():
                    user_logger.warning(f"The building id {building_id} is not in the urban canopy")
                    dev_logger.info(
                        f"The building id {building_id} is not in the urban canopy, make sure you indicated "
                        f"the proper identifier in the input")
                elif not isinstance(self.building_dict[building_id], BuildingModeled) or not \
                        self.building_dict[building_id].is_target:
                    user_logger.warning(
                        f"The building id {building_id} is not a target building, a radiation analysis "
                        f"cannot be performed if the building is not a target. You can update "
                        f"the properties of the building {building_id} to make it a target building.")
                elif self.building_dict[building_id].solar_radiation_and_bipv_simulation_obj is None:
                    user_logger.warning(f"No mesh for radiation simulation was generated for The building id "
                                        f"{building_id}, the radiation simulation will not performed for this building.")
                elif self.building_dict[
                    building_id].solar_radiation_and_bipv_simulation_obj.roof_annual_panel_irradiance_list is None and \
                        self.building_dict[
                            building_id].solar_radiation_and_bipv_simulation_obj.facades_annual_panel_irradiance_list is None:
                    user_logger.warning(f"No irradiance simulation was run for The building id "
                                        f"{building_id}, the BIPV simulation will not be run for this building.")

        # Read the files in the defauly and library and extract the BIPV technologies, transportation and inverter objects
        bipv_technology_obj_dict = {}
        bipv_transportation_obj_dict = {}
        bipv_inverter_obj_dict = {}
        for path_folder in [path_folder_default_bipv_parameters, path_folder_user_bipv_parameters]:
            bipv_technology_obj_dict = BipvTechnology.load_pv_technologies_from_json_to_dictionary(
                bipv_technology_obj_dict=bipv_technology_obj_dict, path_json_folder=path_folder)
            bipv_transportation_obj_dict = BipvTransportation.load_bipv_transportation_obj_from_json_to_dictionary(
                transportation_obj_dict=bipv_transportation_obj_dict, path_json_folder=path_folder)
            bipv_inverter_obj_dict = BipvInverter.load_bipv_inverter_obj_from_json_to_dictionary(
                inverter_obj_dict=bipv_inverter_obj_dict, path_json_folder=path_folder)

        # Reinitialize the simulation for the all the buildings if the simulation is not continued
        if not continue_simulation:
            for building_obj in self.building_dict.values():
                if isinstance(building_obj, BuildingModeled) and building_obj.is_target:
                    building_obj.solar_radiation_and_bipv_simulation_obj.init_bipv_simulation()

        #
        roof_pv_tech_obj = bipv_technology_obj_dict[roof_id_pv_tech]
        facade_pv_tech_obj = bipv_technology_obj_dict[facades_id_pv_tech]
        roof_transport_obj = bipv_transportation_obj_dict[roof_transport_id]
        facades_transport_obj = bipv_transportation_obj_dict[facades_transport_id]
        roof_inverter_obj = bipv_inverter_obj_dict[roof_inverter_id]
        facades_inverter_obj = bipv_inverter_obj_dict[facades_inverter_id]

        # Folder to store the results
        path_radiation_and_bipv_result_folder = os.path.join(path_simulation_folder,
                                                             name_radiation_simulation_folder)

        # Run the simulation for the buildings
        solar_rad_and_bipv_obj_list = []
        for building_obj in self.building_dict.values():
            if self.does_building_fits_bipv_requirement(building_obj=building_obj,
                                                        building_id_list=building_id_list,
                                                        continue_simulation=continue_simulation):
                building_obj.building_run_bipv_panel_simulation(path_simulation_folder=path_simulation_folder,
                                                                roof_pv_tech_obj=roof_pv_tech_obj,
                                                                facades_pv_tech_obj=facade_pv_tech_obj,
                                                                roof_inverter_obj=roof_inverter_obj,
                                                                facades_inverter_obj=facades_inverter_obj,
                                                                roof_inverter_sizing_ratio=roof_inverter_sizing_ratio,
                                                                facades_inverter_sizing_ratio=facades_inverter_sizing_ratio,
                                                                roof_transport_obj=roof_transport_obj,
                                                                facades_transport_obj=facades_transport_obj,
                                                                uc_start_year=bipv_scenario_obj.start_year,
                                                                uc_current_year=start_year,
                                                                uc_end_year=bipv_scenario_obj.end_year,
                                                                efficiency_computation_method=efficiency_computation_method,
                                                                minimum_panel_eroi=minimum_panel_eroi,
                                                                replacement_scenario=replacement_scenario,
                                                                continue_simulation=continue_simulation,
                                                                path_radiation_and_bipv_result_folder=path_radiation_and_bipv_result_folder,
                                                                **kwargs)
                solar_rad_and_bipv_obj_list.append(building_obj.solar_radiation_and_bipv_simulation_obj)

        """ to be implemented potentially, but not likely to be """
        # # Add the selected panels to the building shades
        # for building_obj in self.building_dict.values():
        #     if isinstance(building_obj, BuildingModeled):
        #         building_obj.add_selected_bipv_panels_to_shades()

        # Get the list of buildings that were simualted
        building_id_list = self.get_list_of_bipv_simulated_buildings()
        bipv_scenario_obj.set_simulated_building_id_list(building_id_list=building_id_list)
        # Compute the results at urban scale
        bipv_scenario_obj.sum_bipv_results_at_urban_scale(
            solar_rad_and_bipv_obj_list=solar_rad_and_bipv_obj_list)

        # Write urban scale results to CSV file (overwrite existing file if it exists)
        bipv_scenario_obj.write_bipv_results_to_csv(
            path_radiation_and_bipv_result_folder=path_radiation_and_bipv_result_folder)

    @staticmethod
    def does_building_fits_bipv_requirement(building_obj, building_id_list, continue_simulation):
        """
        Check if the building fits the requirements to run the BIPV simulation
        :param building_obj: Building object
        :param building_id_list: list of the building id to run the simulation, if None or empty list, all the target
        :param continue_simulation: boolean, if True, the simulation will be continued
        :return: boolean, True if the building fits the requirements, False if it does not
        """
        # Building is in the list of buildings to simulate or the list is empty
        condition_1 = ((
                               building_id_list is None or building_id_list is []) or building_obj.id in building_id_list)
        # Building is a BuildingModeled and is a target
        condition_2 = isinstance(building_obj, BuildingModeled) and building_obj.is_target
        # The annual irradiance of the building were computed
        condition_2 = condition_2 and (
                building_obj.solar_radiation_and_bipv_simulation_obj.roof_annual_panel_irradiance_list is not None or \
                building_obj.solar_radiation_and_bipv_simulation_obj.facades_annual_panel_irradiance_list is not None)
        # The simulationm for this building is ongoing
        condition_3 = condition_2 and (
                building_obj.solar_radiation_and_bipv_simulation_obj.parameter_dict["roof"][
                    "start_year"] is not None or \
                building_obj.solar_radiation_and_bipv_simulation_obj.parameter_dict["facades"][
                    "start_year"] is not None)

        return (condition_1 and condition_2) or (
                condition_2 and condition_3 and continue_simulation)

    def compute_bipv_kpis_at_urban_scale(self, path_simulation_folder, bipv_scenario_identifier,
                                         grid_ghg_intensity, grid_energy_intensity,
                                         grid_electricity_sell_price, zone_area):
        """
        Post-process the BIPV results at urban scale
        :param path_simulation_folder: string, path to the simulation folder
        :param bipv_scenario_identifier: string, identifier of the BIPV scenario
        :param grid_ghg_intensity: float, kgCO2/kWh, grid GHG intensity
        :param grid_energy_intensity: float, kWh/m2, grid energy intensity
        :param grid_electricity_sell_price: float, €/kWh, grid electricity sell price

        :param zone_area: float, m2, area of the zone

        """

        bipv_scenario_obj = self.bipv_scenario_dict[bipv_scenario_identifier]

        ubes_electricity_consumption = sum(self.get_ubes_electricity_consumption_from_building_id_list(
            bipv_scenario_obj.bipv_simulated_building_id_list))

        conditioned_apartment_area = sum(
            self.get_conditioned_area_from_building_id_list(
                bipv_scenario_obj.bipv_simulated_building_id_list))
        # Set the grid parameters
        bipv_scenario_obj.compute_scenario_kpis(
            grid_ghg_intensity=grid_ghg_intensity,
            grid_energy_intensity=grid_energy_intensity,
            grid_electricity_sell_price=grid_electricity_sell_price,
            ubes_electricity_consumption=ubes_electricity_consumption,
            conditioned_apartment_area=conditioned_apartment_area,
            zone_area=zone_area)
        # Write the results to CSV file
        path_radiation_and_bipv_result_folder = os.path.join(path_simulation_folder,
                                                             name_radiation_simulation_folder)
        bipv_scenario_obj.write_kpis_to_csv(
            path_radiation_and_bipv_result_folder=path_radiation_and_bipv_result_folder)

    def get_list_of_bipv_simulated_buildings(self):
        """
        Get the list of buildings for which the BIPV simulation was run
        """
        building_list = []
        for building_id, building_obj in self.building_dict.items():
            if isinstance(building_obj, BuildingModeled) and building_obj.is_target \
                    and (building_obj.solar_radiation_and_bipv_simulation_obj.parameter_dict["roof"][
                             "start_year"] is not None or
                         building_obj.solar_radiation_and_bipv_simulation_obj.parameter_dict["facades"][
                             "start_year"] is not None):
                building_list.append(building_id)
        return building_list

    def get_ubes_electricity_consumption_from_building_id_list(self, building_id_list):
        """
        Get the energy consumption of buildings (if the energy simulation was run)
        :param building_id_list: list of building id
        """
        energy_consumption = []
        for building_id in building_id_list:
            building_obj = self.building_dict[building_id]
            energy_consumption.append(building_obj.get_bes_energy_consumption())

        return energy_consumption

    def get_conditioned_area_from_building_id_list(self, building_id_list):
        """
        Get the total conditioned area of the buildings
        :param building_id_list: list of building id
        """
        conditioned_area = []
        for building_id in building_id_list:
            building_obj = self.building_dict[building_id]
            conditioned_area.append(building_obj.get_conditioned_area())

        return conditioned_area

    # def plot_graphs_buildings(self, path_simulation_folder, study_duration_years, country_ghe_cost):
    #     for building in self.building_dict.values():
    #         if type(building) is BuildingModeled and building.is_target:
    #             if building.results_panels["roof"] and building.results_panels["facades"] and \
    #                     building.results_panels[
    #                         "Total"]:
    #                 path_simulation_folder_building = os.path.join(path_simulation_folder,
    #                                                                name_radiation_simulation_folder,
    #                                                                building.id)
    #                 building.plot_panels_energy_results(path_simulation_folder_building, study_duration_years)
    #                 building.plot_panels_ghg_results(path_simulation_folder_building, study_duration_years,
    #                                                  country_ghe_cost)
    #                 building.plot_panels_results_ghe_per_kwh(path_simulation_folder_building,
    #                                                          study_duration_years)
    #                 building.plot_panels_results_eroi(path_simulation_folder_building, study_duration_years)
    #
    # def plot_graphs_urban_canopy(self, path_simulation_folder, study_duration_years, country_ghe_cost):
    #
    #     energy_data = UrbanCanopyAdditionalFunction.get_energy_data_from_all_buildings(self.building_dict)
    #     carbon_data = UrbanCanopyAdditionalFunction.get_carbon_data_from_all_buildings(self.building_dict,
    #                                                                                    country_ghe_cost)
    #
    #     cum_energy_harvested_roof_uc, cum_energy_harvested_facades_uc, cum_energy_harvested_total_uc = \
    #         energy_data[0], \
    #             energy_data[1], energy_data[2]
    #     cum_primary_energy_roof_uc, cum_primary_energy_facades_uc, cum_primary_energy_total_uc = energy_data[
    #         3], \
    #         energy_data[4], energy_data[5]
    #
    #     cum_avoided_carbon_emissions_roof_uc, cum_avoided_carbon_emissions_facades_uc, \
    #         cum_avoided_carbon_emissions_total_uc = carbon_data[0], carbon_data[1], carbon_data[2]
    #     cum_carbon_emissions_roof_uc, cum_carbon_emissions_facades_uc, cum_carbon_emissions_total_uc = \
    #         carbon_data[3], \
    #             carbon_data[4], carbon_data[5]
    #
    #     years = list(range(study_duration_years))
    #
    #     UrbanCanopyAdditionalFunction.plot_energy_results_uc(path_simulation_folder, years,
    #                                                          cum_energy_harvested_roof_uc,
    #                                                          cum_energy_harvested_facades_uc,
    #                                                          cum_energy_harvested_total_uc,
    #                                                          cum_primary_energy_roof_uc,
    #                                                          cum_primary_energy_facades_uc,
    #                                                          cum_primary_energy_total_uc)
    #
    #     UrbanCanopyAdditionalFunction.plot_carbon_results_uc(path_simulation_folder, years,
    #                                                          cum_avoided_carbon_emissions_roof_uc,
    #                                                          cum_avoided_carbon_emissions_facades_uc,
    #                                                          cum_avoided_carbon_emissions_total_uc,
    #                                                          cum_carbon_emissions_roof_uc,
    #                                                          cum_carbon_emissions_facades_uc,
    #                                                          cum_carbon_emissions_total_uc)
    #
    #     UrbanCanopyAdditionalFunction.plot_ghe_per_kwh_uc(path_simulation_folder, years,
    #                                                       cum_energy_harvested_total_uc,
    #                                                       cum_carbon_emissions_total_uc)
    #
    #     UrbanCanopyAdditionalFunction.plot_results_eroi_uc(path_simulation_folder, years,
    #                                                        cum_primary_energy_total_uc,
    #                                                        cum_energy_harvested_total_uc)
