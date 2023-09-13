"""
Urban canopy class, containing and managing collections of buildings in urban areas.
"""
import os
import pickle
import json
import logging

from honeybee.model import Model

from urban_canopy.urban_canopy_additional_functions import UrbanCanopyAdditionalFunction
from urban_canopy.export_to_json import ExportUrbanCanopyToJson

from building.building_basic import BuildingBasic
from building.building_modeled import BuildingModeled
from libraries_addons.extract_gis_files import extract_gis
from typology.typology import Typology
from bipv.bipv_technology import BipvTechnology

from utils.utils_configuration import name_urban_canopy_export_file_pkl, name_urban_canopy_export_file_json, \
    name_radiation_simulation_folder
from utils.utils_constants import TOLERANCE_LBT

from utils.utils_default_values_user_parameters import default_path_weather_file

dev_logger = logging.getLogger("dev")
user_logger = logging.getLogger("user")


class UrbanCanopy:

    def __init__(self):
        """Initialize the Urban Canopy"""
        self.building_dict = {}  # dictionary of the buildings in the urban canopy
        self.typology_dict = {}  # dictionary of the typologies loaded the urban canopy
        self.moving_vector_to_origin = None  # moving vector of the urban canopy that moved the urban canopy to the origin
        self.json_dict = {}  # dictionary containing relevant attributes of the urban canopy to be exported to json

    def __len__(self):
        """ Return the number of buildings in the urban canopy """
        return len(self.building_dict)

    @classmethod
    def make_urban_canopy_from_pkl(cls, path_pkl):
        """ Load the urban canopy from a pickle file """
        with open(path_pkl, 'rb') as pkl_file:
            # Load pickle file
            urban_canopy_object = pickle.load(pkl_file)  # TODO can we define urban_canopy as table?
            # Load the buildings objects that might have some properties stored into dict (ex HB_models)
            urban_canopy_object.load_building_HB_attributes()
            # Reinitialize the json dictionary
            urban_canopy_object.reinitialize_json_dict()

        return urban_canopy_object

    def to_pkl(self, path_simulation_folder):
        """ Save the urban canopy to a pickle file """
        # Turn certain attribute HB objects into dictionary to enable pickling (see the function)
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

    # todo @Elie : to be removed
    # def to_json(self, path_simulation_folder):
    #     """ Save the urban canopy to a pickle json """
    #     # Transform the data from the urban canopy in the json dictionary
    #     self.write_json_dictionary(path_simulation_folder=path_simulation_folder)
    #     # Write json file
    #     with open(os.path.join(path_simulation_folder, name_urban_canopy_export_file_json), 'w') as json_file:
    #         json.dump(self.json_dict, json_file)

    def reinitialize_json_dict(self):
        """
        Reinitialize the json dict
        Not 100% necessary as te dictionary is written after the urban canopy is pickled, but some of
        """
        self.json_dict = {}

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
        # todo @Elie: here there is only one function that works for any type of building, but maybe we will
        # todo.cont: have to make a specific function for each type of building (like this it's simpler but maybe more confusing)
        # it is depend in the the action - it is better to have one method if all the functions purpose is the same
        # if not how can we separarte the building type into groups and then decide what is unique for each group
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
        else:
            # add the building to the urban canopy
            self.building_dict[building_id] = building_obj

    def add_list_of_buildings_to_dict(self, building_id_list, building_obj_list):
        """ Add a list of buildings to the urban canopy"""
        # TODO the "i" describe the building type? building name? buikding number? index_building_id_list
        for i, building_id in enumerate(building_id_list):
            building_obj = building_obj_list[i]
            self.add_building_to_dict(building_id, building_obj)

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

        # Check if the building_id_key_gis is an attribute in the shape file other - set it to None,
        # and the building will automatically be assigned an id
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
                additional_gis_attribute_key_dict = load_additional_gis_attribute_key_dict(
                    path_additional_gis_attribute_key_dict)
            else:
                additional_gis_attribute_key_dict = None
        else:
            additional_gis_attribute_key_dict = None

        ## loop to create a building_obj for each footprint in the shp file
        number_of_buildings_in_shp_file = len(shape_file['geometry'])
        for building_index_in_gis in range(0, number_of_buildings_in_shp_file):
            # create the building object
            building_id_list, building_obj_list = BuildingBasic.make_buildingbasic_from_GIS(self, shape_file,
                                                                                            building_index_in_gis,
                                                                                            building_id_key_gis,
                                                                                            unit)
            # add the building to the urban canopy
            if building_obj_list is not None:
                self.add_list_of_buildings_to_dict(building_id_list, building_obj_list)

        # Collect the attributes to the buildings from the shp file
        for building in self.building_dict.values():
            building.extract_building_attributes_from_GIS(shape_file, additional_gis_attribute_key_dict)

    # todo : New, to test
    def add_buildings_from_hbjson_to_dict(self, path_directory_hbjson=None, path_file_hbjson=None,
                                          are_buildings_targets=False):
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
                    path_hbjson=hbjson_file_path, is_target=are_buildings_targets)
                # Add the building to the urban canopy
                self.add_building_to_dict(identifier, building_HB_model_obj)
            else:
                logging.info("The file {} is empty".format(hbjson_file_path))

    def add_hb_model_envelop_to_json_dict(self):
        """

        :return:
        """
        UrbanCanopyAdditionalFunction.add_hb_model_of_urban_canopy_envelop_to_json_dict(
            json_dict=self.json_dict,
            building_dict=self.building_dict)

    # todo : to delete, it is useless

    def make_HB_model_envelops_from_buildings(self, path_folder=None):
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

    def make_oriented_bounding_boxes_of_buildings(self, overwrite=False):
        """ Make the oriented bounding boxes of the buildings in the urban canopy
        and save it to hbjson file if the path is provided """
        for building in self.building_dict.values():
            building.make_LB_polyface3d_oriented_bounding_box(overwrite=overwrite)

    def initialize_shading_context_obj_of_buildings_to_simulate(self, min_VF_criterion, number_of_rays):
        """
        Initialize the shading context object of the buildings to simulate
        :param min_VF_criterion: float, the minimum view factor criterion
        :param number_of_rays: int, the number of rays to be used for raytracing to the shading context
        """
        for building_obj in self.building_dict.values():
            if building_obj.to_simulate:
                building_obj.initialize_shading_context_obj()

    def perform_first_pass_context_filtering_on_buildings(self, building_id_list=None,
                                                          on_building_to_simulate=True):
        """
        Perform the first pass context filtering on the BuildingModeled objects in the urban canopy that need to be simulated.
        :param building_id_list: list of str, the list of building id to perform the first pass context filtering on.
        :param on_building_to_simulate: bool, if True, perform the first pass context filtering on the buildings to simulate.
        :return:
        """
        context_building_id_list = []  # Initialize the list
        # todo @Elie, make bounding boxes of all buildings if not done yet
        self.make_oriented_bounding_boxes_of_buildings()
        # if we specify the building no need to do it on all the simulated buildings
        if building_id_list is not None and building_id_list != []:
            on_building_to_simulate = False
        # Loop over the buildings
        for i, (building_id, building_obj) in enumerate(self.building_dict.items()):
            if (on_building_to_simulate and building_obj.to_simulate) or building_id in building_id_list:
                context_building_id_list += building_obj.perform_first_pass_context_filtering(
                    building_dictionary=self.building_dict)

        return context_building_id_list

    def convert_list_of_buildings_to_BuildingModeled(self, building_id_list_to_convert_to_BuildingModeled,
                                                     automatic_floor_subdivision=False,
                                                     layout_from_typology=False,
                                                     properties_from_typology=False,
                                                     are_target=False, are_simulated=False):
        """
        Convert the buildings to BuildingModeled
        :param building_id_list_to_convert_to_BuildingModeled: list of str, the list of building id to convert to BuildingModeled
        :param automatic_floor_subdivision: bool, if True, perform the automatic floor subdivision
        :param layout_from_typology: bool, if True, use the layout from the typology
        :param properties_from_typology: bool, if True, use the properties from the typology
        :param are_target: bool, if True, the buildings are target
        :param are_simulated: bool, if True, the buildings are simulated
        :return:
        """
        # Convert the buildings to BuildingModeled
        for building_id in building_id_list_to_convert_to_BuildingModeled:
            building_obj = self.building_dict[building_id]
            self.building_dict[building_id] = BuildingModeled.convert_building_to_BuildingModeled(
                building_obj=building_obj, is_target=are_target, is_simulated=are_simulated,
                layout_from_typology=layout_from_typology,
                automatic_floor_subdivision=automatic_floor_subdivision,
                properties_from_typology=properties_from_typology)

    def perform_context_filtering_for_shading_on_buildingmodeled_to_simulate(self, minimum_vf_criterion):
        """
        Perform the context filtering on the BuildingModeled objects in the urban canopy that need to be simulated.

        """
        # todo @Elie: to adapt from old code

        # todo @ Sharon and @Elie: speed up this part LATER by preparing making some preprocessing (centroid of faces, height etc...)

        # Make bounding boxes and extruded footprint if they don't exist already
        # todo @Elie: can be put in a separate function
        for building_obj in self.building_dict.values():
            # by default the functions don't overwrite the existing attribute if it exist already
            building_obj.make_lb_polyface3d_extruded_footprint()
            building_obj.make_LB_polyface3d_oriented_bounding_box()

        # Make a Pyvista mesh containing all the surfaces of all the buildings in the urban canopy
        # todo @Elie : make the mesh, only once for all the buildings

        # Loop through the buildings in the urban canopy
        for building_obj in self.building_dict.values():
            if isinstance(building_obj, BuildingModeled) and building_obj.to_simulate:
                list_of_all_buildings = list(self.building_dict.values())
                building_obj.select_context_surfaces_for_shading_computation(
                    context_building_list=list_of_all_buildings, minimum_vf_criterion=minimum_vf_criterion)

    def make_Pyvista_Polydata_mesh_of_all_buildings(self):
        """

        :return:
        """
        # todo @Elie: test the function
        # Make list of all the LB_Polyface3D_extruded_footprint of the buildings in the urban canopy
        list_of_building_LB_Polyface3D_extruded_footprint = [building.lb_polyface3d_extruded_footprint for
                                                             building in
                                                             self.building_dict.values()]
        # Convert to Pyvista Polydata
        # todo @Elie: add the mport and finish the function
        # Pyvista_Polydata_mesh = make_Pyvista_Polydata_from_LB_Polyface3D_list(list_of_building_LB_Polyface3D_extruded_footprint)

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
                                                north_angle=0):
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
                    north_angle=north_angle)

    def generate_sensor_grid_on_buildings(self, building_id_list=None, bipv_on_roof=True,
                                          bipv_on_facades=True, roof_grid_size_x=1,
                                          facades_grid_size_x=1,
                                          roof_grid_size_y=1, facades_grid_size_y=1, offset_dist=0.1):
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
                                                  offset_dist=offset_dist)

    def run_annual_solar_irradiance_simulation_on_buildings(self, path_simulation_folder,
                                                            building_id_list=None,
                                                            path_epw_file=default_path_weather_file,
                                                            overwrite=False, north_angle=0, silent=False):
        """
        Run the solar radiation simulation for the buildings in the urban canopy.
        :param building_id_list: list of the building id to run the simulation, if None or empty list, all the target
        :param path_simulation_folder: string, path to the folder where the simulation will be performed.
        :param path_epw_file: string, path to the weather file.
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
                    and isinstance(building_obj, BuildingModeled) and building_obj.is_target :
                building_obj.run_annual_solar_irradiance_simulation(
                    path_simulation_folder=path_simulation_folder,
                    path_epw_file=path_epw_file,
                    overwrite=overwrite,
                    north_angle=north_angle, silent=silent)

    def run_bipv_panel_simulation_on_buildings(self, path_simulation_folder, path_pv_tech_dictionary_json,
                                               building_id_list, roof_id_pv_tech, facades_id_pv_tech,
                                               efficiency_computation_method="yearly", minimum_panel_eroi=1.2,
                                               study_duration_in_years=50,
                                               replacement_scenario="replace_failed_panels_every_X_years",
                                               **kwargs):
        """
        Run the panels simulation on the urban canopy
        :param path_simulation_folder: path to the simulation folder
        :param path_pv_tech_dictionary_json: path to the json dictionary containing all PVPanelTechnology objects
        :param id_pv_tech_roof: string: id of the roof technology used, default = "mitrex_roof c-Si"
        :param id_pv_tech_facades: string: id of the facades technology used, default = "metsolar_facades c-Si"
        :param minimum_ratio_energy_harvested_on_primary_energy: int: production minimal during the first year for a panel to be installed at
        this position, Default0.5 kWh
        :param performance_ratio: float: performance ratio of the PV, Default=0.75
        :param study_duration_in_years: integer: duration of the study in years, default = 50
        :param replacement_scenario: string: scenario of replacements for the panels, default = 'yearly'
        """

        # todo: check ifg the file exist and put a default value
        pv_technologies_dictionary = BipvTechnology.load_pv_technologies_from_json_to_dictionary(
            path_pv_tech_dictionary_json)

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

        for building_obj in self.building_dict.values():
            if ((building_id_list is None or building_id_list is []) or building_obj.id in building_id_list) \
                    and isinstance(building_obj, BuildingModeled) and building_obj.is_target \
                    and building_obj.solar_radiation_and_bipv_simulation_obj is not None and (
                    self.building_dict[
                        building_id].solar_radiation_and_bipv_simulation_obj.roof_annual_panel_irradiance_list is not None or \
                    self.building_dict[
                        building_id].solar_radiation_and_bipv_simulation_obj.facades_annual_panel_irradiance_list is not None):
                # Run the BIPV simulation
                building_obj.run_bipv_panel_simulation(path_simulation_folder=path_simulation_folder,
                                                       pv_technologies_dictionary=pv_technologies_dictionary,
                                                       roof_id_pv_tech=roof_id_pv_tech,
                                                       facades_id_pv_tech=facades_id_pv_tech,
                                                       efficiency_computation_method=efficiency_computation_method,
                                                       minimum_panel_eroi=minimum_panel_eroi,
                                                       study_duration_in_years=study_duration_in_years,
                                                       replacement_scenario=replacement_scenario,
                                                       **kwargs)

    def post_process_bipv_results_at_urban_scale(self, path_simulation_folder, building_id_list):
        """

        """

    def plot_graphs_buildings(self, path_simulation_folder, study_duration_years, country_ghe_cost):
        for building in self.building_dict.values():
            if type(building) is BuildingModeled and building.is_target:
                if building.results_panels["roof"] and building.results_panels["facades"] and \
                        building.results_panels[
                            "Total"]:
                    path_simulation_folder_building = os.path.join(path_simulation_folder,
                                                                   name_radiation_simulation_folder,
                                                                   building.id)
                    building.plot_panels_energy_results(path_simulation_folder_building, study_duration_years)
                    building.plot_panels_ghg_results(path_simulation_folder_building, study_duration_years,
                                                     country_ghe_cost)
                    building.plot_panels_results_ghe_per_kwh(path_simulation_folder_building,
                                                             study_duration_years)
                    building.plot_panels_results_eroi(path_simulation_folder_building, study_duration_years)

    def plot_graphs_urban_canopy(self, path_simulation_folder, study_duration_years, country_ghe_cost):

        energy_data = UrbanCanopyAdditionalFunction.get_energy_data_from_all_buildings(self.building_dict)
        carbon_data = UrbanCanopyAdditionalFunction.get_carbon_data_from_all_buildings(self.building_dict,
                                                                                       country_ghe_cost)

        cum_energy_harvested_roof_uc, cum_energy_harvested_facades_uc, cum_energy_harvested_total_uc = \
            energy_data[0], \
                energy_data[1], energy_data[2]
        cum_primary_energy_roof_uc, cum_primary_energy_facades_uc, cum_primary_energy_total_uc = energy_data[
            3], \
            energy_data[4], energy_data[5]

        cum_avoided_carbon_emissions_roof_uc, cum_avoided_carbon_emissions_facades_uc, \
            cum_avoided_carbon_emissions_total_uc = carbon_data[0], carbon_data[1], carbon_data[2]
        cum_carbon_emissions_roof_uc, cum_carbon_emissions_facades_uc, cum_carbon_emissions_total_uc = \
            carbon_data[3], \
                carbon_data[4], carbon_data[5]

        years = list(range(study_duration_years))

        UrbanCanopyAdditionalFunction.plot_energy_results_uc(path_simulation_folder, years,
                                                             cum_energy_harvested_roof_uc,
                                                             cum_energy_harvested_facades_uc,
                                                             cum_energy_harvested_total_uc,
                                                             cum_primary_energy_roof_uc,
                                                             cum_primary_energy_facades_uc,
                                                             cum_primary_energy_total_uc)

        UrbanCanopyAdditionalFunction.plot_carbon_results_uc(path_simulation_folder, years,
                                                             cum_avoided_carbon_emissions_roof_uc,
                                                             cum_avoided_carbon_emissions_facades_uc,
                                                             cum_avoided_carbon_emissions_total_uc,
                                                             cum_carbon_emissions_roof_uc,
                                                             cum_carbon_emissions_facades_uc,
                                                             cum_carbon_emissions_total_uc)

        UrbanCanopyAdditionalFunction.plot_ghe_per_kwh_uc(path_simulation_folder, years,
                                                          cum_energy_harvested_total_uc,
                                                          cum_carbon_emissions_total_uc)

        UrbanCanopyAdditionalFunction.plot_results_eroi_uc(path_simulation_folder, years,
                                                           cum_primary_energy_total_uc,
                                                           cum_energy_harvested_total_uc)
