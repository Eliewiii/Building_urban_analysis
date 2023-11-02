from unit_tests.utils_main_import_scripts import *

# Create simulation folder
# SimulationCommonMethods.make_simulation_folder()
# # Create urban_canopy
# urban_canopy_object = SimulationCommonMethods.create_or_load_urban_canopy_object(
#     path_simulation_folder=default_path_simulation_folder)

# Create urban_canopy
path_simulation_folder = r'C:\Users\eliem\Documents\Technion\Simulation_IBPSA\High_Density_Context'
urban_canopy_object = SimulationCommonMethods.create_or_load_urban_canopy_object(
    path_simulation_folder=path_simulation_folder)


print("read")