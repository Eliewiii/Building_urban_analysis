"""
Contains all the functions to export the data of an urban canopy object to json files.
"""

import os
import copy

from honeybee.room import Room

from bipv.bipv_technology import BipvTechnology

from building.building_basic import BuildingBasic
from building.building_modeled import BuildingModeled

# Tree structure of the urban canopy json file
tree_structure_urban_canopy_json_dict = {
    "name": None,
    "buildings": {},
    "list_of_building_ids": [],
    "bipv_scenarios": {}
}

# Tree structure for each building
tree_structure_per_building_urban_canopy_json_dict = {
    # General attributes
    "index_in_gis": None,
    "height": None,
    "age": None,
    "typology": None,
    "hb_room_envelope": None,
    # BuildingModeled specific attributes
    "is_target_building": False,
    "is_building_to_simulate": False,
    "hb_model": None,
    "merged_faces_hb_model": None,
    "lb_polyface3d_oriented_bounding_box": None,
    "context_surfaces": {
        "parameters": {
            "first_pass_done": False,
            "second_pass_done": False,
            "min_vf_criterion": None,
            "number_of_rays": None,
            "consider_windows": None
        },
        "first_pass_selected_building_id_list": None,
        "second_pass_selected_hb_shade_list": None,
        "discarded_face3d_second_pass_list": None,
        "forced_shades_from_user": None
    },
    "solar_radiation_and_bipv": None
}


class ExportUrbanCanopyToJson:
    """
    Contains all the functions to format the data of an urban canopy object to be exported to json files.
    """

    @classmethod
    def make_urban_canopy_json_dict(cls, urban_canopy_obj):
        """ Make the dictionary of the urban canopy object to be exported to a json file. """

        # Initialize the json dictionary
        cls.init_json_dict(urban_canopy_obj)
        # Initialize the buildings in the json dictionary
        cls.init_buildings_in_json_dict(urban_canopy_obj)
        # Add the attributes of the building to the json dictionary
        cls.add_building_attributes_to_json_dict(urban_canopy_obj)
        # Add the building shades to the json dictionary
        cls.add_building_shades_to_json_dict(urban_canopy_obj)
        # Add the solar radiation and BIPV data to the json dictionary
        cls.add_solar_radiation_and_bipv_to_json_dict(urban_canopy_obj)
        # todo @Elie, add the other data when ready

    @staticmethod
    def init_json_dict(urban_canopy_obj):
        """ Initialize the json dictionary of the urban canopy object. """
        urban_canopy_obj.json_dict = copy.deepcopy(tree_structure_urban_canopy_json_dict)

    @staticmethod
    def init_buildings_in_json_dict(urban_canopy_obj):
        """
        Initialize the buildings in the json dictionary of the urban canopy object.
        """
        for building_id, building_obj in urban_canopy_obj.building_dict.items():
            urban_canopy_obj.json_dict["list_of_building_ids"].append(building_id)
            urban_canopy_obj.json_dict["buildings"][building_id] = building_obj.to_dict()

    @staticmethod
    def add_building_attributes_to_json_dict(urban_canopy_obj):
        """ Add the attributes of the building to the json dictionary of the urban canopy object. """
        for building_id, building_obj in urban_canopy_obj.building_dict.items():
            urban_canopy_obj.json_dict["buildings"][building_id]["index_in_gis"] = building_obj.index_in_gis
            urban_canopy_obj.json_dict["buildings"][building_id]["height"] = building_obj.height
            urban_canopy_obj.json_dict["buildings"][building_id]["age"] = building_obj.age
            urban_canopy_obj.json_dict["buildings"][building_id]["typology"] = building_obj.typology
            if building_obj.lb_polyface3d_extruded_footprint is None:
                building_obj.make_lb_polyface3d_extruded_footprint()
            building_hb_room_envelope_dict = Room.from_polyface3d(identifier=building_id,
                                                                  polyface=building_obj.lb_polyface3d_extruded_footprint).to_dict()
            urban_canopy_obj.json_dict["buildings"][building_id][
                "hb_room_envelope"] = building_hb_room_envelope_dict

            # Bounding box of the building, used for the context filtering
            if building_obj.lb_polyface3d_oriented_bounding_box is not None:
                urban_canopy_obj.json_dict["buildings"][building_id][
                    "lb_polyface3d_oriented_bounding_box"] = building_obj.lb_polyface3d_oriented_bounding_box.to_dict()

            if isinstance(building_obj, BuildingModeled):
                urban_canopy_obj.json_dict["buildings"][building_id][
                    "is_target_building"] = building_obj.is_target
                urban_canopy_obj.json_dict["buildings"][building_id][
                    "is_building_to_simulate"] = building_obj.to_simulate
                urban_canopy_obj.json_dict["buildings"][building_id]["hb_model"] = building_obj.hb_model_dict
                # HB model with merged faces of the building (used for the context filtering and the solar radiation)
                urban_canopy_obj.json_dict["buildings"][building_id][
                    "merged_faces_hb_model"] = building_obj.merged_faces_hb_model_dict

    @staticmethod
    def add_building_shades_to_json_dict(urban_canopy_obj):
        """ Add the context filtering results of the building to the json dictionary of the urban canopy object. """
        for building_id, building_obj in urban_canopy_obj.building_dict.items():
            if isinstance(building_obj, BuildingModeled):
                # List of the forced shades from the user
                # No need to convert the shades to dict, they are already in dict format after pickling
                urban_canopy_obj.json_dict["buildings"][building_id][
                    "context_surfaces"]["forced_shades_from_user"] = \
                    building_obj.shading_context_obj.forced_hb_shades_from_user_list
                if building_obj.shading_context_obj.first_pass_done:
                    # Ids of the selected context buildings from the first pass
                    urban_canopy_obj.json_dict["buildings"][building_id][
                        "context_surfaces"]["first_pass_selected_building_id_list"] = \
                        building_obj.shading_context_obj.selected_context_building_id_list
                    # parameters of the first pass
                    urban_canopy_obj.json_dict["buildings"][building_id][
                        "context_surfaces"]["parameters"]["first_pass_done"] = \
                        building_obj.shading_context_obj.first_pass_done
                    urban_canopy_obj.json_dict["buildings"][building_id][
                        "context_surfaces"]["parameters"]["min_vf_criterion"] = \
                        building_obj.shading_context_obj.min_vf_criterion
                if building_obj.shading_context_obj.second_pass_done:
                    # List of the selected context shades from the second pass
                    # No need to convert the shades to dict, they are already in dict format after pickling
                    urban_canopy_obj.json_dict["buildings"][building_id][
                        "context_surfaces"]["second_pass_selected_hb_shade_list"] = \
                        building_obj.shading_context_obj.context_shading_hb_shade_list
                    urban_canopy_obj.json_dict["buildings"][building_id][
                        "context_surfaces"]["discarded_face3d_second_pass_list"] = [face.to_dict() for face in
                                                                                    building_obj.shading_context_obj.discarded_lb_face3d_context_shading_second_pass_list]
                    # parameters of the second pass
                    urban_canopy_obj.json_dict["buildings"][building_id][
                        "context_surfaces"]["parameters"]["second_pass_done"] = \
                        building_obj.shading_context_obj.second_pass_done
                    urban_canopy_obj.json_dict["buildings"][building_id][
                        "context_surfaces"]["parameters"]["number_of_rays"] = \
                        building_obj.shading_context_obj.number_of_rays
                    urban_canopy_obj.json_dict["buildings"][building_id][
                        "context_surfaces"]["parameters"]["consider_windows"] = \
                        building_obj.shading_context_obj.consider_windows

    @staticmethod
    def add_solar_radiation_and_bipv_to_json_dict(urban_canopy_obj):
        """ Add the solar radiation and BIPV data to the json dictionary of the urban canopy object. """
        for building_id, building_obj in urban_canopy_obj.building_dict.items():
            if isinstance(building_obj, BuildingModeled) \
                    and building_obj.solar_radiation_and_bipv_simulation_obj is not None:
                # Paramters
                urban_canopy_obj.json_dict["buildings"][building_id][
                    "solar_radiation_and_bipv"] = building_obj.solar_radiation_and_bipv_simulation_obj.to_json_dict()

        # Add the results of the BIPV scenarios
        for scenario_id, scenario_obj in urban_canopy_obj.bipv_scenario_dict.items():
            urban_canopy_obj.json_dict["bipv_scenarios"][scenario_id] = scenario_obj.to_dict()

    @staticmethod
    def add_urban_canopy_bipv_scenarios(urban_canopy_obj):
        """ Add the BIPV scenarios of the urban canopy object to the json dictionary. """
        for scenario_id, scenario_obj in urban_canopy_obj.bipv_scenario_dict.items():
            urban_canopy_obj.json_dict["bipv_scenarios"][scenario_id] = scenario_obj.to_dict()

    @staticmethod
    def add_urban_canopy_ubes_obj_to_json_dict(urban_canopy_obj):
        """ Add the UBES object of the urban canopy object to the json dictionary. """
        urban_canopy_obj.json_dict["ubes"] = urban_canopy_obj.ubes_obj.to_dict()

#
# def replace_bipv_technology_obj_by_id(parameter_dict):
#     """
#     Replace the technology object by its id
#     :param parameter_dict: dict of the parameters
#     :return: dict of the parameters
#     """
#     for key, value in parameter_dict.items():
#         if isinstance(value, dict):
#             parameter_dict[key] = replace_bipv_technology_obj_by_id(value)
#         elif isinstance(value, list):
#             for i, v in enumerate(value):
#                 if isinstance(v, dict):
#                     value[i] = replace_bipv_technology_obj_by_id(v)
#         elif isinstance(value, BipvTechnology):
#             parameter_dict[key] = value.identifier
#
#     return parameter_dict
