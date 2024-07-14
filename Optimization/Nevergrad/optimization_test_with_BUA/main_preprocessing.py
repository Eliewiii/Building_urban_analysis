from unit_tests.utils_main_import_scripts import *


def preprocessing(path_hbjson_file: str):

    ###############################
    # Initialize the simulation
    ###############################
    # Clear simulation temp folder
    SimulationCommonMethods.clear_simulation_temp_folder()
    # Create simulation folder
    SimulationCommonMethods.make_simulation_folder()
    # Create urban_canopy
    urban_canopy_object = SimulationCommonMethods.create_or_load_urban_canopy_object(
        path_simulation_folder=default_path_simulation_folder)

    ###############################
    # Load Buildings and Context
    ###############################

    # Load Context
    # todo: add for larger simulation

    # Load Buildings from json
    SimulationLoadBuildingOrGeometry.add_buildings_from_hbjson_to_urban_canopy(
        urban_canopy_object=urban_canopy_object,
        path_folder_hbjson=None,
        path_file_hbjson=path_hbjson_file,
        are_buildings_targets=True)

    ###############################
    # Context Selection
    ###############################

    # Perform the Context Selection
    # todo: add for larger simulation


    ###############################
    # UBES Simulation
    ###############################

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

    ###############################
    # Radiation Simulation
    ###############################

    # Merge the face of the buildings to reduce the number of faces and the
    SimulationBuildingManipulationFunctions.make_merged_face_of_buildings_in_urban_canopy(
        urban_canopy_object=urban_canopy_object)
    # Generate the sensor grid
    SimFunSolarRadAndBipv.generate_sensor_grid(urban_canopy_object=urban_canopy_object)
    # Run annual solar irradiance simulation
    SimFunSolarRadAndBipv.run_annual_solar_irradiance_simulation(urban_canopy_object=urban_canopy_object)

    ###############################
    # Export the results
    ###############################

    # Export urban_canopy to pickle
    SimulationCommonMethods.save_urban_canopy_object_to_pickle(urban_canopy_object=urban_canopy_object,
                                                               path_simulation_folder=default_path_simulation_folder)
    # Export urban_canopy to json
    SimulationCommonMethods.save_urban_canopy_to_json(urban_canopy_object=urban_canopy_object,
                                                      path_simulation_folder=default_path_simulation_folder)

if __name__ == "__main__":
    path_hbjson_file = r"C:\Users\elie-medioni\OneDrive\OneDrive - Technion\Ministry of Energy Research\Papers\BIPV extended paper\Simulations\Test_Nevergrad\hbjsons\Buil_TA_0.hbjson"

    preprocessing(path_hbjson_file)