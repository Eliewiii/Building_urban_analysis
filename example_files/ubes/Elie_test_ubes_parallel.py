from bua.utils.utils_import_simulation_steps_and_config_var import *


path_hb_json_folder = r"C:\Users\elie-medioni\AppData\Local\Building_urban_analysis\Libraries\Samples_for_example_file\hbjson_models"

def run_main():
    # Clear simulation temp folder
    SimulationCommonMethods.clear_simulation_temp_folder()
    # Create simulation folder
    SimulationCommonMethods.make_simulation_folder()
    # Create urban_canopy
    urban_canopy_object = SimulationCommonMethods.create_or_load_urban_canopy_object(
        path_simulation_folder=default_path_simulation_folder)

    SimulationLoadBuildingOrGeometry.add_buildings_from_hbjson_to_urban_canopy(
        urban_canopy_object=urban_canopy_object,
        path_folder_hbjson=path_hb_json_folder,
        path_file_hbjson=None,
        are_buildings_targets=True,
        keep_context_from_hbjson=False)



    # Load epw and simulation parameters
    UrbanBuildingEnergySimulationFunctions.load_epw_and_hb_simulation_parameters_for_ubes_in_urban_canopy(
        urban_canopy_obj=urban_canopy_object,
        # path_simulation_folder=default_path_simulation_folder,
        # path_hbjson_simulation_parameter_file=default_path_hbjson_simulation_parameter_file,
        # path_file_epw=default_path_weather_file,
        # ddy_file=None,
        overwrite=True)

    # Write IDF
    UrbanBuildingEnergySimulationFunctions.generate_idf_files_for_ubes_with_openstudio_in_urban_canopy(
        urban_canopy_obj=urban_canopy_object,
        path_simulation_folder=default_path_simulation_folder,
        overwrite=False,
        silent=True)

    # Run IDF through EnergyPlus
    UrbanBuildingEnergySimulationFunctions.run_idf_files_with_energyplus_for_ubes_in_urban_canopy(
        urban_canopy_obj=urban_canopy_object,
        path_simulation_folder=default_path_simulation_folder,
        overwrite=False,
        silent=True)


    # Extract results
    UrbanBuildingEnergySimulationFunctions.extract_results_from_ep_simulation(
        urban_canopy_obj=urban_canopy_object,
        path_simulation_folder=default_path_simulation_folder,
        cop_heating=3., cop_cooling=3.)





    # Export urban_canopy to pickle
    SimulationCommonMethods.save_urban_canopy_object_to_pickle(urban_canopy_object=urban_canopy_object,
                                                               path_simulation_folder=default_path_simulation_folder)
    # Export urban_canopy to json
    SimulationCommonMethods.save_urban_canopy_to_json(urban_canopy_object=urban_canopy_object,
                                                      path_simulation_folder=default_path_simulation_folder)


if __name__ == "__main__":
    run_main()