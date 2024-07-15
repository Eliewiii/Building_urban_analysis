"""
Unit tests for the BUA workflow.
"""

import pytest

from bua.utils.utils_import_simulation_steps_and_config_var import *

from bua.urban_canopy.urban_canopy import UrbanCanopy


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
    path_test_gis_folder = r"..\test_files\test_gis"
    unit_gis = "m"

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

    # Save the UrbanCanopy object to a pickle and json files
    SimulationCommonMethods.save_urban_canopy_object_to_pickle(urban_canopy_object=urban_canopy_object,
                                                               path_simulation_folder=path_simulation_temp_folder)
    SimulationCommonMethods.save_urban_canopy_to_json(urban_canopy_object=urban_canopy_object,
                                                      path_simulation_folder=path_simulation_temp_folder)


def test_load_lb_polyface_3d_json_in_urban_canopy():
    """
    Check that the LB Polyface 3D can be added to UrbanCanopy object
    """
    path_test_lb_polyface3d_json = r"..\test_files\test_lb_polyface3d_context.json"

    # Create an UrabanCanopy object
    urban_canopy_object = SimulationCommonMethods.create_or_load_urban_canopy_object(
        path_simulation_folder=path_simulation_temp_folder)

    # Add LB Polyface 3D to the UrbanCanopy object
    SimulationLoadBuildingOrGeometry.add_buildings_from_lb_polyface3d_json_in_urban_canopy(
        urban_canopy_object=urban_canopy_object,
        path_lb_polyface3d_json_file=path_test_lb_polyface3d_json,
        typology=None,
        other_options_to_generate_building=None)

    # Save the UrbanCanopy object to a pickle and json files
    SimulationCommonMethods.save_urban_canopy_object_to_pickle(urban_canopy_object=urban_canopy_object,
                                                               path_simulation_folder=path_simulation_temp_folder)
    SimulationCommonMethods.save_urban_canopy_to_json(urban_canopy_object=urban_canopy_object,
                                                      path_simulation_folder=path_simulation_temp_folder)


def test_load_building_hbjson_in_urban_canopy():
    """
    Check that the building HBJSON can be added to UrbanCanopy object
    """
    path_test_building_hbjson_1 = r"..\test_files\test_building_1.hbjson"
    path_test_building_hbjson_2 = r"..\test_files\test_building_2.hbjson"

    # Create an UrabanCanopy object
    urban_canopy_object = SimulationCommonMethods.create_or_load_urban_canopy_object(
        path_simulation_folder=path_simulation_temp_folder)

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

    # Save the UrbanCanopy object to a pickle and json files
    SimulationCommonMethods.save_urban_canopy_object_to_pickle(urban_canopy_object=urban_canopy_object,
                                                               path_simulation_folder=path_simulation_temp_folder)
    SimulationCommonMethods.save_urban_canopy_to_json(urban_canopy_object=urban_canopy_object,
                                                      path_simulation_folder=path_simulation_temp_folder)


def test_context_selection():
    """
    Check that the context selection is done correctly
    """

    # Create an UrabanCanopy object
    urban_canopy_object = SimulationCommonMethods.create_or_load_urban_canopy_object(
        path_simulation_folder=path_simulation_temp_folder)

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


    # Save the UrbanCanopy object to a pickle and json files
    SimulationCommonMethods.save_urban_canopy_object_to_pickle(urban_canopy_object=urban_canopy_object,
                                                               path_simulation_folder=path_simulation_temp_folder)
    SimulationCommonMethods.save_urban_canopy_to_json(urban_canopy_object=urban_canopy_object,
                                                      path_simulation_folder=path_simulation_temp_folder)


def test_ubes():
    """
    Check that the UBES simulation is done correctly
    """

    # Create an UrabanCanopy object
    urban_canopy_object = SimulationCommonMethods.create_or_load_urban_canopy_object(
        path_simulation_folder=path_simulation_temp_folder)

    # Save the UrbanCanopy object to a pickle and json files
    SimulationCommonMethods.save_urban_canopy_object_to_pickle(urban_canopy_object=urban_canopy_object,
                                                               path_simulation_folder=path_simulation_temp_folder)
    SimulationCommonMethods.save_urban_canopy_to_json(urban_canopy_object=urban_canopy_object,
                                                      path_simulation_folder=path_simulation_temp_folder)


def test_mesh_generation():
    """
    Check that the mesh generation is done correctly
    """

    # Create an UrabanCanopy object
    urban_canopy_object = SimulationCommonMethods.create_or_load_urban_canopy_object(
        path_simulation_folder=path_simulation_temp_folder)

    # Save the UrbanCanopy object to a pickle and json files
    SimulationCommonMethods.save_urban_canopy_object_to_pickle(urban_canopy_object=urban_canopy_object,
                                                               path_simulation_folder=path_simulation_temp_folder)
    SimulationCommonMethods.save_urban_canopy_to_json(urban_canopy_object=urban_canopy_object,
                                                      path_simulation_folder=path_simulation_temp_folder)


def test_radiation_simulation():
    """
    Check that the radiation simulation is done correctly
    """

    # Create an UrabanCanopy object
    urban_canopy_object = SimulationCommonMethods.create_or_load_urban_canopy_object(
        path_simulation_folder=path_simulation_temp_folder)

    # Save the UrbanCanopy object to a pickle and json files
    SimulationCommonMethods.save_urban_canopy_object_to_pickle(urban_canopy_object=urban_canopy_object,
                                                               path_simulation_folder=path_simulation_temp_folder)
    SimulationCommonMethods.save_urban_canopy_to_json(urban_canopy_object=urban_canopy_object,
                                                      path_simulation_folder=path_simulation_temp_folder)


def test_bipv_simulation():
    """
    Check that the BIPV simulation is done correctly
    """

    # Create an UrabanCanopy object
    urban_canopy_object = SimulationCommonMethods.create_or_load_urban_canopy_object(
        path_simulation_folder=path_simulation_temp_folder)

    # Save the UrbanCanopy object to a pickle and json files
    SimulationCommonMethods.save_urban_canopy_object_to_pickle(urban_canopy_object=urban_canopy_object,
                                                               path_simulation_folder=path_simulation_temp_folder)
    SimulationCommonMethods.save_urban_canopy_to_json(urban_canopy_object=urban_canopy_object,
                                                      path_simulation_folder=path_simulation_temp_folder)


def test_kpi_extraction():
    """
    Check that the KPI extraction is done correctly
    """

    # Create an UrabanCanopy object
    urban_canopy_object = SimulationCommonMethods.create_or_load_urban_canopy_object(
        path_simulation_folder=path_simulation_temp_folder)

    # Save the UrbanCanopy object to a pickle and json files
    SimulationCommonMethods.save_urban_canopy_object_to_pickle(urban_canopy_object=urban_canopy_object,
                                                               path_simulation_folder=path_simulation_temp_folder)
    SimulationCommonMethods.save_urban_canopy_to_json(urban_canopy_object=urban_canopy_object,
                                                      path_simulation_folder=path_simulation_temp_folder)
