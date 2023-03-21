"""
test, add building HB model to Urban Canopy
"""
import os
from urban_canopy_ubem.urban_canopy import UrbanCanopy

# Inputs
path_folder_simulation = "C:\\Users\\elie-medioni\\OneDrive\\OneDrive - Technion\\BUA\\Elie\\Simulation_test"
path_folder_hbjson = "C:\\Users\\elie-medioni\\OneDrive\\OneDrive - Technion\\BUA\\Elie\\Samples\\hb_model"

# path to urban canopy pickle file
path_urban_canopy_pkl = os.path.join(path_folder_simulation, "urban_canopy.pkl")

#load the urban canopy
urban_canopy = UrbanCanopy.from_pkl(path_urban_canopy_pkl)
print(urban_canopy)

urban_canopy.add_building_from_hbjsons(path_folder_hbjson)

urban_canopy.remove_building("sample_model")
print("done")