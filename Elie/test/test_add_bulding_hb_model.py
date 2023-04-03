"""
test, add building HB model to Urban Canopy
"""
from Elie.utils import *

'''
# Inputs
path_folder_test_simulation = "C:\\Users\\elie-medioni\\OneDrive\\OneDrive - Technion\\BUA\\Elie\\Simulation_test"
path_folder_hbjson = "C:\\Users\\elie-medioni\\OneDrive\\OneDrive - Technion\\BUA\\Elie\\Samples\\HB_model"
'''
# path to urban canopy pickle file
path_urban_canopy_pkl = os.path.join(path_folder_test_simulation, "urban_canopy.pkl")

#load the urban canopy
urban_canopy = UrbanCanopy.make_urban_canopy_from_pkl(path_urban_canopy_pkl)
print(urban_canopy)

urban_canopy.add_building_from_hbjson_to_dict(path_folder_hbjson)

urban_canopy.remove_building_from_dict("sample_model")
print("done")