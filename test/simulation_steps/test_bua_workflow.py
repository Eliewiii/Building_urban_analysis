"""
Unit tests for the BUA workflow.
"""

import pytest

from bua.utils.utils_import_simulation_steps_and_config_var import *

from bua.urban_canopy.urban_canopy import UrbanCanopy

# Inputs to be used
path_test_gis_folder = r"..\test_files\test_gis"
unit_gis = "m"

path_test_lb_polyface3d_json = r"..\test_files\test_lb_polyface3d_context.json"
path_test_building_hbjson_1 = r"..\test_files\test_hbjsons\Building_sample_0.hbjson.hbjson"
path_test_building_hbjson_2 = r"..\test_files\test_hbjsons\Building_sample_1.hbjson.hbjson"


def test_clean_temp_folder_and_make_simulation_folder():
    """
    Check that
    """
    # Clear simulation temp folder
    SimulationCommonMethods.clear_simulation_temp_folder()
    assert os.path.listdir(default_path_simulation_folder) is []
    # Create simulation folder
    SimulationCommonMethods.make_simulation_folder(path_simulation_folder=path_simulation_temp_folder)
    assert os.isdir(os.path.join(path_simulation_temp_folder, name_gh_components_logs_folder))
    assert os.isdir(os.path.join(path_simulation_temp_folder, name_temporary_files_folder))


def test_make_and_save_urban_canopy_object():
    """
    Check that an UrbanCanopy object is created
    """
    # Create an UrabanCanopy object
    urban_canopy_object = SimulationCommonMethods.create_or_load_urban_canopy_object(
        path_simulation_folder=path_simulation_temp_folder)
    assert isinstance(urban_canopy_object, UrbanCanopy)
    # Save the UrbanCanopy object to a pickle and json files
    SimulationCommonMethods.save_urban_canopy_object_to_pickle(urban_canopy_object=urban_canopy_object,
                                                               path_simulation_folder=path_simulation_temp_folder)
    assert os.isfile(os.path.join(path_simulation_temp_folder, "urban_canopy.pkl"))
    SimulationCommonMethods.save_urban_canopy_to_json(urban_canopy_object=urban_canopy_object,
                                                      path_simulation_folder=path_simulation_temp_folder)
    assert os.isfile(os.path.join(path_simulation_temp_folder, "urban_canopy.json"))


def test_load_gis_in_urban_canopy():
    """
    Check that the GIS data is added to the UrbanCanopy object
    """

    ###############################
    # Load GIS data
    ###############################

    # Create an UrabanCanopy object
    urban_canopy_object = SimulationCommonMethods.create_or_load_urban_canopy_object(
        path_simulation_folder=path_simulation_temp_folder)

    # Add GIS data to the UrbanCanopy object
    SimulationLoadBuildingOrGeometry.add_2D_GIS_to_urban_canopy(urban_canopy=urban_canopy_object,
                                                                path_gis=path_test_gis_folder,
                                                                path_additional_gis_attribute_key_dict=
                                                                None,
                                                                unit=unit_gis)
    SimulationBuildingManipulationFunctions.move_buildings_to_origin(urban_canopy_object=urban_canopy_object)

    # Tests
    # todo

    ###############################
    # Load Breps from Polyface3D
    ###############################

    # Add LB Polyface 3D to the UrbanCanopy object
    SimulationLoadBuildingOrGeometry.add_buildings_from_lb_polyface3d_json_in_urban_canopy(
        urban_canopy_object=urban_canopy_object,
        path_lb_polyface3d_json_file=path_test_lb_polyface3d_json,
        typology=None,
        other_options_to_generate_building=None)

    ###############################
    # Load HBJSONs
    ###############################

    # Add HBJSON building to the UrbanCanopy object
    SimulationLoadBuildingOrGeometry.add_buildings_from_hbjson_to_urban_canopy(
        urban_canopy_object=urban_canopy_object,
        path_folder_hbjson=None,
        path_file_hbjson=path_test_building_hbjson_1,
        are_buildings_targets=False,
        keep_context_from_hbjson=False)
    SimulationLoadBuildingOrGeometry.add_buildings_from_hbjson_to_urban_canopy(
        urban_canopy_object=urban_canopy_object,
        path_folder_hbjson=None,
        path_file_hbjson=path_test_building_hbjson_2,
        are_buildings_targets=False,
        keep_context_from_hbjson=False)

    # Tests
    assert len(urban_canopy_object.buildings) == 2
    # todo: more tests, with lovers, user cintext etc.

    ###############################
    # Context Selection
    ###############################

    # Generate Bounding Boxes
    SimulationBuildingManipulationFunctions.make_oriented_bounding_boxes_of_buildings_in_urban_canopy(
        urban_canopy_object=urban_canopy_object, overwrite=True)

    # Merge faces of buildings
    SimulationBuildingManipulationFunctions.make_merged_face_of_buildings_in_urban_canopy(
        urban_canopy_object=urban_canopy_object,
        orient_roof_mesh_to_according_to_building_orientation=True,
        overwrite=True)

    # Perform the first pass of context filtering
    SimulationContextFiltering.perform_first_pass_of_context_filtering_on_buildings(
        urban_canopy_object=urban_canopy_object,
        min_vf_criterion=0.01,
        overwrite=True)

    # Tests for the first pass of context filtering
    # todo

    # Perform the second pass of context filtering
    SimulationContextFiltering.perform_second_pass_of_context_filtering_on_buildings(
        urban_canopy_object=urban_canopy_object,
        number_of_rays= 3,
        consider_windows=True,
        keep_shades_from_user=False,
        no_ray_tracing=False,
        overwrite=True,
        keep_discarded_faces=False)

    # Tests for the second pass of context filtering
    # todo

    ###############################
    # UBES
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

    # Test
    # todo

    ###############################
    # BIPV simulation
    ###############################

    # Generate the sensor grids
    SimFunSolarRadAndBipv.generate_sensor_grid(
        urban_canopy_object=urban_canopy_object,
        bipv_on_roof=True,
        bipv_on_facades=True,
        roof_grid_size_x=default_roof_grid_size_x,
        facades_grid_size_x=default_facades_grid_size_x,
        roof_grid_size_y=default_roof_grid_size_y,
        facades_grid_size_y=default_facades_grid_size_y,
        offset_dist=default_offset_dist,
        overwrite=True
    )

    # Test
    # todo

    # Run Solar Radiation Simulation
    SimFunSolarRadAndBipv.run_solar_radiation_simulation(
        urban_canopy_object=urban_canopy_object,
        path_simulation_folder=default_path_simulation_folder,
        path_weather_file=default_path_weather_file,
        overwrite=True)

    # Test
    # todo

    # Run BIPV Simulation
    SimFunSolarRadAndBipv.run_bipv_simulation(
        urban_canopy_object=urban_canopy_object,
        path_simulation_folder=default_path_simulation_folder,
        bipv_scenario_identifier=default_bipv_scenario_identifier,
        roof_id_pv_tech=default_id_pv_tech_roof,
        facades_id_pv_tech=default_id_pv_tech_facades,
        roof_transport_id=default_roof_transport_id,
        facades_transport_id=default_facades_transport_id,
        roof_inverter_id=default_roof_inverter_id,
        facades_inverter_id=default_facades_inverter_id,
        roof_inverter_sizing_ratio=default_roof_inverter_sizing_ratio,
        facades_inverter_sizing_ratio=default_facades_inverter_sizing_ratio,
        minimum_panel_eroi=1.5,
        start_year=0,
        end_year=30,
        replacement_scenario=default_replacement_scenario,
        continue_simulation=False,
        replacement_frequency=25
    )
    # Test
    # todo

    # Run KPI computation
    SimFunSolarRadAndBipv.run_kpi_simulation(
        urban_canopy_object=urban_canopy_object,
        path_simulation_folder=default_path_simulation_folder,
        bipv_scenario_identifier=default_bipv_scenario_identifier,
        grid_ghg_intensity=default_grid_ghg_intensity,
        grid_energy_intensity=default_grid_energy_intensity,
        grid_electricity_sell_price=default_grid_electricity_sell_price,
        zone_area=None
    )

    # Test
    # todo


    # Save the UrbanCanopy object to a pickle and json files
    SimulationCommonMethods.save_urban_canopy_object_to_pickle(urban_canopy_object=urban_canopy_object,
                                                               path_simulation_folder=path_simulation_temp_folder)
    SimulationCommonMethods.save_urban_canopy_to_json(urban_canopy_object=urban_canopy_object,
                                                      path_simulation_folder=path_simulation_temp_folder)
