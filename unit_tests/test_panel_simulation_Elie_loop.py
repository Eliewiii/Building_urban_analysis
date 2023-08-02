from unit_tests.utils_main_import_scripts import *
import shutil


minimum_ratio_energy_harvested_on_primary_energy_list = [3]
replacement_year_list = [50]
os.makedirs(os.path.join(default_path_folder_simulation, "panels_simulation_results"), exist_ok=True)

uc_csv = os.path.join(default_path_folder_simulation, "panels_simulation_results.csv")
cumulative_energy_harvested_and_primary_energy_urban_canopy = os.path.join(default_path_folder_simulation,
                                                                           "cumulative_energy_harvested_and_primary_energy_urban_canopy.pdf")
cumulative_ghg_emissions_urban_canopy = os.path.join(default_path_folder_simulation,
                                                     "cumulative_ghg_emissions_urban_canopy.pdf")
eroi_urban_canopy = os.path.join(default_path_folder_simulation, "eroi_urban_canopy.pdf")
ghg_per_kWh_plot_urban_canopy = os.path.join(default_path_folder_simulation,
                                             "ghg_per_kWh_plot_urban_canopy.pdf")

for ratio in minimum_ratio_energy_harvested_on_primary_energy_list:
    for replacement_year in replacement_year_list:
        # Load urban_canopy
        urban_canopy_object = SimulationCommonMethods.create_or_load_urban_canopy_object(
            path_folder_simulation=
            default_path_folder_simulation)
        # Run radiation simulation on the Urban Canopy
        SolarOrPanelSimulation.panel_simulation(urban_canopy_object=urban_canopy_object,
                                                path_folder_simulation=default_path_folder_simulation,
                                                path_pv_tech_dictionary_json=default_path_pv_tech_dictionary,
                                                id_pv_tech_roof=default_id_pv_tech_roof,
                                                id_pv_tech_facades=default_id_pv_tech_facades,
                                                minimum_ratio_energy_harvested_on_primary_energy=ratio,
                                                performance_ratio=default_performance_ratio,
                                                study_duration_in_years=default_study_duration_years,
                                                replacement_scenario="every_X_years",
                                                replacement_year=replacement_year)

        # Export urban_canopy to pickle
        SimulationCommonMethods.save_urban_canopy_object_to_pickle(urban_canopy_object=urban_canopy_object,
                                                                   path_folder_simulation=default_path_folder_simulation)
        # Export urban_canopy to json
        SimulationCommonMethods.save_urban_canopy_to_json(urban_canopy_object=urban_canopy_object,
                                                          path_folder_simulation=default_path_folder_simulation)

        SimulationPostProcessingAndPlots.plot_graphs_total_urban_canopy(
            urban_canopy_object=urban_canopy_object,
            path_folder_simulation=default_path_folder_simulation,
            study_duration_years=default_study_duration_years,
            country_ghe_cost=default_country_ghe_cost)
        # Generate csv panels data
        SimulationPostProcessingAndPlots.generate_csv_panels_simulation_results(
            urban_canopy_object=urban_canopy_object,
            path_folder_simulation=
            default_path_folder_simulation)

        path_results_sim_folder = os.path.join(default_path_folder_simulation, "panels_simulation_results",
                                               f"eroi_panel_{ratio}_replacement_{replacement_year}")
        os.makedirs(path_results_sim_folder, exist_ok=True)

        shutil.move(uc_csv, path_results_sim_folder)
        shutil.move(cumulative_energy_harvested_and_primary_energy_urban_canopy, path_results_sim_folder)
        shutil.move(cumulative_ghg_emissions_urban_canopy, path_results_sim_folder)
        shutil.move(eroi_urban_canopy, path_results_sim_folder)
        shutil.move(ghg_per_kWh_plot_urban_canopy, path_results_sim_folder)
