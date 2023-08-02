from unit_tests.utils_main_import_scripts import *

# Load urban_canopy
urban_canopy_object = SimulationCommonMethods.create_or_load_urban_canopy_object(path_folder_simulation=
                                                                                 default_path_folder_simulation)

# Run radiation simulation on the Urban Canopy
SolarOrPanelSimulation.panel_simulation(urban_canopy_object=urban_canopy_object,
                                        path_folder_simulation=default_path_folder_simulation,
                                        path_pv_tech_dictionary_json=default_path_pv_tech_dictionary,
                                        id_pv_tech_roof=default_id_pv_tech_roof,
                                        id_pv_tech_facades=default_id_pv_tech_facades,
                                        minimum_ratio_energy_harvested_on_primary_energy=2.,
                                        performance_ratio=default_performance_ratio,
                                        study_duration_in_years=default_study_duration_years,
                                        replacement_scenario="every_X_years",
                                        replacement_year=10)

# Export urban_canopy to pickle
SimulationCommonMethods.save_urban_canopy_object_to_pickle(urban_canopy_object=urban_canopy_object,
                                                           path_folder_simulation=default_path_folder_simulation)
# Export urban_canopy to json
SimulationCommonMethods.save_urban_canopy_to_json(urban_canopy_object=urban_canopy_object,
                                                  path_folder_simulation=default_path_folder_simulation)

SimulationPostProcessingAndPlots.plot_graphs_total_urban_canopy(urban_canopy_object=urban_canopy_object,
                                                                path_folder_simulation=default_path_folder_simulation,
                                                                study_duration_years=default_study_duration_years,
                                                                country_ghe_cost=default_country_ghe_cost)
# Generate csv panels data
SimulationPostProcessingAndPlots.generate_csv_panels_simulation_results(urban_canopy_object=urban_canopy_object,
                                                                        path_folder_simulation=
                                                                        default_path_folder_simulation)
