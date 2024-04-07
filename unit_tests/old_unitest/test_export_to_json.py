from unit_tests.utils_main_import_scripts import *

# Create urban_canopy
urban_canopy_object = SimulationCommonMethods.create_or_load_urban_canopy_object(
    path_simulation_folder=default_path_simulation_folder)

#add GIS
SimulationLoadBuildingOrGeometry.add_2D_GIS_to_urban_canopy(urban_canopy=urban_canopy_object,
                                                            path_gis=default_path_gis,
                                                            path_additional_gis_attribute_key_dict=
                                                            None,
                                                            unit=default_unit_gis)

# make envelope
SimulationPostProcessingAndPlots.generate_hb_model_contains_all_building_envelopes_to_plot_Grasshopper(
    urban_canopy_object=urban_canopy_object,
    path_simulation_folder=default_path_simulation_folder)

#

# Export urban_canopy to pickle
SimulationCommonMethods.save_urban_canopy_object_to_pickle(urban_canopy_object=urban_canopy_object,
                                                           path_simulation_folder=default_path_simulation_folder)
# Export urban_canopy to json
SimulationCommonMethods.save_urban_canopy_to_json(urban_canopy_object=urban_canopy_object,
                                                           path_simulation_folder=default_path_simulation_folder)
