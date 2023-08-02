"""
todo
"""

import logging

from building.solar_radiations_and_panel.utils_sensorgrid import generate_sensor_grid_for_hb_model

user_logger = logging.getLogger("user")
dev_logger = logging.getLogger("dev")

empty_parameter_dict = {
    "Roof": {
        "grid_x": None,
        "grid_y": None,
        "offset": None,
        "panel_technology": None
    },
    "Facade": {
        "grid_x": None,
        "grid_y": None,
        "offset": None,
        "panel_technology": None
    },
    "minimum_ratio_energy_harvested_on_primary_energy": None,
    "study_duration_in_years": None,
    "replacement_scenario": {}
}


class SolarRadAndBipvSimulation:
    """

    """

    def __init__(self, do_simulation_on_roof, do_simulation_on_facades):
        """
        todo @Elie
        """
        self.on_roof = do_simulation_on_roof
        self.on_facade = do_simulation_on_facades
        # SensorGrid objects
        self.roof_sensorgrid_dict = None
        self.facade_sensorgrid_dict = None
        # Panel objects
        self.roof_panel_list = None
        self.facade_panel_list = None
        # Results
        self.parameter_dict = empty_parameter_dict

    def add_sensorgrids(self, hb_model_obj, roof_grid_size_x=1, facade_grid_size_x=1, roof_grid_size_y=1,
                        facade_grid_size_y=1, offset_dist=0.1):
        """Create a HoneyBee SensorGrid from a HoneyBe model for the roof, the facades or both and add it to the
        model
        todo @Elie
        :param grid_size : Number for the size of the test grid
        :param offset_dist : Number for the distance to move points from the surfaces of the geometry of the model. Typically, this
        :param on_roof: bool: default=True
        :param on_facades: bool: default=True"""

        if self.on_roof:
            self.roof_sensorgrid_dict = generate_sensor_grid_for_hb_model(hb_model_obj, roof_grid_size_x, roof_grid_size_y, offset_dist, "Roof")
        elif self.on_facade:
            self.facade_sensorgrid_dict = generate_sensor_grid_for_hb_model(hb_model_obj, facade_grid_size_x, facade_grid_size_y, offset_dist, "Facade")


        else:
            user_logger.warning(f"You did not precise whether you want to run the simulation on the roof, "
                                f"the facades or both")
            dev_logger.warning(f"You did not precise whether you want to run the simulation on the roof, "
                               f"the facades or both")
