"""
Performs the energy simulation of a building using the EnergyPlus software and saves the results in a dictionary.
"""

import logging

from copy import deepcopy

user_logger = logging.getLogger("user")
dev_logger = logging.getLogger("dev")

empty_bes_results_dict = {
    "heating": {"monthly": [], "monthly_cumulative": [], "yearly": None},
    "cooling": {"monthly": [], "monthly_cumulative": [], "yearly": None},
    "equipment": {"monthly": [], "monthly_cumulative": [], "yearly": None},
    "lighting": {"monthly": [], "monthly_cumulative": [], "yearly": None},
    "ventilation": {"monthly": [], "monthly_cumulative": [], "yearly": None},  # Unused for now
    "total": {"monthly": [], "monthly_cumulative": [], "yearly": None}
}


class BuildingEnergySimulation:
    """
    Class to perform the energy simulation of a building using the EnergyPlus software and saves the results in a
    dictionary.
    """

    def __init__(self, building_id):
        """
        Initialize the BuildingEnergySimulation class.
        :param building_id: str, id of the building the object belongs to
        """

        self.building_id = building_id
        # Parameters
        self.simulation_parameters = None
        self.epw_name = None
        self.cop_heating = None
        self.cop_cooling = None
        # Flags
        self.has_run = False
        # Results
        self.bes_results_dict = deepcopy(empty_bes_results_dict)

