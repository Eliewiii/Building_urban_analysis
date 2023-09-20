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
    "list_of_building_ids": []
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
    "context_surfaces": {
        "First_pass_filter": {},
        "Second_pass_filter": {}
    },
    "solar_radiation_and_bipv": {
        "parameters": None,
        "roof_sensorgrid": None,
        "facades_sensorgrid": None,
        "roof_annual_panel_irradiance_list": None,
        "facades_annual_panel_irradiance_list": None,
        "roof_panel_mesh_index_list": None,
        "facades_panel_mesh_index_list": None,
        "roof_result_dict": None,
        "facades_result_dict": None,
        "total_result_dict": None
    }
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
        for building_id in urban_canopy_obj.building_dict.keys():
            urban_canopy_obj.json_dict["list_of_building_ids"].append(building_id)
            urban_canopy_obj.json_dict["buildings"][building_id] = copy.deepcopy(
                tree_structure_per_building_urban_canopy_json_dict)

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

            if isinstance(building_obj, BuildingModeled):
                urban_canopy_obj.json_dict["buildings"][building_id][
                    "is_target_building"] = building_obj.is_target
                urban_canopy_obj.json_dict["buildings"][building_id][
                    "is_building_to_simulate"] = building_obj.to_simulate
                urban_canopy_obj.json_dict["buildings"][building_id]["hb_model"] = building_obj.hb_model_dict
                urban_canopy_obj.json_dict["buildings"][building_id][
                    "merged_faces_hb_model"] = building_obj.merged_faces_hb_model_dict

    @staticmethod
    def add_solar_radiation_and_bipv_to_json_dict(urban_canopy_obj):
        """ Add the solar radiation and BIPV data to the json dictionary of the urban canopy object. """
        for building_id, building_obj in urban_canopy_obj.building_dict.items():
            if isinstance(building_obj, BuildingModeled) \
                    and building_obj.solar_radiation_and_bipv_simulation_obj is not None:
                # Paramters
                urban_canopy_obj.json_dict["buildings"][building_id]["solar_radiation_and_bipv"][
                    "parameters"] = \
                    replace_bipv_technology_obj_by_id(
                        building_obj.solar_radiation_and_bipv_simulation_obj.parameter_dict)

                # Mesh/Sensorgrid
                urban_canopy_obj.json_dict["buildings"][building_id]["solar_radiation_and_bipv"][
                    "roof_sensorgrid"] = \
                    building_obj.solar_radiation_and_bipv_simulation_obj.roof_sensorgrid_dict
                urban_canopy_obj.json_dict["buildings"][building_id]["solar_radiation_and_bipv"][
                    "facades_sensorgrid"] = \
                    building_obj.solar_radiation_and_bipv_simulation_obj.facades_sensorgrid_dict
                # Results solar irradiance
                urban_canopy_obj.json_dict["buildings"][building_id]["solar_radiation_and_bipv"][
                    "roof_annual_panel_irradiance_list"] = \
                    building_obj.solar_radiation_and_bipv_simulation_obj.roof_annual_panel_irradiance_list
                urban_canopy_obj.json_dict["buildings"][building_id]["solar_radiation_and_bipv"][
                    "facades_annual_panel_irradiance_list"] = \
                    building_obj.solar_radiation_and_bipv_simulation_obj.facades_annual_panel_irradiance_list
                # Index of panels kept in the mesh
                if building_obj.solar_radiation_and_bipv_simulation_obj.roof_panel_list is not None:
                    urban_canopy_obj.json_dict["buildings"][building_id]["solar_radiation_and_bipv"][
                        "roof_panel_mesh_index_list"] = [panel.index for panel in
                                                         building_obj.solar_radiation_and_bipv_simulation_obj.roof_panel_list]
                if building_obj.solar_radiation_and_bipv_simulation_obj.facades_panel_list is not None:
                    urban_canopy_obj.json_dict["buildings"][building_id]["solar_radiation_and_bipv"][
                        "facades_panel_mesh_index_list"] = [panel.index for panel in
                                                         building_obj.solar_radiation_and_bipv_simulation_obj.facades_panel_list]
                # Results BIPV
                urban_canopy_obj.json_dict["buildings"][building_id]["solar_radiation_and_bipv"][
                    "roof_result_dict"] = \
                    building_obj.solar_radiation_and_bipv_simulation_obj.bipv_results_dict["roof"]
                urban_canopy_obj.json_dict["buildings"][building_id]["solar_radiation_and_bipv"][
                    "facades_result_dict"] = \
                    building_obj.solar_radiation_and_bipv_simulation_obj.bipv_results_dict["facades"]
                urban_canopy_obj.json_dict["buildings"][building_id]["solar_radiation_and_bipv"][
                    "total_result_dict"] = \
                    building_obj.solar_radiation_and_bipv_simulation_obj.bipv_results_dict["total"]


def replace_bipv_technology_obj_by_id(parameter_dict):
    """
    Replace the technology object by its id
    :param parameter_dict: dict of the parameters
    :return: dict of the parameters
    """
    for key, value in parameter_dict.items():
        if isinstance(value, dict):
            parameter_dict[key] = replace_bipv_technology_obj_by_id(value)
        elif isinstance(value, list):
            for i, v in enumerate(value):
                if isinstance(v, dict):
                    value[i] = replace_bipv_technology_obj_by_id(v)
        elif isinstance(value, BipvTechnology):
            parameter_dict[key] = value.identifier

    return parameter_dict