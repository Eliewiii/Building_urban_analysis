"""
Unit tests for the BUA workflow.
"""

import pytest

from bua.utils.utils_import_simulation_steps_and_config_var import *

from bua.urban_canopy.urban_canopy import UrbanCanopy
from bua.building.building_modeled import BuildingModeled

# Inputs to be used
path_test_gis_folder = r"..\test_files\test_gis"
unit_gis = "deg"

path_test_lb_polyface3d_json = r"..\test_files\test_lb_polyface3d_context.json"

path_test_building_hbjson_0 = r"..\test_files\test_hbjsons\Building_sample_0.hbjson"
path_test_building_hbjson_1 = r"..\test_files\test_hbjsons\Building_sample_3.hbjson"
path_test_building_hbjson_2 = r"..\test_files\test_hbjsons\Building_sample_2.hbjson"



def test_clean_temp_folder_and_make_simulation_folder():
    """
    Check that
    """
    # Clear simulation temp folder
    SimulationCommonMethods.clear_simulation_temp_folder()
    # Create simulation folder
    SimulationCommonMethods.make_simulation_folder(path_simulation_folder=path_simulation_temp_folder)

    urban_canopy_object = SimulationCommonMethods.create_or_load_urban_canopy_object(
        path_simulation_folder=path_simulation_temp_folder)

    # Add HBJSON building to the UrbanCanopy object
    SimulationLoadBuildingOrGeometry.add_buildings_from_hbjson_to_urban_canopy(
        urban_canopy_object=urban_canopy_object,
        path_folder_hbjson=None,
        path_file_hbjson=path_test_building_hbjson_0,
        are_buildings_targets=True,
        keep_context_from_hbjson=False)
    SimulationLoadBuildingOrGeometry.add_buildings_from_hbjson_to_urban_canopy(
        urban_canopy_object=urban_canopy_object,
        path_folder_hbjson=None,
        path_file_hbjson=path_test_building_hbjson_1,
        are_buildings_targets=True,
        keep_context_from_hbjson=False)
    SimulationLoadBuildingOrGeometry.add_buildings_from_hbjson_to_urban_canopy(
        urban_canopy_object=urban_canopy_object,
        path_folder_hbjson=None,
        path_file_hbjson=path_test_building_hbjson_2,
        are_buildings_targets=False,
        keep_context_from_hbjson=False)

    building_ids = list(urban_canopy_object.building_dict.keys())

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
        building_id_list=building_ids,
        overwrite=True,
        silent=True)

    # Run IDF through EnergyPlus
    UrbanBuildingEnergySimulationFunctions.run_idf_files_with_energyplus_for_ubes_in_urban_canopy(
        urban_canopy_obj=urban_canopy_object,
        path_simulation_folder=default_path_simulation_folder,
        building_id_list=building_ids,
        overwrite=True,
        silent=True)

    # Extract results
    UrbanBuildingEnergySimulationFunctions.extract_results_from_ep_simulation(
        urban_canopy_obj=urban_canopy_object,
        path_simulation_folder=default_path_simulation_folder,
        cop_heating=3., cop_cooling=3.)

    # # Write IDF
    # UrbanBuildingEnergySimulationFunctions.generate_idf_files_for_ubes_with_openstudio_in_urban_canopy(
    #     urban_canopy_obj=urban_canopy_object,
    #     path_simulation_folder=default_path_simulation_folder,
    #     building_id_list=[building_ids[1]],
    #     overwrite=False,
    #     silent=True)
    #
    # # Run IDF through EnergyPlus
    # UrbanBuildingEnergySimulationFunctions.run_idf_files_with_energyplus_for_ubes_in_urban_canopy(
    #     urban_canopy_obj=urban_canopy_object,
    #     path_simulation_folder=default_path_simulation_folder,
    #     building_id_list=[building_ids[1]],
    #     overwrite=False,
    #     silent=True)

    # Extract results
    UrbanBuildingEnergySimulationFunctions.extract_results_from_ep_simulation(
        urban_canopy_obj=urban_canopy_object,
        path_simulation_folder=default_path_simulation_folder,
        cop_heating=3., cop_cooling=3.)

    # Save the UrbanCanopy object to a pickle and json files
    SimulationCommonMethods.save_urban_canopy_object_to_pickle(urban_canopy_object=urban_canopy_object,
                                                               path_simulation_folder=path_simulation_temp_folder)
    SimulationCommonMethods.save_urban_canopy_to_json(urban_canopy_object=urban_canopy_object,
                                                      path_simulation_folder=path_simulation_temp_folder)