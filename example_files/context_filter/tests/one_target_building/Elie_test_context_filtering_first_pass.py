from bua.utils.utils_import_simulation_steps_and_config_var import *


# Inputs
path_gis = r"C:\Users\eliem\OneDrive - Technion\BUA\Context_filter\Sample GIS\sample_gis_context_filter_1"
path_hbjson_file = r"C:\Users\eliem\OneDrive - Technion\BUA\Samples\Elie\hb_model\complex_hb_model.hbjson"




urban_canopy_object = SimulationCommonMethods.create_or_load_urban_canopy_object(
    path_simulation_folder=default_path_simulation_folder)



mvfc_list = [0.001]

for mvfc in mvfc_list:
    context_building_id_list, tot_duration, sim_duration_dict = SimulationContextFiltering.perform_first_pass_of_context_filtering_on_buildings(urban_canopy_object,
                                                                 building_id_list=None,
                                                                 on_building_to_simulate=False,
                                                                 min_vf_criterion=mvfc,
                                                                 overwrite=True)

    print(f"mvfc: {mvfc}, nb_build :{len(context_building_id_list)}, dur: {sim_duration_dict}")



# Export urban_canopy to pickle
SimulationCommonMethods.save_urban_canopy_object_to_pickle(urban_canopy_object=urban_canopy_object,
                                                           path_simulation_folder=default_path_simulation_folder)
# Export urban_canopy to json
SimulationCommonMethods.save_urban_canopy_to_json(urban_canopy_object=urban_canopy_object,
                                                  path_simulation_folder=default_path_simulation_folder)

