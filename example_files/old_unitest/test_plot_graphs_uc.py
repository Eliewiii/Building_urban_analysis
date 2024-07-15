from bua.utils.utils_import_simulation_steps_and_config_var import *

# Load urban_canopy
urban_canopy_object = SimulationCommonMethods.create_or_load_urban_canopy_object(path_simulation_folder=
                                                                                 default_path_simulation_folder)

# Export urban_canopy to pickle
SimulationCommonMethods.save_urban_canopy_object_to_pickle(urban_canopy_object=urban_canopy_object,
                                                           path_simulation_folder=default_path_simulation_folder)
# Export urban_canopy to json
SimulationCommonMethods.save_urban_canopy_to_json(urban_canopy_object=urban_canopy_object,
                                                  path_simulation_folder=default_path_simulation_folder)

SimulationPostProcessingAndPlots.plot_graphs_total_urban_canopy(urban_canopy_object=urban_canopy_object,
                                                                path_simulation_folder=default_path_simulation_folder,
                                                                study_duration_years=default_study_duration_years,
                                                                country_ghe_cost=default_country_ghe_cost)
# Generate csv panels data
SimulationPostProcessingAndPlots.generate_csv_panels_simulation_results(urban_canopy_object=urban_canopy_object,
                                                                        path_simulation_folder=
                                                                        default_path_simulation_folder)