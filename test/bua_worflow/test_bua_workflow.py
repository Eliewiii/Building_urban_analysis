"""
Unit tests for the BUA workflow.
"""

import pytest

from bua.utils.utils_import_simulation_step_and_config_variables import *

from bua.urban_canopy.urban_canopy import UrbanCanopy


def test_clean_temp_folder():
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
