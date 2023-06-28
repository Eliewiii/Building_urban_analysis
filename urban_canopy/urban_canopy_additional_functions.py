"""
Additional functions used by Urban canopy
"""

from mains_tool.utils_general import *
from urban_canopy.utils_urban_canopy import *
from libraries_addons.solar_panels.useful_functions_solar_panel import write_to_csv_arr


class UrbanCanopyAdditionalFunction:

    @classmethod
    def add_hb_model_of_urban_canopy_envelop_to_json_dict(cls, json_dict, building_dict):
        """
            todo @Elie, change it, so that it is writen in the json file
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
                json_dict["buildings"][building_id]["HB_room_envelop"] = HB_room_dict
            elif type(building_object) is BuildingModeled:
                HB_room_dict = building_object.export_building_to_elevated_HB_room_envelop().to_dict()
                json_dict["buildings"][building_id]["HB_room_envelop"] = HB_room_dict
                # at this stage of the simulation, the HB has already been turned into a dict (to avoid locked class
                # issue)
                json_dict["buildings"][building_id]["HB_model"] = building_object.HB_model_dict

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
    def add_panel_attributes_to_json_dict(json_dict, building_dict):

        for building_id, building_object in building_dict.items():
            if type(building_object) is BuildingModeled:
                json_dict["buildings"][building_id]["Solar_radiation"]["Panels_results"]["Roof"] = \
                    building_object.results_panels["Roof"]
                json_dict["buildings"][building_id]["Solar_radiation"]["Panels_results"]["Facades"] = \
                    building_object.results_panels["Facades"]
                json_dict["buildings"][building_id]["Solar_radiation"]["Panels_results"]["Total"] = \
                    building_object.results_panels["Total"]

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

    @staticmethod
    def write_to_csv_panels_simulation_results(json_dict, building_dict, path_folder_simulation):
        # todo change names lca energy/lca carbon ?
        for building_id, building_object in building_dict.items():
            path_folder_building = os.path.join(path_folder_simulation, default_name_radiation_simulation_folder,
                                                building_id)
            path_folder_panels_results_csv = os.path.join(path_folder_building, "panels_simulation_results.csv")
            header = ["energy_produced_roof (kWh)", "energy_produced_facades (kWh)", "energy_produced_total (kWh)",
                      "primary_energy_roof (kWh)", "primary_energy_facades (kWh)", "primary_energy_total (kWh)",
                      "gh_gas_emissions_manufacturing_roof (kgCO2eq)",
                      "gh_gas_emissions_manufacturing_facades (kgCO2eq)",
                      "gh_gas_emissions_manufacturing_total (kgCO2eq)",
                      "dmfa_roof (kg)", "dmfa_facades (kg)", "dmfa_total (kg)", "energy_end_of_life_roof (kWh)",
                      "energy_end_of_life_facades (kWh)", "energy_end_of_life_total (kWh)"]
            list1 = \
                json_dict["buildings"][building_id]["Solar_radiation"]["Panels_results"]["Roof"]["energy_produced"][
                    "list"]
            list2 = \
                json_dict["buildings"][building_id]["Solar_radiation"]["Panels_results"]["Facades"]["energy_produced"][
                    "list"]
            list3 = \
                json_dict["buildings"][building_id]["Solar_radiation"]["Panels_results"]["Total"]["energy_produced"][
                    "list"]
            list4 = json_dict["buildings"][building_id]["Solar_radiation"]["Panels_results"]["Roof"]["lca_craddle_to_installation_energy"][
                "list"]
            list5 = json_dict["buildings"][building_id]["Solar_radiation"]["Panels_results"]["Facades"]["lca_craddle_to_installation_energy"][
                "list"]
            list6 = json_dict["buildings"][building_id]["Solar_radiation"]["Panels_results"]["Total"]["lca_craddle_to_installation_energy"][
                "list"]
            list7 = json_dict["buildings"][building_id]["Solar_radiation"]["Panels_results"]["Roof"]["lca_craddle_to_installation_carbon"][
                "list"]
            list8 = json_dict["buildings"][building_id]["Solar_radiation"]["Panels_results"]["Facades"]["lca_craddle_to_installation_carbon"][
                "list"]
            list9 = json_dict["buildings"][building_id]["Solar_radiation"]["Panels_results"]["Total"]["lca_craddle_to_installation_carbon"][
                "list"]
            list10 = json_dict["buildings"][building_id]["Solar_radiation"]["Panels_results"]["Roof"]["dmfa"]["list"]
            list11 = json_dict["buildings"][building_id]["Solar_radiation"]["Panels_results"]["Facades"]["dmfa"][
                "list"]
            list12 = json_dict["buildings"][building_id]["Solar_radiation"]["Panels_results"]["Total"]["dmfa"]["list"]
            list13 = \
                json_dict["buildings"][building_id]["Solar_radiation"]["Panels_results"]["Roof"]["lca_recycling_energy"][
                    "list"]
            list14 = \
                json_dict["buildings"][building_id]["Solar_radiation"]["Panels_results"]["Facades"]["lca_recycling_energy"][
                    "list"]
            list15 = \
                json_dict["buildings"][building_id]["Solar_radiation"]["Panels_results"]["Total"]["lca_recycling_energy"][
                    "list"]

            array = numpy.transpose(
                [list1, list2, list3, list4, list5, list6, list7, list8, list9, list10, list11, list12, list13, list14,
                 list15])

            write_to_csv_arr(header, array, path_folder_panels_results_csv)
