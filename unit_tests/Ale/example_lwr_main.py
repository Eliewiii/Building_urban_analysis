from unit_tests.utils_main_import_scripts import *

# Clear simulation temp folder
SimulationCommonMethods.clear_simulation_temp_folder()
# Create simulation folder
SimulationCommonMethods.make_simulation_folder()
# Create urban_canopy
urban_canopy_object = SimulationCommonMethods.create_or_load_urban_canopy_object(
    path_simulation_folder=default_path_simulation_folder)

# Load Buildings from json
path_folder_json = "todo :"

SimulationLoadBuildingOrGeometry.add_buildings_from_hbjson_to_urban_canopy(
    urban_canopy_object=urban_canopy_object,
    path_folder_hbjson=path_folder_json,
    are_buildings_targets=True,
    keep_context_from_hbjson=True)

# LWR #

# Generate IDFs
EnergyAndLwrSimulation.generate_idf_file(urban_canopy_object=urban_canopy_object,
                                         path_simulation_folder=default_path_simulation_folder,
                                         time_step=6,
                                         parameter_1=None)

# Generate the FMUs
EnergyAndLwrSimulation.generate_fmus(urban_canopy_object=urban_canopy_object,
                                         path_simulation_folder=default_path_simulation_folder)

#
