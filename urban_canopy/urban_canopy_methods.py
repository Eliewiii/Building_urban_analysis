"""
Urban canopy class, containing and managing collections of buildings in urban areas.
"""

from mains_tool.utils_general import *
#from mains_tool.utils_general import default_minimum_vf_criterion_context_filter_first_pass_shading
from urban_canopy.utils_urban_canopy import *

class UrbanCanopy:

    def __init__(self):
        """Initialize the Urban Canopy"""
        self.building_dict = {}  # dictionary of the buildings in the urban canopy
        self.typology_dict = {}  # dictionary of the typologies loaded the urban canopy
        self.moving_vector_to_origin = None # moving vector of the urban canopy that moved the urban canopy to the origin

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
            urban_canopy = pickle.load(pkl_file) #TODO can we define urban_canopy as table?
            # Load the buildings objects that might have some properties stored into dict (ex HB_models)
            urban_canopy.load_building_HB_attributes()
        return urban_canopy

    def export_urban_canopy_to_pkl(self, path_folder):
        """ Save the urban canopy to a pickle file """
        with open(os.path.join(path_folder, "urban_canopy.pkl"), 'wb') as pkl_file:
            # todo
            self.pickle_building_HB_attributes()
            # todo
            pickle.dump(self, pkl_file)

    def export_urban_canopy_to_pkl_and_json(self, path_folder):
        """ Save the urban canopy to a pickle file """
        # PKL file
        # Turn certain attribute HB objects into dictionary to enable pickling (see the function)
        self.pickle_building_HB_attributes()
        # Write pkl file
        with open(os.path.join(path_folder, "urban_canopy.pkl"), 'wb') as pkl_file:
            pickle.dump(self, pkl_file)

        # Json file
        urban_canopy_dict = self.json_urban_canopy_attributes(path_folder)
        # Write json file
        with open(os.path.join(path_folder, "urban_canopy.json"), 'w') as json_file:
            json.dump(urban_canopy_dict, json_file)

    def load_typologies(self, typology_folder_path):
        """ Load the typologies from the folder
         :param typo_folder_path: path to the folder containing the typologies
         :return: None
         """

        # todo : to improve @Sharon
        # get the list of all the typology from the typology folder
        typology_folders_list = os.listdir(typology_folder_path)
        # loop through the typology folders list
        for typology in typology_folders_list:
            path_to_typology = os.path.join(typology_folder_path, typology)  # path to the given typology
            typology_obj = Typology.from_json(path_to_typology)  # make typology object from the json file in the folder
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
                if building.sensor_grid_dict['Roof'] is not None and building.sensor_grid_dict['Facades'] is not None:
                    path_building_roof_values = os.path.join(path_building, 'Roof', 'annual_radiation_values.txt')
                    path_building_facades_values = os.path.join(path_building, 'Facades', 'annual_radiation_values.txt')
                    building_attributes_dict = {'SensorGrid_dict': building.sensor_grid_dict,
                                                'HB_model_dict': building.HB_model_dict,
                                                'path_values_roof': path_building_roof_values,
                                                'path_values_facades': path_building_facades_values}

                elif building.sensor_grid_dict['Roof'] is not None and building.sensor_grid_dict['Facades'] is None:
                    path_building_roof_values = os.path.join(path_building, 'Roof', 'annual_radiation_values.txt')
                    building_attributes_dict = {'SensorGrid_dict': building.sensor_grid_dict,
                                                'HB_model_dict': building.HB_model_dict,
                                                'path_values_roof': path_building_roof_values,
                                                'path_values_facades': None}

                elif building.sensor_grid_dict['Roof'] is None and building.sensor_grid_dict['Facades'] is not None:
                    path_building_facades_values = os.path.join(path_building, 'Facades', 'annual_radiation_values.txt')
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
            logging.warning("The building id {building_id} is already in the urban canopy, "
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
                                          additional_gis_attribute_key_dict=None):
        """ Extract the data from a shp file and create the associated buildings objects"""
        # Read GIS file
        shape_file = extract_gis(path_gis)

        # Check if the building_id_key_gis is an attribute in the shape file other - set it to None,
        # and the building will automatically be assigned an id
        try:
            shape_file[building_id_key_gis]
        except KeyError:
            logging.error("The key {building_id_key_gis} is not an attribute of the shape file, the id will be generated automatically")

            raise
            building_id_key_gis = None

        ## loop to create a building_obj for each footprint in the shp file
        number_of_buildings_in_shp_file = len(shape_file['geometry'])
        for building_index_in_GIS in range(0, number_of_buildings_in_shp_file):
            # create the building object
            building_id_list, building_obj_list = BuildingBasic.make_buildingbasic_from_GIS(self, shape_file,
                                                                                            building_index_in_GIS,
                                                                                            building_id_key_gis, unit)
            # add the building to the urban canopy
            if building_obj_list is not None:
                self.add_list_of_buildings_to_dict(building_id_list, building_obj_list)

        # Collect the attributes to the buildings from the shp file
        for building in self.building_dict.values():
            building.extract_building_attributes_from_GIS(shape_file, additional_gis_attribute_key_dict)

    # todo : New, to test
    def add_buildings_from_hbjson_to_dict(self, path_directory_hbjson, are_buildings_targets=False):
        """ Add the buildings from the hb models in the folder
        :param path_directory_hbjson: path to the directory containing the hbjson files
        :return: None
        """
        # Get the list of the hbjson files
        hbjson_files_list = [hbjson_file for hbjson_file in os.listdir(path_directory_hbjson) if hbjson_file.endswith(".hbjson")]
        # Loop through the hbjson files
        if hbjson_files_list:
            for hbjson_file in hbjson_files_list:
                if os.path.getsize(os.path.join(path_directory_hbjson, hbjson_file)) > 0: # hbjson_file should be the fullpath of json
                    # Get the path to the hbjson file
                    path_hbjson = os.path.join(path_directory_hbjson, hbjson_file)
                    # Create the building object
                    building_HB_model_obj, identifier = BuildingModeled.make_buildingmodeled_from_hbjson(
                        path_hbjson=path_hbjson,is_target=are_buildings_targets)
                    # Add the building to the urban canopy
                    self.add_building_to_dict(identifier, building_HB_model_obj)
                else:
                    logging.info("The file is empty")
        # todo @Sharon or @Elie : check that the list of the building ids is not empty or invalid - done # try catch?
                    # todo: add a log in case it is not added!
        # Add the new buildings to the UrbanCanopy building dict

    def make_HB_model_envelops_from_buildings(self, path_folder=None):
        """ Make the hb model for the building envelop and save it to hbjson file if the path is provided """
        # List of the hb rooms representing the building envelops
        # HB_room_envelop_list = [building.export_building_to_elevated_HB_room_envelop() for building in self.building_dict.values()] todo:to delete if it works
        HB_room_envelop_list = []  # Initialize the list
        for building in self.building_dict.values():
            if type(building) is BuildingBasic:  # Make an HB room by extruding the footprint
                HB_room_envelop_list.append(building.export_building_to_elevated_HB_room_envelop())
            elif type(building) is BuildingModeled:  # Extract the rooms from the HB model attribute of the building
                for HB_room in building.HB_model_obj.rooms:
                    HB_room_envelop_list.append(HB_room)
        # additional cleaning of the colinear vertices, might not be necessary
        for room in HB_room_envelop_list:
            room.remove_colinear_vertices_envelope(tolerance = self.tolerance_default_value, delete_degenerate=True)
        # Make the hb model
        HB_model = Model(identifier="urban_canopy_building_envelops", rooms=HB_room_envelop_list, tolerance=self.tolerance_default_value)
        HB_dict = HB_model.to_dict()
        if path_folder is not None:
            HB_model.to_hbjson(name="buildings_envelops", folder=path_folder)
        return HB_dict, HB_model

    def make_oriented_bounding_boxes_of_buildings(self, path_folder=None, hbjson_name=None):
        """ Make the oriented bounding boxes of the buildings in the urban canopy
        and save it to hbjson file if the path is provided """
        for building in self.building_dict.values():
            building.make_LB_polyface3d_oriented_bounding_box()
        if path_folder is not None:
            # List of the hb rooms representing the building envelops
            bounding_boxes_HB_room_list = [
                Room.from_polyface3d(identifier=str(building.id), polyface=building.LB_polyface3d_oriented_bounding_box) for building in
                self.building_dict.values()]
            HB_model = Model(identifier="urban_canopy_bounding_boxes", rooms=bounding_boxes_HB_room_list,
                             tolerance = self.tolerance_default_value)
            HB_model.to_hbjson(name=hbjson_name, folder=path_folder)

    def perform_context_filtering_for_shading_on_buildingmodeled_to_simulate(self,minimum_vf_criterion=default_minimum_vf_criterion_context_filter_first_pass_shading):
        """
        Perform the context filtering on the BuildingModeled objects in the urban canopy that need to be simulated.

        """
        # todo @Elie: to adapt from old code

        #todo @ Sharon and @Elie: speed up this part LATER by preparing making some preprocessing (centroid of faces, height etc...)

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
                building_obj.select_context_surfaces_for_shading_computation(context_building_list=list_of_all_buildings,minimum_vf_criterion=minimum_vf_criterion)

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
            logging.info("The urban canopy has already been moved to the origin, the building will be moved back and"
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

    def radiation_simulation_urban_canopy(self, path_folder_simulation, path_weather_file, list_id=None, grid_size=1,
                                          offset_dist=0.1, on_roof=True, on_facades=True):
        for building in self.building_dict.values():  # for every building in the urban canopy
            if list_id is None:
                if type(building) is BuildingModeled and building.is_target:
                    path_folder_building = os.path.join(path_folder_simulation, building.id)
                    if on_roof and on_facades:
                        # we run the radiation simulation on all the roofs of the buildings within the urban canopy
                        values_roof = building.solar_radiations(str(building.id), path_folder_building,
                                                                path_weather_file, grid_size, offset_dist,
                                                                on_facades=False)
                        name_file = os.path.join(path_folder_building, 'Roof', 'annual_radiation_values.txt')
                        file = open(name_file, 'w')
                        tmp = (','.join(str(n) for n in values_roof[0]))
                        file.write('{}'.format(tmp))
                        file.close()
                        # then we run it on all the facades of the buildings within the urban canopy
                        values_facades = building.solar_radiations(str(building.id), path_folder_building,
                                                                   path_weather_file, grid_size, offset_dist,
                                                                   on_roof=False)
                        name_file = os.path.join(path_folder_building, 'Facades', 'annual_radiation_values.txt')
                        file = open(name_file, 'w')
                        tmp = (','.join(str(n) for n in values_facades[0]))
                        file.write('{}'.format(tmp))
                        file.close()
                    elif on_roof and not on_facades:
                        # we only run the radiation simulation on the facades of the buildings
                        values_roof = building.solar_radiations(str(building.id), path_folder_building,
                                                                path_weather_file, grid_size, offset_dist,
                                                                on_facades=False)
                        name_file = os.path.join(path_folder_building, 'Roof', 'annual_radiation_values.txt')
                        file = open(name_file, 'w')
                        tmp = (','.join(str(n) for n in values_roof[0]))
                        file.write('{}'.format(tmp))
                        file.close()
                    elif on_facades and not on_roof:
                        # we only run the radiation simulation on the facades of the buildings
                        values_facades = building.solar_radiations(str(building.id), path_folder_building,
                                                                   path_weather_file, grid_size, offset_dist,
                                                                   on_roof=False)
                        name_file = os.path.join(path_folder_building, 'Facades', 'annual_radiation_values.txt')
                        file = open(name_file, 'w')
                        tmp = (','.join(str(n) for n in values_facades[0]))
                        file.write('{}'.format(tmp))
                        file.close()
            else:
                if type(building) is BuildingModeled and building.id in list_id:
                    path_folder_building = os.path.join(path_folder_simulation, building.id)
                    if on_roof and on_facades:
                        # we run the radiation simulation on all the roofs of the buildings within the urban canopy
                        values_roof = building.solar_radiations(str(building.id), path_folder_building, path_weather_file,
                                                                grid_size, offset_dist, on_facades=False)
                        name_file = os.path.join(path_folder_building, 'Roof', 'annual_radiation_values.txt')
                        file = open(name_file, 'w')
                        tmp = (','.join(str(n) for n in values_roof[0]))
                        file.write('{}'.format(tmp))
                        file.close()
                        # then we run it on all the facades of the buildings within the urban canopy
                        values_facades = building.solar_radiations(str(building.id), path_folder_building, path_weather_file
                                                                   , grid_size, offset_dist, on_roof=False)
                        name_file = os.path.join(path_folder_building, 'Facades', 'annual_radiation_values.txt')
                        file = open(name_file, 'w')
                        tmp = (','.join(str(n) for n in values_facades[0]))
                        file.write('{}'.format(tmp))
                        file.close()
                    elif on_roof and not on_facades:
                        # we only run the radiation simulation on the facades of the buildings
                        values_roof = building.solar_radiations(str(building.id), path_folder_building, path_weather_file,
                                                                grid_size,
                                                                offset_dist, on_facades=False)
                        name_file = os.path.join(path_folder_building, 'Roof', 'annual_radiation_values.txt')
                        file = open(name_file, 'w')
                        tmp = (','.join(str(n) for n in values_roof[0]))
                        file.write('{}'.format(tmp))
                        file.close()
                    elif on_facades and not on_roof:
                        # we only run the radiation simulation on the facades of the buildings
                        values_facades = building.solar_radiations(str(building.id), path_folder_building, path_weather_file
                                                                   , grid_size, offset_dist, on_roof=False)
                        name_file = os.path.join(path_folder_building, 'Facades', 'annual_radiation_values.txt')
                        file = open(name_file, 'w')
                        tmp = (','.join(str(n) for n in values_facades[0]))
                        file.write('{}'.format(tmp))
                        file.close()
            print("Another radiation simulation was done")

    def post_processing_urban_canopy(self, path_folder_simulation):
        for building in self.building_dict.values():  # for every building in the urban canopy
            # if type(building) is BuildingModeled and building.is_target:
            if type(building) is BuildingModeled:
                path_building = os.path.join(path_folder_simulation, building.id)
                building.post_process(path_building)

    def get_list_id_buildings_urban_canopy(self, path_folder):
        path_json = os.path.join(path_folder, 'urban_canopy.json')
        if os.path.isfile(path_json):
            f = open(path_json)
            urban_canopy_dictionary = json.load(f)
            list_id = urban_canopy_dictionary["list_id_buildings"]
        else:
            list_id = []
            for building in self.building_dict.values():  # for every building in the urban canopy
                if type(building) is BuildingModeled:
                    list_id.append(building.id)
        return list_id
