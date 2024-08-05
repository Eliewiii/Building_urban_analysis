from bua.utils.utils_import_simulation_steps_and_config_var import *


def test_generate_mesh():
    # Create simulation folder
    SimulationCommonMethods.make_simulation_folder()
    # Create urban_canopy
    urban_canopy_object = SimulationCommonMethods.create_or_load_urban_canopy_object(
        path_simulation_folder=default_path_simulation_folder)

    # Generate the sensor grid
    SimFunSolarRadAndBipv.generate_sensor_grid(
        urban_canopy_object=urban_canopy_object,
        bipv_on_roof=True,
        bipv_on_facades=True,
        roof_grid_size_x=2.05,
        facades_grid_size_x=2.05,
        roof_grid_size_y=1.05,
        facades_grid_size_y=0.9,
        offset_dist=0.1,
        overwrite=True
    )

    # Export urban_canopy to pickle
    SimulationCommonMethods.save_urban_canopy_object_to_pickle(
        urban_canopy_object=urban_canopy_object,
        path_simulation_folder=default_path_simulation_folder
    )
    # Export urban_canopy to json
    SimulationCommonMethods.save_urban_canopy_to_json(urban_canopy_object=urban_canopy_object,
                                                      path_simulation_folder=default_path_simulation_folder)
