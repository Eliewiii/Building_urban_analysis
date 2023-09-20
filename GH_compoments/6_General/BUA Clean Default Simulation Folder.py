"""Clean the default simulation folder.
    Inputs:
        _run: Set to True to run the component"""

__author__ = "Eliewiii"
__version__ = "2023.08.22"

ghenv.Component.Name = "BUA Clean Default Simulation Folder"
ghenv.Component.NickName = 'CleanDefaultSimulationFolder'
ghenv.Component.Message = '0.0.0'
ghenv.Component.Category = 'BUA'
ghenv.Component.SubCategory = '6 :: General'
ghenv.Component.AdditionalHelpFromDocStrings = "1"

import shutil
import os

local_appdata = os.environ['LOCALAPPDATA']
path_tool = os.path.join(local_appdata, "Building_urban_analysis")
path_simulation_temp_folder = os.path.join(path_tool, "Simulation_temp")

if _run:
    if os.path.isdir(path_simulation_temp_folder):
        shutil.rmtree(path_simulation_temp_folder)
    os.makedirs(path_simulation_temp_folder)