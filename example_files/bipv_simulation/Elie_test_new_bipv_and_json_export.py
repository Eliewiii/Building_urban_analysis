from bua.utils.utils_import_simulation_steps_and_config_var import *

# Create urban_canopy
urban_canopy_object = SimulationCommonMethods.create_or_load_urban_canopy_object(
    path_simulation_folder=default_path_simulation_folder)

SimFunSolarRadAndBipv.run_bipv_harvesting_and_lca_simulation(
    urban_canopy_object=urban_canopy_object,
    building_id_list=None,
    roof_id_pv_tech="mitrex_facades c-Si Solar Siding 350W - Dove Grey china",
    facades_id_pv_tech="mitrex_facades c-Si Solar Siding 350W - Dove Grey china",
    roof_transport_id="transport c-si roof canada",
    facades_transport_id="transport c-si roof canada",
    roof_inverter_id=default_roof_inverter_id,
    facades_inverter_id=default_facades_inverter_id,
    roof_inverter_sizing_ratio=default_roof_inverter_sizing_ratio,
    facades_inverter_sizing_ratio=default_facades_inverter_sizing_ratio,
    minimum_panel_eroi=default_minimum_panel_eroi,
    start_year=2020,
    end_year=2080,
    replacement_scenario="replace_failed_panels_every_X_years",
    continue_simulation=False,
    update_panel_technology=False,
    replacement_frequency_in_years=30)

# Export urban_canopy to pickle
SimulationCommonMethods.save_urban_canopy_object_to_pickle(urban_canopy_object=urban_canopy_object,
                                                           path_simulation_folder=default_path_simulation_folder)
# Export urban_canopy to json
SimulationCommonMethods.save_urban_canopy_to_json(urban_canopy_object=urban_canopy_object,
                                                  path_simulation_folder=default_path_simulation_folder)
