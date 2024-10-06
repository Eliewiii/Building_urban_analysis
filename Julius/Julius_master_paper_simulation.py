"""
Script for the context selection paper UBES simulation.
"""
import json
import logging

from Julius.data_plotting import kpi_bar
from Julius.postprocessing import calculate_npv_per_year, include_carbon_credit
from bua.utils.utils_import_simulation_steps_and_config_var import *

from bua.building.building_modeled import BuildingModeled

'''
Which steps to take?
'''
ubes_check = 'no'
bipv_and_kpi_check = 'no'
postprocessing_check = 'yes'
plotting_check = 'yes'

# Initialize logger
dev_logger = logging.getLogger("dev")
dev_logger.setLevel(logging.WARNING)
dev_handler = logging.FileHandler('dev_log.log', mode='w')
dev_formatter = logging.Formatter(
    '% %(asctime)s - %(message)s')
dev_handler.setFormatter(dev_formatter)
dev_logger.addHandler(dev_handler)

# Initialize json result file
name_result_json_file = "results_context_filter.json"
path_result_folder = r"C:\Users\julius.jandl\OneDrive - Technion\Julius PhD\Paper\results"
path_json_result_file = os.path.join(path_result_folder, name_result_json_file)

# Buildings folder
path_buildings = r"C:\Users\julius.jandl\OneDrive - Technion\Elie_Julius\Paper_Julius\Geometry\hbjson_target_buildings"

# EPW file
path_epw = r"C:\Users\julius.jandl\AppData\Local\Building_urban_analysis\Libraries\EPW\IS_5280_A_Tel_Aviv.epw"

cop_heating = 3
cop_cooling = 3

#post-processing
load_json_for_postprocessing = 'yes'
path_json_for_postprocessing = r"C:\Users\julius.jandl\OneDrive - Technion\Julius PhD\Paper\results\results_context_filter.json"

# discount rate for NPV
discount_rate = 0.05
# carbon credit
carboncredit = 37 # USD/t CO2

# Definition of Scenarios
rooftech_baseline = "mitrex_roof c-Si M390-A1F"  # baseline csi id
envtech_baseline = "mitrex_facades c-Si Solar Siding 350W - Dove Grey china"  # baseline csi id
replacement_frequency_baseline = 10  # years

envtech_aesthetic = "mitrex_facades c-Si Solar Siding 216W - beige china"  # baseline beige csi id
rooftech_econ_opt = "mitrex_roof c-Si M390-A1F optimistic"  # csi roof optimistic
envtech_econ_opt = "mitrex_facades c-Si Solar Siding 350W - Dove Grey china optimistic"  # csi grey env optimistic
rooftech_econ_pess = "mitrex_roof c-Si M390-A1F pessimistic"  # csi roof pessimistic
envtech_econ_pess = "mitrex_facades c-Si Solar Siding 350W - Dove Grey china pessimistic"  # csi grey env pessimistic
rooftech_cdte = "cdte firstsolar FS-6445 roof"
envtech_cdte = "cdte firstsolar FS-6445 facade"
rooftech_cigs = "cigs eterbright CIGS-3650A1 roof"
envtech_cigs = "cigs eterbright CIGS-3650A1 facade"


# dimensions of panelgrid
# c-si
panel_x_length_csi = 2.030
panel_y_length_csi = 0.990
# cdte
panel_x_length_cdte = 2.009
panel_y_length_cdte = 1.232
# cigs
panel_x_length_cigs = 1.901
panel_y_length_cigs = 1.237


scenarios_dict = {
    "baseline": {
        "rooftech": rooftech_baseline,
        "envtech": envtech_baseline,
        "replacement": replacement_frequency_baseline,
        "x_size" : panel_x_length_csi,
        "y_size" : panel_y_length_csi
    },
    "rep_5": {
        "rooftech": rooftech_baseline,
        "envtech": envtech_baseline,
        "replacement": 5,
        "x_size" : panel_x_length_csi,
        "y_size" : panel_y_length_csi
    },
    "rep_15": {
        "rooftech": rooftech_baseline,
        "envtech": envtech_baseline,
        "replacement": 15,
        "x_size" : panel_x_length_csi,
        "y_size" : panel_y_length_csi
    },
    "rep_20": {
        "rooftech": rooftech_baseline,
        "envtech": envtech_baseline,
        "replacement": 20,
        "x_size" : panel_x_length_csi,
        "y_size" : panel_y_length_csi
    },
    "rep_25": {
        "rooftech": rooftech_baseline,
        "envtech": envtech_baseline,
        "replacement": 25,
        "x_size" : panel_x_length_csi,
        "y_size" : panel_y_length_csi
    },
    "aesthetic": {
        "rooftech": rooftech_baseline,
        "envtech": envtech_aesthetic,
        "replacement": replacement_frequency_baseline,
        "x_size" : panel_x_length_csi,
        "y_size" : panel_y_length_csi
    },
    "econ_opt": {
        "rooftech": rooftech_econ_opt,
        "envtech": envtech_econ_opt,
        "replacement": replacement_frequency_baseline,
        "x_size" : panel_x_length_csi,
        "y_size" : panel_y_length_csi
    },
    "econ_pess": {
        "rooftech": rooftech_econ_pess,
        "envtech": envtech_econ_pess,
        "replacement": replacement_frequency_baseline,
        "x_size" : panel_x_length_csi,
        "y_size" : panel_y_length_csi
    },
    "cdte": {
        "rooftech": rooftech_cdte,
        "envtech": envtech_cdte,
        "replacement": replacement_frequency_baseline,
        "x_size" : panel_x_length_cdte,
        "y_size" : panel_y_length_cdte
    },
    "cigs": {
        "rooftech": rooftech_cigs,
        "envtech": envtech_cigs,
        "replacement": replacement_frequency_baseline,
        "x_size" : panel_x_length_cigs,
        "y_size" : panel_y_length_cigs
}
}

scenarios_list = list(scenarios_dict.keys())

if ubes_check == 'yes':

    # -------------------------------------------------------------------------------------------
    # Init json results file
    # -------------------------------------------------------------------------------------------
    json_result_dict = {}
    with open(path_json_result_file, 'w') as json_file:
        json.dump(json_result_dict, json_file)

    # -------------------------------------------------------------------------------------------
    # Preprocessing for all scenarios
    # -------------------------------------------------------------------------------------------
    # Clear simulation temp folder at when simulating for another building
    SimulationCommonMethods.clear_simulation_temp_folder()
    # Create simulation folder
    SimulationCommonMethods.make_simulation_folder()
    # Make an original urban canopy object that will be copied for each simulation
    urban_canopy_object = SimulationCommonMethods.create_or_load_urban_canopy_object()
    # Load context from json
    SimulationLoadBuildingOrGeometry.add_buildings_from_lb_polyface3d_json_in_urban_canopy(
        urban_canopy_object=urban_canopy_object,
        path_lb_polyface3d_json_file=r"C:\Users\julius.jandl\OneDrive - Technion\Elie_Julius\Paper_Julius\Geometry\Ramat_gan_lb_pf3d_julius_paper.json")
    # Make the merged face of the context buildings
    SimulationBuildingManipulationFunctions.make_merged_face_of_buildings_in_urban_canopy(
        urban_canopy_object=urban_canopy_object, overwrite=True)
    SimulationBuildingManipulationFunctions.make_oriented_bounding_boxes_of_buildings_in_urban_canopy(
        urban_canopy_object=urban_canopy_object, overwrite=True)

    # Load epw and simulation parameters
    UrbanBuildingEnergySimulationFunctions.load_epw_and_hb_simulation_parameters_for_ubes_in_urban_canopy(
        urban_canopy_obj=urban_canopy_object,
        path_weather_file=path_epw,
        overwrite=True)

    # Load building from json
    SimulationLoadBuildingOrGeometry.add_buildings_from_hbjson_to_urban_canopy(
        urban_canopy_object=urban_canopy_object,
        path_folder_hbjson=path_buildings,
        path_file_hbjson=None,
        are_buildings_targets=True,
        keep_context_from_hbjson=False)

    # Make the merged face of the building (not too sure if necessary)
    SimulationBuildingManipulationFunctions.make_merged_face_of_buildings_in_urban_canopy(
        urban_canopy_object=urban_canopy_object, overwrite=False)
    # Make the oriented bounding boxes of the building (not too sure if necessary)
    SimulationBuildingManipulationFunctions.make_oriented_bounding_boxes_of_buildings_in_urban_canopy(
        urban_canopy_object=urban_canopy_object, overwrite=False)

    mvfc = 0.01
    nb_of_rays = 3
    consider_windows = True

    # Perform the context filtering
    SimulationContextFiltering.perform_first_pass_of_context_filtering_on_buildings(
        urban_canopy_object=urban_canopy_object,
        min_vf_criterion=mvfc,
        overwrite=True)
    SimulationContextFiltering.perform_second_pass_of_context_filtering_on_buildings(
        urban_canopy_object=urban_canopy_object,
        number_of_rays=nb_of_rays,
        consider_windows=consider_windows,
        overwrite=True)

    # UBES
    # Write IDF
    UrbanBuildingEnergySimulationFunctions.generate_idf_files_for_ubes_with_openstudio_in_urban_canopy(
        urban_canopy_obj=urban_canopy_object,
        overwrite=True,
        silent=True)
    # Run IDF through EnergyPlus
    UrbanBuildingEnergySimulationFunctions.run_idf_files_with_energyplus_for_ubes_in_urban_canopy(
        urban_canopy_obj=urban_canopy_object,
        overwrite=True,
        silent=True)
    # Extract UBES results
    UrbanBuildingEnergySimulationFunctions.extract_results_from_ep_simulation(
        urban_canopy_obj=urban_canopy_object,
        cop_heating=3., cop_cooling=3.)

if bipv_and_kpi_check == 'yes':
    # -------------------------------------------------------------------------------------------
    # Loop over scenarios for BIPV assessment
    # -------------------------------------------------------------------------------------------
    for scenario_id in scenarios_list:
        # BIPV
        # Merge the face of the buildings to reduce the number of faces and the
        SimulationBuildingManipulationFunctions.make_merged_face_of_buildings_in_urban_canopy(
            urban_canopy_object=urban_canopy_object)
        # Generate the sensor grid
        SimFunSolarRadAndBipv.generate_sensor_grid(urban_canopy_object=urban_canopy_object,
                                                   roof_grid_size_x = scenarios_dict[scenario_id]["x_size"],
                                                   facades_grid_size_x = scenarios_dict[scenario_id]["x_size"],
                                                   roof_grid_size_y = scenarios_dict[scenario_id]["y_size"],
                                                   facades_grid_size_y = scenarios_dict[scenario_id]["y_size"],
                                                   offset_dist = 0.01,
                                                   overwrite=True
                                                   )
        # Run annual solar irradiance simulation
        SimFunSolarRadAndBipv.run_annual_solar_irradiance_simulation(urban_canopy_object=urban_canopy_object)
        SimFunSolarRadAndBipv.run_bipv_harvesting_and_lca_simulation(
            urban_canopy_object=urban_canopy_object,
            building_id_list=None,
            bipv_scenario_identifier=scenario_id,
            roof_id_pv_tech = scenarios_dict[scenario_id]["rooftech"],
            facades_id_pv_tech = scenarios_dict[scenario_id]["envtech"],
            minimum_panel_eroi=1.45,
            start_year=2024,
            end_year=2074,
            replacement_scenario="replace_failed_panels_every_X_years",
            continue_simulation=False,
            update_panel_technology=False,
            replacement_frequency_in_years=scenarios_dict[scenario_id]["replacement"])

        ##### Run KPI computation
        SimFunSolarRadAndBipv.run_kpi_simulation(urban_canopy_object=urban_canopy_object,
                                                 bipv_scenario_identifier=scenario_id,
                                                 grid_ghg_intensity=default_grid_ghg_intensity,
                                                 grid_energy_intensity=default_grid_energy_intensity,
                                                 grid_electricity_sell_price=default_grid_electricity_sell_price,
                                                 zone_area=None)

        alternative_result_dict = {
            "scenario_id": scenario_id,
            "start_year": 2024,
            'end_year': 2074,
            "bipv_and_kpi_simulation": urban_canopy_object.bipv_scenario_dict[scenario_id].to_dict(),
            "UBES": urban_canopy_object.ubes_obj.to_dict()
        }


        json_result_dict[scenario_id] = alternative_result_dict
        # Overwrite the json file
        with open(path_json_result_file, 'w') as json_file:
            json.dump(json_result_dict, json_file)

if postprocessing_check == 'yes':
    # -------------------------------------------------------------------------------------------
    # Post-processing for carbon credit und net present value
    # -------------------------------------------------------------------------------------------

    for scenario_id in scenarios_list:

        # Open and read the JSON file
        if load_json_for_postprocessing == 'yes':
            with open(path_json_for_postprocessing, 'r') as file:
                dict_for_pp = json.load(file)
        else:
            with open(path_json_result_file, 'r') as file:
                dict_for_pp = json.load(file)

        # adding revenue of carbon credit to net economical benefit
        updated_revenue, updated_benefit = include_carbon_credit(carboncredit, default_grid_ghg_intensity, scenario_id,
                                                                 dict_for_pp)
        print('carbon credit calculated')
        for i in range(0, len(updated_revenue)):
            dict_for_pp[scenario_id]["bipv_and_kpi_simulation"]['kpis_results_dict']['intermediate_results']['total'][
                'net_economical_income']['yearly'][i] = updated_revenue[i]
            dict_for_pp[scenario_id]["bipv_and_kpi_simulation"]['kpis_results_dict']['intermediate_results']['total'][
                'net_economical_benefit']['yearly'][i] = updated_benefit[i]

        print('updating yearly values with carbon credit done')
        # updating cumulative values of income and benefit to include carbon credit
        dict_for_pp[scenario_id]["bipv_and_kpi_simulation"]['kpis_results_dict']['intermediate_results']['total'][
            'net_economical_income']['cumulative'] = []
        dict_for_pp[scenario_id]["bipv_and_kpi_simulation"]['kpis_results_dict']['intermediate_results']['total'][
            'net_economical_income']['cumulative'].append(updated_revenue[0])

        dict_for_pp[scenario_id]["bipv_and_kpi_simulation"]['kpis_results_dict']['intermediate_results']['total'][
            'net_economical_benefit']['cumulative'] = []
        dict_for_pp[scenario_id]["bipv_and_kpi_simulation"]['kpis_results_dict']['intermediate_results']['total'][
            'net_economical_benefit']['cumulative'].append(updated_benefit[0])

        for i in range(1, len(updated_benefit)):
            dict_for_pp['baseline']["bipv_and_kpi_simulation"]['kpis_results_dict']['intermediate_results']['total'][
                'net_economical_income']['cumulative'].append(
                dict_for_pp['baseline']["bipv_and_kpi_simulation"]['kpis_results_dict']['intermediate_results']['total'][
                    'net_economical_income']['cumulative'][i - 1] + updated_revenue[i])

            dict_for_pp[scenario_id]["bipv_and_kpi_simulation"]['kpis_results_dict']['intermediate_results']['total'][
                'net_economical_benefit']['cumulative'].append(
                dict_for_pp[scenario_id]["bipv_and_kpi_simulation"]['kpis_results_dict']['intermediate_results']['total'][
                    'net_economical_benefit']['cumulative'][i - 1] + updated_benefit[i])

        print('updating cumulative values with carbon credit done')

        # post-processing of the results to discount cash flows

        cash_flows = [[dict_for_pp[scenario_id]["bipv_and_kpi_simulation"]['bipv_results_dict']['total']['cost'][
                           'investment']['total'][
                           'yearly'][i] for i in range(0, 50)],
                      [dict_for_pp[scenario_id]["bipv_and_kpi_simulation"]['kpis_results_dict']['intermediate_results'][
                           'total'][
                           'net_economical_benefit']['yearly'][i] for i in range(0, 50)],
                      [dict_for_pp[scenario_id]["bipv_and_kpi_simulation"]['kpis_results_dict']['intermediate_results'][
                           'total'][
                           'net_economical_income']['yearly'][i] for i in range(0, 50)]]
        n = 0
        for cf in cash_flows:
            discounted_cf_cumu, discounted_cf_yearly = calculate_npv_per_year(cf, discount_rate)

            # update yearly values in result dict for discounted values
            cf = discounted_cf_yearly

            cumulative_values = []
            # Initialize the first cumulative value
            cumulative_values.append(cf[0])

            print(scenario_id, n, cf)
            # Calculate the cumulative sum for the rest of the values
            for i in range(1, len(cf)):
                cumulative_values.append(cumulative_values[i - 1] + cf[i])
                if n == 0:
                    dict_for_pp[scenario_id]["bipv_and_kpi_simulation"]['bipv_results_dict']['total']['cost']['investment'][
                        'total'][
                        'cumulative'][i] = cumulative_values[i]
                elif n == 1:
                    dict_for_pp[scenario_id]["bipv_and_kpi_simulation"]['kpis_results_dict']['intermediate_results'][
                        'total'][
                        'net_economical_benefit']['cumulative'][i] = cumulative_values[i]
                elif n == 2:
                    dict_for_pp[scenario_id]["bipv_and_kpi_simulation"]['kpis_results_dict']['intermediate_results'][
                    'total'][
                    'net_economical_income']['cumulative'][i] = cumulative_values[i]

            n = n + 1
        print('npv calculated')
        # adding net revenue from cost and benefit
        revenue_yearly = [
            dict_for_pp[scenario_id]["bipv_and_kpi_simulation"]['kpis_results_dict']['intermediate_results']['total'][
                'net_economical_benefit']['yearly'][i] +
            dict_for_pp[scenario_id]["bipv_and_kpi_simulation"]['bipv_results_dict']['total']['cost']['investment'][
                'total']['yearly'][i] for i in range(0, 50)]

        revenue_cumulative = [revenue_yearly[0]]
        for i in range(1, len(revenue_yearly)):
            revenue_cumulative.append(revenue_cumulative[i - 1] + revenue_yearly[i])

        # write revenue to dict
        dict_for_pp[scenario_id]["bipv_and_kpi_simulation"]['kpis_results_dict']['intermediate_results']['total'][
            'new_economical_revenue'] = {}
        dict_for_pp[scenario_id]["bipv_and_kpi_simulation"]['kpis_results_dict']['intermediate_results']['total'][
            'new_economical_revenue']['yearly'] = revenue_yearly
        dict_for_pp[scenario_id]["bipv_and_kpi_simulation"]['kpis_results_dict']['intermediate_results']['total'][
            'new_economical_revenue']['cumulative'] = revenue_cumulative
        print('revenue calculated')

        # save post-processed data in additional json
        json_result_dict = {}
        path_json_pp_file = os.path.join(path_result_folder, 'postprocessed_simulation_results.json')
        json_result_dict[scenario_id] = dict_for_pp
        # Overwrite the json file
        with open(path_json_pp_file, 'w') as json_file:
            json.dump(json_result_dict, json_file)
        print('json saved')


if plotting_check == 'yes':
    path_json_pp_file = os.path.join(path_result_folder, 'postprocessed_simulation_results.json')
    kpi_bar(path_json_pp_file, 2024, 2074)

# # Export urban_canopy to pickle
# SimulationCommonMethods.save_urban_canopy_object_to_pickle(urban_canopy_object=urban_canopy_object,
#                                                            path_simulation_folder=default_path_simulation_folder)
# # Export urban_canopy to json
# SimulationCommonMethods.save_urban_canopy_to_json(urban_canopy_object=urban_canopy_object,
#                                                   path_simulation_folder=default_path_simulation_folder)
