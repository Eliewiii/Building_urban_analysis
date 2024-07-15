from bua.utils.utils_import_simulation_steps_and_config_var import *

simulation_folders = [r'C:\Users\eliem\Documents\Technion\Simulation_IBPSA\High_Density_Context',
                      r'C:\Users\eliem\Documents\Technion\Simulation_IBPSA\Medium_Density_Context',
                      r'C:\Users\eliem\Documents\Technion\Simulation_IBPSA\Low_Density_Context']

scenario_list = ["Efficiency", "Balanced", "Production"]

scenario_param_dict = {
    "Efficiency": {"replacement_scenario": "replace_all_panels_every_X_years", "replacement frequency": 25,
                   "minimal_panel_eroi": 3},
    "Balanced": {"replacement_scenario": "replace_all_panels_every_X_years", "replacement frequency": 25,
                 "minimal_panel_eroi": 2},
    "Production": {"replacement_scenario": "replace_failed_panels_every_X_years", "replacement frequency": 5,
                   "minimal_panel_eroi": 1.2}
    }

roof_id_pv_tech = "mitrex_roof c-Si M395-B1F china"
facades_id_pv_tech = "mitrex_facades c-Si Solar Siding 350W - Dove Grey china"

for path_simulation_folder in simulation_folders:

    # Create urban_canopy
    urban_canopy_object = SimulationCommonMethods.create_or_load_urban_canopy_object(
        path_simulation_folder=path_simulation_folder)

    for scenario in scenario_list:

        # Run simulation
        SimFunSolarRadAndBipv.run_bipv_harvesting_and_lca_simulation(
            path_simulation_folder=path_simulation_folder,
            urban_canopy_object=urban_canopy_object,
            start_year=0,
            end_year=50,
            continue_simulation=False,
            bipv_scenario_identifier=scenario,
            replacement_frequency_in_years=scenario_param_dict[scenario]["replacement frequency"],
            roof_id_pv_tech=roof_id_pv_tech,
            facades_id_pv_tech=facades_id_pv_tech,
            efficiency_computation_method=default_efficiency_computation_method,
            minimum_panel_eroi=scenario_param_dict[scenario]["minimal_panel_eroi"],
            replacement_scenario=scenario_param_dict[scenario]["replacement_scenario"])

# # Export urban_canopy to pickle
# SimulationCommonMethods.save_urban_canopy_object_to_pickle(urban_canopy_object=urban_canopy_object,
#                                                            path_simulation_folder=default_path_simulation_folder)
# # Export urban_canopy to json
# SimulationCommonMethods.save_urban_canopy_to_json(urban_canopy_object=urban_canopy_object,
#                                                   path_simulation_folder=default_path_simulation_folder)
