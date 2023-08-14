"""
Contains all the functions to export the data of an urban canopy object to json files.
"""

import os
import copy

from building.building_basic import BuildingBasic
from building.building_modeled import BuildingModeled

# Tree structure of the urban canopy json file
tree_structure_urban_canopy_json_dict = {
    "name": None,
    "buildings": {},
    "list_of_building_ids": [],

}

# Tree structure for each building
tree_structure_per_building_urban_canopy_json_dict = {
    # General attributes
    "index_in_gis": None,
    "height": None,
    "age": None,
    "typology": None,
    "lb_polyface3d_extruded_footprint": None,
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
        "facade_sensorgrid": None,
        "roof_result_dict": None,
        "facades_result_dict": None,
        "total": None,
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
    def init_urban_canopy_json_dict(urban_canopy_obj):
        """ Initialize the json dictionary of the urban canopy object. """
        urban_canopy_obj.json_dict = copy.deepcopy(tree_structure_urban_canopy_json_dict)

    @staticmethod
    def init_buildings_in_json_dict(urban_canopy_obj):
        """
        Initialize the buildings in the json dictionary of the urban canopy object.
        """
        for building_id in urban_canopy_obj.building_dict.keys():
            urban_canopy_obj.building_dict["list_of_building_ids"].append(building_id)
            urban_canopy_obj.building_dict["buildings"][building_id] = copy.deepcopy(
                tree_structure_per_building_urban_canopy_json_dict)

    @staticmethod
    def add_building_attributes_to_json_dict(urban_canopy_obj):
        """ Add the attributes of the building to the json dictionary of the urban canopy object. """
        for building_id, building_obj in urban_canopy_obj.building_dict.items():
            urban_canopy_obj.json_dict["buildings"][building_id]["index_in_gis"] = building_obj.index_in_gis
            urban_canopy_obj.json_dict["buildings"][building_id]["height"] = building_obj.height
            urban_canopy_obj.json_dict["buildings"][building_id]["age"] = building_obj.age
            urban_canopy_obj.json_dict["buildings"][building_id]["typology"] = building_obj.typology
            urban_canopy_obj.json_dict["buildings"][building_id][
                "lb_polyface3d_extruded_footprint"] = building_obj.lb_polyface3d_extruded_footprint

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
                urban_canopy_obj.json_dict["buildings"][building_id]["solar_radiation_and_bipv"]["parameters"] = \
                    building_obj.solar_radiation_and_bipv_simulation_obj.parameter_dict
                urban_canopy_obj.json_dict["buildings"][building_id]["solar_radiation_and_bipv"]["roof_sensorgrid"] = \
                    building_obj.solar_radiation_and_bipv_simulation_obj.roof_sensorgrid_dict
                urban_canopy_obj.json_dict["buildings"][building_id]["solar_radiation_and_bipv"]["facade_sensorgrid"] = \
                    building_obj.solar_radiation_and_bipv_simulation_obj.facade_sensorgrid_dict
                urban_canopy_obj.json_dict["buildings"][building_id]["solar_radiation_and_bipv"]["roof_result_dict"] = \
                    building_obj.solar_radiation_and_bipv_simulation_obj.results_dict["roof"]
                urban_canopy_obj.json_dict["buildings"][building_id]["solar_radiation_and_bipv"]["facades_result_dict"] = \
                    building_obj.solar_radiation_and_bipv_simulation_obj.results_dict["facades"]
                urban_canopy_obj.json_dict["buildings"][building_id]["solar_radiation_and_bipv"]["total"] = \
                    building_obj.solar_radiation_and_bipv_simulation_obj.results_dict["total"]
