"""
Load an existing UrbanCanopy object for debugging
"""
import os
from urban_canopy_ubem.urban_canopy import UrbanCanopy

# Inputs
path_folder_simulation = "C:\\Users\\elie-medioni\\OneDrive\\OneDrive - Technion\\BUA\\Elie\\Simulation_test"

path_urban_canopy_pkl = os.path.join(path_folder_simulation, "urban_canopy.pkl")
urban_canopy = UrbanCanopy.from_pkl(path_urban_canopy_pkl)

None