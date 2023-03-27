"""
Load an existing UrbanCanopy object for debugging
"""
import os
from urban_canopy.urban_canopy import UrbanCanopy

# Inputs
# path_folder_simulation = "C:\\Users\\elie-medioni\\OneDrive\\OneDrive - Technion\\BUA\\Elie\\Simulation_test"

local_appdata = os.environ['LOCALAPPDATA']
path_folder_simulation = os.path.join(local_appdata, "Building_urban_analysis","Simulation_temp")
path_urban_canopy_pkl = os.path.join(path_folder_simulation, "urban_canopy.pkl")

path_urban_canopy_pkl = os.path.join(path_folder_simulation, "urban_canopy.pkl")
urban_canopy = UrbanCanopy.make_urban_canopy_from_pkl(path_urban_canopy_pkl)

None