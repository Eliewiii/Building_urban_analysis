"""
Additional functions used by Urban canopy
"""

from mains_tool.utils_general import *
from urban_canopy_pack.utils_urban_canopy import *
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
            header = ["energy_harvested_roof (kWh)", "energy_harvested_facades (kWh)", "energy_harvested_total (kWh)",
                      "primary_energy_roof (kWh)", "primary_energy_facades (kWh)", "primary_energy_total (kWh)",
                      "gh_gas_emissions_manufacturing_roof (kgCO2eq)",
                      "gh_gas_emissions_manufacturing_facades (kgCO2eq)",
                      "gh_gas_emissions_manufacturing_total (kgCO2eq)",
                      "dmfa_roof (kg)", "dmfa_facades (kg)", "dmfa_total (kg)", "energy_end_of_life_roof (kWh)",
                      "energy_end_of_life_facades (kWh)", "energy_end_of_life_total (kWh)",
                      "carbon_end_of_life_roof (kgCO2eq)", "carbon_end_of_life_facades (kgCO2eq)",
                      "carbon_end_of_life_total (kgCO2eq)"]
            list1 = \
                json_dict["buildings"][building_id]["Solar_radiation"]["Panels_results"]["Roof"]["energy_harvested"][
                    "list"]
            list2 = \
                json_dict["buildings"][building_id]["Solar_radiation"]["Panels_results"]["Facades"]["energy_harvested"][
                    "list"]
            list3 = \
                json_dict["buildings"][building_id]["Solar_radiation"]["Panels_results"]["Total"]["energy_harvested"][
                    "list"]
            list4 = json_dict["buildings"][building_id]["Solar_radiation"]["Panels_results"]["Roof"][
                "lca_craddle_to_installation_primary_energy"][
                "list"]
            list5 = json_dict["buildings"][building_id]["Solar_radiation"]["Panels_results"]["Facades"][
                "lca_craddle_to_installation_primary_energy"][
                "list"]
            list6 = json_dict["buildings"][building_id]["Solar_radiation"]["Panels_results"]["Total"][
                "lca_craddle_to_installation_primary_energy"][
                "list"]
            list7 = json_dict["buildings"][building_id]["Solar_radiation"]["Panels_results"]["Roof"][
                "lca_craddle_to_installation_carbon"][
                "list"]
            list8 = json_dict["buildings"][building_id]["Solar_radiation"]["Panels_results"]["Facades"][
                "lca_craddle_to_installation_carbon"][
                "list"]
            list9 = json_dict["buildings"][building_id]["Solar_radiation"]["Panels_results"]["Total"][
                "lca_craddle_to_installation_carbon"][
                "list"]
            list10 = json_dict["buildings"][building_id]["Solar_radiation"]["Panels_results"]["Roof"]["dmfa"]["list"]
            list11 = json_dict["buildings"][building_id]["Solar_radiation"]["Panels_results"]["Facades"]["dmfa"][
                "list"]
            list12 = json_dict["buildings"][building_id]["Solar_radiation"]["Panels_results"]["Total"]["dmfa"]["list"]
            list13 = \
                json_dict["buildings"][building_id]["Solar_radiation"]["Panels_results"]["Roof"][
                    "lca_recycling_primary_energy"][
                    "list"]
            list14 = \
                json_dict["buildings"][building_id]["Solar_radiation"]["Panels_results"]["Facades"][
                    "lca_recycling_primary_energy"][
                    "list"]
            list15 = \
                json_dict["buildings"][building_id]["Solar_radiation"]["Panels_results"]["Total"][
                    "lca_recycling_primary_energy"][
                    "list"]
            list16 = \
                json_dict["buildings"][building_id]["Solar_radiation"]["Panels_results"]["Roof"][
                    "lca_recycling_carbon"][
                    "list"]
            list17 = \
                json_dict["buildings"][building_id]["Solar_radiation"]["Panels_results"]["Facades"][
                    "lca_recycling_carbon"][
                    "list"]
            list18 = \
                json_dict["buildings"][building_id]["Solar_radiation"]["Panels_results"]["Total"][
                    "lca_recycling_carbon"][
                    "list"]

            array = numpy.transpose(
                [list1, list2, list3, list4, list5, list6, list7, list8, list9, list10, list11, list12, list13, list14,
                 list15, list16, list17, list18])

            write_to_csv_arr(header, array, path_folder_panels_results_csv)

    @staticmethod
    def get_energy_data_from_all_buildings(building_dict):

        cum_energy_harvested_roof_uc = []
        cum_energy_harvested_facades_uc = []
        cum_energy_harvested_total_uc = []
        cum_primary_energy_roof_uc = []
        cum_primary_energy_facades_uc = []
        cum_primary_energy_total_uc = []

        for building in building_dict.values():
            # get the energy values
            cum_energy_harvested_roof = get_cumul_values(building.results_panels["Roof"]["energy_harvested"][
                                                             "list"])
            cum_primary_energy_roof = add_elements_of_two_lists(
                get_cumul_values(building.results_panels["Roof"]["lca_craddle_to_installation_primary_energy"][
                                     "list"]),
                get_cumul_values(building.results_panels["Roof"]["lca_recycling_primary_energy"]["list"]))
            cum_energy_harvested_facades = get_cumul_values(
                building.results_panels["Facades"]["energy_harvested"][
                    "list"])
            cum_primary_energy_facades = add_elements_of_two_lists(
                get_cumul_values(
                    building.results_panels["Facades"]["lca_craddle_to_installation_primary_energy"][
                        "list"]),
                get_cumul_values(building.results_panels["Facades"]["lca_recycling_primary_energy"]["list"]))
            cum_energy_harvested_total = get_cumul_values(building.results_panels["Total"]["energy_harvested"][
                                                              "list"])
            cum_primary_energy_total = add_elements_of_two_lists(
                get_cumul_values(building.results_panels["Total"]["lca_craddle_to_installation_primary_energy"][
                                     "list"]),
                get_cumul_values(building.results_panels["Total"]["lca_recycling_primary_energy"]["list"]))

            # and add it to the total list of the uc
            cum_energy_harvested_roof_uc = add_elements_of_two_lists(cum_energy_harvested_roof_uc,
                                                                     cum_energy_harvested_roof)
            cum_energy_harvested_facades_uc = add_elements_of_two_lists(cum_energy_harvested_facades_uc,
                                                                        cum_energy_harvested_facades)
            cum_energy_harvested_total_uc = add_elements_of_two_lists(cum_energy_harvested_total_uc,
                                                                      cum_energy_harvested_total)
            cum_primary_energy_roof_uc = add_elements_of_two_lists(cum_primary_energy_roof_uc,
                                                                   cum_primary_energy_roof)
            cum_primary_energy_facades_uc = add_elements_of_two_lists(cum_primary_energy_facades_uc,
                                                                      cum_primary_energy_facades)
            cum_primary_energy_total_uc = add_elements_of_two_lists(cum_primary_energy_total_uc,
                                                                    cum_primary_energy_total)

        return cum_energy_harvested_roof_uc, cum_energy_harvested_facades_uc, cum_energy_harvested_total_uc, \
            cum_primary_energy_roof_uc, cum_primary_energy_facades_uc, cum_primary_energy_total_uc

    @staticmethod
    def get_carbon_data_from_all_buildings(building_dict, country_ghe_cost):

        cum_carbon_emissions_roof_uc = []
        cum_carbon_emissions_facades_uc = []
        cum_carbon_emissions_total_uc = []
        cum_avoided_carbon_emissions_roof_uc = []
        cum_avoided_carbon_emissions_facades_uc = []
        cum_avoided_carbon_emissions_total_uc = []

        for building in building_dict.items():
            # get the carbon values
            cum_carbon_emissions_roof = add_elements_of_two_lists(
                get_cumul_values(building.results_panels["Roof"]["lca_craddle_to_installation_carbon"]["list"]),
                get_cumul_values(building.results_panels["Roof"]["lca_recycling_carbon"]["list"]))
            avoided_carbon_emissions_list_roof = [i * country_ghe_cost for i in building.results_panels["Roof"][
                "energy_harvested"]["list"]]
            cum_avoided_carbon_emissions_roof = get_cumul_values(avoided_carbon_emissions_list_roof)
            cum_carbon_emissions_facades = add_elements_of_two_lists(
                get_cumul_values(building.results_panels["Facades"]["lca_craddle_to_installation_carbon"]["list"]),
                get_cumul_values(building.results_panels["Facades"]["lca_recycling_carbon"]["list"]))
            avoided_carbon_emissions_list_facades = [i * country_ghe_cost for i in building.results_panels["Facades"][
                "energy_harvested"]["list"]]
            cum_avoided_carbon_emissions_facades = get_cumul_values(avoided_carbon_emissions_list_facades)
            cum_carbon_emissions_total = add_elements_of_two_lists(
                get_cumul_values(building.results_panels["Total"]["lca_craddle_to_installation_carbon"]["list"]),
                get_cumul_values(building.results_panels["Total"]["lca_recycling_carbon"]["list"]))
            avoided_carbon_emissions_list_total = [i * country_ghe_cost for i in building.results_panels["Total"][
                "energy_harvested"]["list"]]
            cum_avoided_carbon_emissions_total = get_cumul_values(avoided_carbon_emissions_list_total)

            # and add it to the total list of the uc
            cum_carbon_emissions_roof_uc = add_elements_of_two_lists(cum_carbon_emissions_roof_uc,
                                                                     cum_carbon_emissions_roof)
            cum_carbon_emissions_facades_uc = add_elements_of_two_lists(cum_carbon_emissions_facades_uc,
                                                                        cum_carbon_emissions_facades)
            cum_carbon_emissions_total_uc = add_elements_of_two_lists(cum_carbon_emissions_total_uc,
                                                                      cum_carbon_emissions_total)
            cum_avoided_carbon_emissions_roof_uc = add_elements_of_two_lists(cum_avoided_carbon_emissions_roof_uc,
                                                                             cum_avoided_carbon_emissions_roof)
            cum_avoided_carbon_emissions_facades_uc = add_elements_of_two_lists(cum_avoided_carbon_emissions_facades_uc,
                                                                                cum_avoided_carbon_emissions_facades)
            cum_avoided_carbon_emissions_total_uc = add_elements_of_two_lists(cum_avoided_carbon_emissions_total_uc,
                                                                              cum_avoided_carbon_emissions_total)

        return cum_avoided_carbon_emissions_roof_uc, cum_avoided_carbon_emissions_facades_uc, \
            cum_avoided_carbon_emissions_total_uc, cum_carbon_emissions_roof_uc, cum_carbon_emissions_facades_uc, \
            cum_carbon_emissions_total_uc

    @staticmethod
    def plot_energy_results_uc(path_folder_simulation, years, cum_energy_harvested_roof_uc,
                               cum_energy_harvested_facades_uc, cum_energy_harvested_total_uc,
                               cum_primary_energy_roof_uc, cum_primary_energy_facades_uc,
                               cum_primary_energy_total_uc):

        fig = plt.figure()
        plt.plot(years, cum_energy_harvested_roof_uc, 'gd', markersize=4,
                 label="Cumulative energy harvested on the roof")
        plt.plot(years, cum_energy_harvested_facades_uc, 'g.', label="Cumulative energy harvested on the facades")
        plt.plot(years, cum_energy_harvested_total_uc, 'g', label="Total cumulative energy harvested")
        plt.plot(years, cum_primary_energy_roof_uc, 'rd', markersize=4, label="Cumulative primary energy, roof")
        plt.plot(years, cum_primary_energy_facades_uc, 'r.', label="Cumulative primary energy, facades")
        plt.plot(years, cum_primary_energy_total_uc, 'r', label="Total cumulative primary energy")

        # get the intersection when energy harvested becomes higher thant primary energy
        slope, intercept = transform_to_linear_function(years, cum_energy_harvested_total_uc)

        def cum_energy_harvested_eq(x):
            return slope * x + intercept

        cum_primary_energy_total_fun = generate_step_function(years, cum_primary_energy_total_uc)

        intersection = find_intersection_functions(cum_energy_harvested_eq, cum_primary_energy_total_fun, years[0],
                                                   years[-1])
        plt.axhline(round(intersection[1]), color='k')
        plt.axvline(intersection[0], color='k')
        plt.text(-2, round(intersection[1]), f'y={round(intersection[1])}', va='bottom', ha='left')
        plt.text(round(intersection[0], 1), 0, f'x={round(intersection[0], 1)}', va='bottom', ha='left')

        # get the intersection point when all the energy used has been reimbursed
        asymptote_value = round(cum_primary_energy_total_uc[-1])

        def asymptote_eq(x):
            return asymptote_value

        interp_point = find_intersection_functions(cum_energy_harvested_eq, asymptote_eq, years[0], years[-1])
        plt.axvline(x=round(interp_point[0], 1), color='k')
        plt.text(round(interp_point[0], 1) - 3, -80000, f'x={round(interp_point[0], 1)}', va='bottom', ha='left')
        plt.axhline(asymptote_value, color='k')
        plt.text(round(interp_point[0]), asymptote_value, f'y={asymptote_value}', va='bottom', ha='left')

        plt.xlabel('Time (years)')
        plt.ylabel('Energy (kWh)')
        plt.title('Cumulative harvested energy and primary energy used during the study over the entire neighborhood')
        plt.grid(True)
        plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.2), ncol=2)
        file_name = 'cumulative_energy_harvested_and_primary_energy_urban_canopy.pdf'
        fig.savefig(f'{path_folder_simulation}/{file_name}', bbox_inches='tight')
        plt.show()

    @staticmethod
    def plot_carbon_results_uc(path_folder_simulation, years, cum_avoided_carbon_emissions_roof_uc,
                               cum_avoided_carbon_emissions_facades_uc, cum_avoided_carbon_emissions_total_uc,
                               cum_carbon_emissions_roof_uc, cum_carbon_emissions_facades_uc,
                               cum_carbon_emissions_total_uc):

        fig = plt.figure(figsize=(8, 6))
        plt.plot(years, cum_avoided_carbon_emissions_roof_uc, 'gd', markersize=4,
                 label="Cumulative avoided GHG emissions, roof")
        plt.plot(years, cum_avoided_carbon_emissions_facades_uc, 'go', markersize=4,
                 label="Cumulative avoided GHG emissions, facades")
        plt.plot(years, cum_avoided_carbon_emissions_total_uc, 'g',
                 label="Total cumulative avoided GHG emissions")
        plt.plot(years, cum_carbon_emissions_roof_uc, 'rd', markersize=4,
                 label="Cumulative GHG emissions, roof")
        plt.plot(years, cum_carbon_emissions_facades_uc, 'ro', markersize=4,
                 label="Cumulative GHG emissions, facades")
        plt.plot(years, cum_carbon_emissions_total_uc, 'r',
                 label="Total cumulative GHG emissions")

        slope, intercept = transform_to_linear_function(years, cum_avoided_carbon_emissions_total_uc)

        def cum_avoided_carbon_emissions_eq(x):
            return slope * x + intercept

        # get the intersection point when all the energy used has been reimbursed
        asymptote_value = round(cum_carbon_emissions_total_uc[-1])

        def asymptote_eq(x):
            return asymptote_value

        interp_point = find_intersection_functions(cum_avoided_carbon_emissions_eq, asymptote_eq, years[0], years[-1])
        plt.axvline(x=round(interp_point[0], 1), color='k')
        plt.text(round(interp_point[0], 1) - 2, -60000, f'x={round(interp_point[0], 1)}', va='bottom', ha='left')
        plt.axhline(asymptote_value, color='k')
        plt.text(round(interp_point[0]) - 6, asymptote_value, f'y={asymptote_value}', va='bottom', ha='left')

        plt.xlabel('Time (years)')
        plt.ylabel('GHE emissions (kgCO2eq)')
        plt.title('Cumulative GHG emissions during the study over the entire neighborhood')
        plt.grid(True)
        plt.subplots_adjust(bottom=0.5)
        plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.2), ncol=2)
        file_name = 'cumulative_ghg_emissions_urban_canopy.pdf'
        fig.savefig(f'{path_folder_simulation}/{file_name}', bbox_inches='tight')
        plt.show()

    @staticmethod
    def plot_ghe_per_kwh_uc(path_folder_simulation, years, cum_energy_harvested_total_uc,
                            cum_carbon_emissions_total_uc):

        ghg_per_kWh = [(x / y) * 1000 for x, y in zip(cum_carbon_emissions_total_uc, cum_energy_harvested_total_uc)]

        fig = plt.figure()
        plt.plot(years, ghg_per_kWh)
        plt.xlabel('Time (years)')
        plt.ylabel('GHE emissions (gCO2eq/kWh)')
        plt.title("Evolution of the cost in GHG emissions for each kWh harvested during the study over the entire "
                  "neighborhood")
        plt.grid(True)
        file_name = 'ghg_per_kWh_plot_urban_canopy.pdf'
        fig.savefig(f'{path_folder_simulation}/{file_name}', bbox_inches='tight')

    @staticmethod
    def plot_results_eroi_uc(path_folder_simulation, years, cum_primary_energy_total_uc,
                             cum_energy_harvested_total_uc):

        eroi = [x / y for x, y in zip(cum_energy_harvested_total_uc, cum_primary_energy_total_uc)]

        fig = plt.figure()
        plt.plot(years, eroi)
        plt.xlabel('Time (years)')
        plt.ylabel('EROI')
        plt.title("Evolution of the EROI during the study over the entire neighborhood")
        plt.grid(True)
        file_name = 'eroi_urban_canopy.pdf'
        fig.savefig(f'{path_folder_simulation}/{file_name}', bbox_inches='tight')
