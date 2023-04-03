import os
from urban_canopy.urban_canopy_methods import UrbanCanopy


# Inputs
path_folder_test_simulation = "C:\\Users\\elie-medioni\\OneDrive\\OneDrive - Technion\\BUA\\Elie\\Simulation_test"
path_folder_hbjson = "C:\\Users\\elie-medioni\\OneDrive\\OneDrive - Technion\\BUA\\Elie\\Samples\\HB_model"

# Inputs
# path_folder_simulation = "C:\\Users\\elie-medioni\\OneDrive\\OneDrive - Technion\\BUA\\Elie\\Simulation_test"

local_appdata = os.environ['LOCALAPPDATA']
path_folder_simulation = os.path.join(local_appdata, "Building_urban_analysis","Simulation_temp")
path_urban_canopy_pkl = os.path.join(path_folder_simulation, "urban_canopy.pkl")