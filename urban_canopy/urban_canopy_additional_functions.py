"""
Additional functions used by Urban canopy
"""

from mains_tool.utils_general import *
from urban_canopy.utils_urban_canopy import *


class UrbanCanopyAdditionalFunction:

    @classmethod
    def add_hb_model_of_urban_canopy_envelop_to_json_dict(cls, json_dict, building_dict):
        """
            todo @Elie, change it, so tha it is writen in the json file
        """
        # Generate the HB model for the building envelops and convert it to dict
        building_envelops_hb_dict = cls.make_HB_model_dict_envelops_from_buildings(building_dict)
        # Add the HB model to the json dict
        json_dict["hb_model_of_urban_canopy_envelop"] = building_envelops_hb_dict

    @staticmethod
    def add_buildings_and_list_of_buildings_to_json_dict(json_dict, building_dict):
        """
        todo @Elie
        """
        # Initialize empty dictionary for the buildings
        building_id_dict = {}
        # Get the list of building ids
        building_id_list = list(building_dict.keys())
        for building_id in building_id_list:
            # Initialize empty dictionary for each building
            building_id_dict[building_id] = copy.deepcopy(default_tree_structure_per_building_urban_canopy_json_dict)

        # write the result on the json dict
        json_dict["buildings"] = building_id_dict
        json_dict["list_of_buildings"] = building_id_list

    @staticmethod
    def add_building_HB_models_and_envelop_to_json_dict(json_dict, building_dict):
        """
        Add the HB model of each building to the json dict
        :param json_dict:
        :param building_dict:
        """
        for building_id, building_object in building_dict.items():
            # Differentiate between the two types of buildings
            if type(building_object) is BuildingBasic:
                HB_room_dict = building_object.export_building_to_elevated_HB_room_envelop().to_dict()
                json_dict["buildings"][building_id]["hb_room_envelop"] = HB_room_dict
            elif type(building_object) is BuildingModeled:
                HB_room_dict = building_object.export_building_to_elevated_HB_room_envelop().to_dict()
                json_dict["buildings"][building_id]["hb_room_envelop"] = HB_room_dict
                # at this stage of the simulation, the HB has already been turned into a dict (to avoid locked class issue)
                json_dict["buildings"][building_id]["HB_model"] = building_object.HB_model_dict()

    @staticmethod
    def add_building_attributes_to_json_dict(json_dict, building_dict):
        """
        todo @Elie
        :param json_dict:
        :param building_dict:
        :return:
        """
        for building_id, building_object in building_dict.items():
            json_dict["buildings"][building_id]["Age"] = building_object.age
            json_dict["buildings"][building_id]["Typology"] = building_object.typology

            if type(building_object) is BuildingModeled:
                json_dict["buildings"][building_id]["Is_target_building"] = building_object.is_target
                json_dict["buildings"][building_id]["Is_to_simulate"] = building_object.to_simulate




    @staticmethod
    def add_radiation_attributes_to_json_dict(json_dict, building_dict, path_folder_simulation):
        """
        todo @Elie
        Buildings were already added to the dictionary before this function is called
        :param json_dict:
        :param building_dict:
        :param path_folder_simulation:
        :return:
        """
        for building_id, building_object in building_dict.items():
            if type(building_object) is BuildingModeled:
                json_dict["buildings"][building_id]["Solar_radiation"][
                    "Sensor_grids_dict"] = building_object.sensor_grid_dict
                path_solar_radiation_folder = os.path.join(path_folder_simulation,
                                                           default_name_radiation_simulation_folder)
                if building_object.sensor_grid_dict["Roof"] is not None:
                    json_dict["buildings"][building_id]["Solar_radiation"]["Path_results"]["Annual"][
                        "Roof"] = os.path.join(path_solar_radiation_folder, building_id, "Roof",
                                               'annual_radiation_values.txt')
                    # todo @Hilany, add the timestep results
                    # json_dict["buildings"][building_id]["Solar_radiation"]["Path_results"]["Timestep"]["Roof"] =
                if building_object.sensor_grid_dict["Facades"] is not None:
                    json_dict["buildings"][building_id]["Solar_radiation"]["Path_results"]["Annual"][
                        "Facades"] = os.path.join(path_solar_radiation_folder, building_id, "Facades",
                                                  'annual_radiation_values.txt')
                    # todo @Hilany, add the timestep results
                    # json_dict["buildings"][building_id]["Solar_radiation"]["Path_results"]["Timestep"]["Facades"] =

    @staticmethod
    def make_HB_model_dict_envelops_from_buildings(building_dict):
        """ Make the hb model for the building envelop and save it to hbjson file if the path is provided """
        HB_room_envelop_list = []  # Initialize the list
        for building in building_dict.values():
            if type(building) is BuildingBasic:  # Make an HB room by extruding the footprint
                HB_room_envelop_list.append(building.export_building_to_elevated_HB_room_envelop())
            elif type(building) is BuildingModeled:  # Extract the rooms from the HB model attribute of the building
                for HB_room in building.HB_model_obj.rooms:
                    HB_room_envelop_list.append(HB_room)
        # additional cleaning of the colinear vertices, might not be necessary
        for room in HB_room_envelop_list:
            room.remove_colinear_vertices_envelope(tolerance=default_tolerance_value, delete_degenerate=True)
        # Make the hb model
        HB_model = Model(identifier="urban_canopy_building_envelops", rooms=HB_room_envelop_list,
                         tolerance=default_tolerance_value)
        HB_dict = HB_model.to_dict()

        return HB_dict
