"""
Urban canopy class, containing and managing collections of buildings in urban areas.
"""
import os
import pickle
import json
import logging

from honeybee.model import Model

from urban_canopy_pack.urban_canopy_additional_functions import UrbanCanopyAdditionalFunction

from building.building_basic import BuildingBasic
from building.building_modeled import BuildingModeled
from libraries_addons.extract_gis_files import extract_gis
from typology.typology import Typology
from solar_panel.pv_panel_technology import PvPanelTechnology

from utils.utils_configuration import name_urban_canopy_export_file_pkl, name_urban_canopy_export_file_json, \
    name_radiation_simulation_folder

dev_logger = logging.getLogger("dev")
user_logger = logging.getLogger("user")

class UrbanCanopy:

    def __init__(self):
        """Initialize the Urban Canopy"""
        self.building_dict = {}  # dictionary of the buildings in the urban canopy
        self.typology_dict = {}  # dictionary of the typologies loaded the urban canopy
        self.moving_vector_to_origin = None  # moving vector of the urban canopy that moved the urban canopy to the origin
        self.json_dict = {}  # dictionary containing relevant attributes of the urban canopy to be exported to json

        self.tolerance_default_value = 0.01  # todo : move this values to utils_general.py,
        # call it LBT_default_tolerance, it will be the same value for all the functions using LBT objects

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

    def export_urban_canopy_to_pkl(self, path_folder_simulation):
        """ Save the urban canopy to a pickle file """
        # Turn certain attribute HB objects into dictionary to enable pickling (see the function)
        self.pickle_building_HB_attributes()
        # Write pkl file
        with open(os.path.join(path_folder_simulation, name_urban_canopy_export_file_pkl), 'wb') as pkl_file:
            pickle.dump(self, pkl_file)

    def export_urban_canopy_to_json(self, path_folder_simulation):
        """ Save the urban canopy to a pickle json """
        # Transform the data from the urban canopy in the json dictionary
        self.write_json_dictionary(path_folder_simulation=path_folder_simulation)
        # Write json file
        with open(os.path.join(path_folder_simulation, name_urban_canopy_export_file_json), 'w') as json_file:
            json.dump(self.json_dict, json_file)

    def reinitialize_json_dict(self):
        """
        Reinitialize the json dict
        Not 100% necessary as te dictionary is written after the urban canopy is pickled, but some of
        """
        self.json_dict = {}

    def write_json_dictionary(self, path_folder_simulation):
        """ Create a dictionary which will contain certain useful attributes of the urban canopy and the buildings """
        # Add buildings and list of buildings to the json dictionary
        UrbanCanopyAdditionalFunction.add_buildings_and_list_of_buildings_to_json_dict(
            json_dict=self.json_dict,
            building_dict=self.building_dict)
        # Add building envelop and model (room)
        UrbanCanopyAdditionalFunction.add_building_HB_models_and_envelop_to_json_dict(
            json_dict=self.json_dict,
            building_dict=self.building_dict)
        # add the various attributes of the buildings to the json dictionary
        UrbanCanopyAdditionalFunction.add_building_attributes_to_json_dict(json_dict=self.json_dict,
                                                                           building_dict=self.building_dict)
        UrbanCanopyAdditionalFunction.add_radiation_attributes_to_json_dict(json_dict=self.json_dict,
                                                                            building_dict=self.building_dict,
                                                                            path_folder_simulation=path_folder_simulation)
        UrbanCanopyAdditionalFunction.add_panel_attributes_to_json_dict(json_dict=self.json_dict,
                                                                        building_dict=self.building_dict)

    def generate_building_envelop_and_add_it_to_json_dict(self):
        """"""
        UrbanCanopyAdditionalFunction.add_hb_model_of_urban_canopy_envelop_to_json_dict(
            json_dict=self.json_dict,
            building_dict=self.building_dict)

    def load_typologies(self, typology_folder_path):
        """ Load the typologies from the folder
         :param typology_folder_path: path to the folder containing the typologies
         :return: None
         """

        # todo : to improve @Sharon
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
        # todo @Elie or @Sharon: here there is only one function that works for any type of building, but maybe we will
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

    def json_urban_canopy_attributes(self, path_folder):
        """ Create a dictionary which will contain certain useful attributes of the urban canopy and the buildings"""
        list_id = self.get_list_id_buildings_urban_canopy(path_folder)
        urban_canopy_attributes_dict = {'list_id_buildings': list_id, 'buildings': {}}
        for building in self.building_dict.values():
            if type(building) is BuildingModeled:
                path_building = os.path.join(path_folder, 'Radiation Simulation', building.id)
                if building.sensor_grid_dict['Roof'] is not None and building.sensor_grid_dict[
                    'Facades'] is not None:
                    path_building_roof_values = os.path.join(path_building, 'Roof',
                                                             'annual_radiation_values.txt')
                    path_building_facades_values = os.path.join(path_building, 'Facades',
                                                                'annual_radiation_values.txt')
                    building_attributes_dict = {'SensorGrid_dict': building.sensor_grid_dict,
                                                'HB_model_dict': building.HB_model_dict,
                                                'path_values_roof': path_building_roof_values,
                                                'path_values_facades': path_building_facades_values}

                elif building.sensor_grid_dict['Roof'] is not None and building.sensor_grid_dict[
                    'Facades'] is None:
                    path_building_roof_values = os.path.join(path_building, 'Roof',
                                                             'annual_radiation_values.txt')
                    building_attributes_dict = {'SensorGrid_dict': building.sensor_grid_dict,
                                                'HB_model_dict': building.HB_model_dict,
                                                'path_values_roof': path_building_roof_values,
                                                'path_values_facades': None}

                elif building.sensor_grid_dict['Roof'] is None and building.sensor_grid_dict[
                    'Facades'] is not None:
                    path_building_facades_values = os.path.join(path_building, 'Facades',
                                                                'annual_radiation_values.txt')
                    building_attributes_dict = {'SensorGrid_dict': building.sensor_grid_dict,
                                                'HB_model_dict': building.HB_model_dict,
                                                'path_values_roof': None,
                                                'path_values_facades': path_building_facades_values}

                else:
                    building_attributes_dict = {'SensorGrid_dict': building.sensor_grid_dict,
                                                'HB_model_dict': building.HB_model_dict,
                                                'path_values_roof': None,
                                                'path_values_facades': None}
                urban_canopy_attributes_dict['buildings'][building.id] = building_attributes_dict
        return urban_canopy_attributes_dict

    def add_building_to_dict(self, building_id, building_obj):
        """ Add a building to the urban canopy"""
        # check if the building id is already in the urban canopy
        if building_id in self.building_dict.keys():
            user_logger.warning("The building id {building_id} is already in the urban canopy, "
                            "it will not be added again to the urban canopy".format(building_id=building_id))
            dev_logger.warning("The building id {building_id} is already in the urban canopy, "
                            "it will not be added again to the urban canopy".format(building_id=building_id))
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
        for building_index_in_GIS in range(0, number_of_buildings_in_shp_file):
            # create the building object
            building_id_list, building_obj_list = BuildingBasic.make_buildingbasic_from_GIS(self, shape_file,
                                                                                            building_index_in_GIS,
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
                for HB_room in building.HB_model_obj.rooms:
                    HB_room_envelop_list.append(HB_room)
        # additional cleaning of the colinear vertices, might not be necessary
        for room in HB_room_envelop_list:
            room.remove_colinear_vertices_envelope(tolerance=self.tolerance_default_value,
                                                   delete_degenerate=True)
        # Make the hb model
        HB_model = Model(identifier="urban_canopy_building_envelops", rooms=HB_room_envelop_list,
                         tolerance=self.tolerance_default_value)
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
        # todo @Elie or @Sharon: can be put in a separate function
        for building_obj in self.building_dict.values():
            # by default the functions don't overwrite the existing attribute if it exist already
            building_obj.make_LB_polyface3d_extruded_footprint()
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
        list_of_building_LB_Polyface3D_extruded_footprint = [building.LB_polyface3d_extruded_footprint for
                                                             building in
                                                             self.building_dict.values()]
        # Convert to Pyvista Polydata
        # todo @Elie: add the mport and finish the function
        # Pyvista_Polydata_mesh = make_Pyvista_Polydata_from_LB_Polyface3D_list(list_of_building_LB_Polyface3D_extruded_footprint)

    def compute_moving_vector_to_origin(self):
        """ Make the moving vector to move the urban canopy to the origin """
        # get the center of mass (Point3D) of the urban canopy on the x,y plane
        list_of_centroid = [building.LB_face_footprint.centroid for building in self.building_dict.values()]
        center_of_mass_x = sum([centroid.x for centroid in list_of_centroid]) / len(list_of_centroid)
        center_of_mass_y = sum([centroid.y for centroid in list_of_centroid]) / len(list_of_centroid)
        # Find the minimum elevation of the buildings in the urban canopy
        # The elevation of all building will be rebased considering the minimum elevation to be z=0
        min_elevation = min([building.elevation for building in self.building_dict.values()])
        self.moving_vector_to_origin = [-center_of_mass_x, -center_of_mass_y, -min_elevation]

    def move_buildings_to_origin(self):
        """ Move the buildings to the origin if the the urban canopy has not already been moved to the origin"""
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

    def radiation_simulation_urban_canopy(self, path_folder_simulation, path_weather_file, list_id, grid_size,
                                          offset_dist, on_roof, on_facades):
        path_folder_radiation_simulation = os.path.join(path_folder_simulation,
                                                        name_radiation_simulation_folder)
        for building in self.building_dict.values():  # for every building in the urban canopy
            if list_id is None:
                if type(building) is BuildingModeled and building.is_target:
                    path_folder_building = os.path.join(path_folder_radiation_simulation, building.id)
                    if on_roof and on_facades:
                        # we run the radiation simulation on all the roofs of the buildings within the urban canopy
                        values_roof = building.solar_radiations(str(building.id), path_folder_building,
                                                                path_weather_file, grid_size, offset_dist,
                                                                on_facades=False)
                        name_file = os.path.join(path_folder_building, 'Roof', 'annual_radiation_values.txt')
                        with open(name_file, 'w') as f:
                            tmp = (','.join(str(n) for n in values_roof[0]))
                            f.write('{}'.format(tmp))
                        # then we run it on all the facades of the buildings within the urban canopy
                        values_facades = building.solar_radiations(str(building.id), path_folder_building,
                                                                   path_weather_file, grid_size, offset_dist,
                                                                   on_roof=False)
                        name_file = os.path.join(path_folder_building, 'Facades',
                                                 'annual_radiation_values.txt')
                        with open(name_file, 'w') as f:
                            tmp = (','.join(str(n) for n in values_facades[0]))
                            f.write('{}'.format(tmp))
                    elif on_roof and not on_facades:
                        # we only run the radiation simulation on the facades of the buildings
                        values_roof = building.solar_radiations(str(building.id), path_folder_building,
                                                                path_weather_file, grid_size, offset_dist,
                                                                on_facades=False)
                        name_file = os.path.join(path_folder_building, 'Roof', 'annual_radiation_values.txt')
                        with open(name_file, 'w') as f:
                            tmp = (','.join(str(n) for n in values_roof[0]))
                            f.write('{}'.format(tmp))
                    elif on_facades and not on_roof:
                        # we only run the radiation simulation on the facades of the buildings
                        values_facades = building.solar_radiations(str(building.id), path_folder_building,
                                                                   path_weather_file, grid_size, offset_dist,
                                                                   on_roof=False)
                        name_file = os.path.join(path_folder_building, 'Facades',
                                                 'annual_radiation_values.txt')
                        with open(name_file, 'w') as f:
                            tmp = (','.join(str(n) for n in values_facades[0]))
                            f.write('{}'.format(tmp))
            else:
                if type(building) is BuildingModeled and building.id in list_id:
                    path_folder_building = os.path.join(path_folder_radiation_simulation, building.id)
                    if on_roof and on_facades:
                        # we run the radiation simulation on all the roofs of the buildings within the urban canopy
                        values_roof = building.solar_radiations(str(building.id), path_folder_building,
                                                                path_weather_file,
                                                                grid_size, offset_dist, on_facades=False)
                        name_file = os.path.join(path_folder_building, 'Roof', 'annual_radiation_values.txt')
                        with open(name_file, 'w') as f:
                            tmp = (','.join(str(n) for n in values_roof[0]))
                            f.write('{}'.format(tmp))
                        # then we run it on all the facades of the buildings within the urban canopy
                        values_facades = building.solar_radiations(str(building.id), path_folder_building,
                                                                   path_weather_file
                                                                   , grid_size, offset_dist, on_roof=False)
                        name_file = os.path.join(path_folder_building, 'Facades',
                                                 'annual_radiation_values.txt')
                        with open(name_file, 'w') as f:
                            tmp = (','.join(str(n) for n in values_facades[0]))
                            f.write('{}'.format(tmp))
                    elif on_roof and not on_facades:
                        # we only run the radiation simulation on the facades of the buildings
                        values_roof = building.solar_radiations(str(building.id), path_folder_building,
                                                                path_weather_file,
                                                                grid_size,
                                                                offset_dist, on_facades=False)
                        name_file = os.path.join(path_folder_building, 'Roof', 'annual_radiation_values.txt')
                        with open(name_file, 'w') as f:
                            tmp = (','.join(str(n) for n in values_roof[0]))
                            f.write('{}'.format(tmp))
                    elif on_facades and not on_roof:
                        # we only run the radiation simulation on the facades of the buildings
                        values_facades = building.solar_radiations(str(building.id), path_folder_building,
                                                                   path_weather_file
                                                                   , grid_size, offset_dist, on_roof=False)
                        name_file = os.path.join(path_folder_building, 'Facades',
                                                 'annual_radiation_values.txt')
                        with open(name_file, 'w') as f:
                            tmp = (','.join(str(n) for n in values_facades[0]))
                            f.write('{}'.format(tmp))
                print("Another radiation simulation was done")

    def get_list_id_buildings_urban_canopy(self, path_folder):
        path_json = os.path.join(path_folder, 'urban_canopy.json')
        if os.path.isfile(path_json):
            with open(path_json) as f:
                urban_canopy_dictionary = json.load(f)
                list_id = urban_canopy_dictionary["list_id_buildings"]
        else:
            list_id = []
            for building in self.building_dict.values():  # for every building in the urban canopy
                if type(building) is BuildingModeled:
                    list_id.append(building.id)
        return list_id

    def run_panel_simulation(self, path_folder_simulation, path_pv_tech_dictionary_json, id_pv_tech_roof,
                             id_pv_tech_facades, minimum_ratio_energy_harvested_on_primary_energy,
                             performance_ratio,
                             study_duration_in_years,
                             replacement_scenario, **kwargs):
        """
        Run the panels simulation on the urban canopy
        :param path_folder_simulation: path to the simulation folder
        :param path_pv_tech_dictionary_json: path to the json dictionary containing all PVPanelTechnology objects
        :param id_pv_tech_roof: string: id of the roof technology used, default = "mitrex_roof c-Si"
        :param id_pv_tech_facades: string: id of the facade technology used, default = "metsolar_facades c-Si"
        :param minimum_ratio_energy_harvested_on_primary_energy: int: production minimal during the first year for a panel to be installed at
        this position, Default0.5 kWh
        :param performance_ratio: float: performance ratio of the PV, Default=0.75
        :param study_duration_in_years: integer: duration of the study in years, default = 50
        :param replacement_scenario: string: scenario of replacements for the panels, default = 'yearly'
        """

        pv_tech_dictionary = PvPanelTechnology.load_pv_technologies_from_json_to_dictionary(path_pv_tech_dictionary_json)

        for building in self.building_dict.values():  # for every building in the urban canopy
            if type(building) is BuildingModeled and building.is_target:
                path_folder_building = os.path.join(path_folder_simulation,
                                                    name_radiation_simulation_folder,
                                                    building.id)
                building.panel_simulation_building(path_folder_building, pv_tech_dictionary, id_pv_tech_roof,
                                                   id_pv_tech_facades,
                                                   minimum_ratio_energy_harvested_on_primary_energy,
                                                   performance_ratio,
                                                   study_duration_in_years, replacement_scenario, **kwargs)

    def plot_graphs_buildings(self, path_folder_simulation, study_duration_years, country_ghe_cost):
        for building in self.building_dict.values():
            if type(building) is BuildingModeled and building.is_target:
                if building.results_panels["Roof"] and building.results_panels["Facades"] and building.results_panels["Total"]:
                    path_folder_simulation_building = os.path.join(path_folder_simulation,
                                                                   name_radiation_simulation_folder,
                                                                   building.id)
                    building.plot_panels_energy_results(path_folder_simulation_building, study_duration_years)
                    building.plot_panels_ghg_results(path_folder_simulation_building, study_duration_years,
                                                     country_ghe_cost)
                    building.plot_panels_results_ghe_per_kwh(path_folder_simulation_building,
                                                             study_duration_years)
                    building.plot_panels_results_eroi(path_folder_simulation_building, study_duration_years)

    def plot_graphs_urban_canopy(self, path_folder_simulation, study_duration_years, country_ghe_cost):

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

        UrbanCanopyAdditionalFunction.plot_energy_results_uc(path_folder_simulation, years,
                                                             cum_energy_harvested_roof_uc,
                                                             cum_energy_harvested_facades_uc,
                                                             cum_energy_harvested_total_uc,
                                                             cum_primary_energy_roof_uc,
                                                             cum_primary_energy_facades_uc,
                                                             cum_primary_energy_total_uc)

        UrbanCanopyAdditionalFunction.plot_carbon_results_uc(path_folder_simulation, years,
                                                             cum_avoided_carbon_emissions_roof_uc,
                                                             cum_avoided_carbon_emissions_facades_uc,
                                                             cum_avoided_carbon_emissions_total_uc,
                                                             cum_carbon_emissions_roof_uc,
                                                             cum_carbon_emissions_facades_uc,
                                                             cum_carbon_emissions_total_uc)

        UrbanCanopyAdditionalFunction.plot_ghe_per_kwh_uc(path_folder_simulation, years,
                                                          cum_energy_harvested_total_uc,
                                                          cum_carbon_emissions_total_uc)

        UrbanCanopyAdditionalFunction.plot_results_eroi_uc(path_folder_simulation, years,
                                                           cum_primary_energy_total_uc,
                                                           cum_energy_harvested_total_uc)
