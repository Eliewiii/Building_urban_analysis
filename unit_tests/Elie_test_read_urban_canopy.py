from unit_tests.utils_main_import_scripts import *

# Create simulation folder
SimulationCommonMethods.make_simulation_folder()
# # Create urban_canopy
# urban_canopy_object = SimulationCommonMethods.create_or_load_urban_canopy_object(
#     path_simulation_folder=default_path_simulation_folder)

# Create urban_canopy
path_simulation_folder = r'C:\Users\eliem\OneDrive - Technion\Ministry of Energy Research\IBPSA US conference\TA_Neighborhood_27.9.2023\Sim_8.10.23'
urban_canopy_object = SimulationCommonMethods.create_or_load_urban_canopy_object(
    path_simulation_folder=path_simulation_folder)


print("read")