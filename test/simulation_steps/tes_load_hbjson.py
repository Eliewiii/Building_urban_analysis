"""
Unit tests for Loading HBjson in an Urban Canopy object.
"""
import os

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


def load_hbjson(path_hbjson_file=path_test_building_hbjson_0):
    """
    Check that
    """

    urban_canopy_object = UrbanCanopy()
    print(path_hbjson_file)

    SimulationLoadBuildingOrGeometry.add_buildings_from_hbjson_to_urban_canopy(
        urban_canopy_object=urban_canopy_object,
        path_folder_hbjson=None,
        path_file_hbjson=path_hbjson_file,
        are_buildings_targets=True,
        keep_context_from_hbjson=False)

    print(list(urban_canopy_object.building_dict.values())[0].lb_face_footprint)

def load_hbjson_folder(path_folder_hbjson):
    """
    Check that
    """

    urban_canopy_object = UrbanCanopy()

    SimulationLoadBuildingOrGeometry.add_buildings_from_hbjson_to_urban_canopy(
        urban_canopy_object=urban_canopy_object,
        path_folder_hbjson=path_folder_hbjson,
        path_file_hbjson=None,
        are_buildings_targets=True,
        keep_context_from_hbjson=False)

    SimulationCommonMethods.save_urban_canopy_to_json(urban_canopy_object, path_folder_hbjson)


if __name__ == '__main__':
    path_folder_hbjson_to_test = r"C:\Users\elie-medioni\OneDrive\OneDrive - Technion\BUA\Issues\Issue_Abraham_24_07_17\_No_Context"
    # list_path_hbjson_to_test = os.listdir(path_folder_hbjson_to_test)
    # for path_hbjson_to_test in list_path_hbjson_to_test:
    #     load_hbjson(path_hbjson_file=os.path.join(path_folder_hbjson_to_test, path_hbjson_to_test))

    load_hbjson_folder(path_folder_hbjson=path_folder_hbjson_to_test)
