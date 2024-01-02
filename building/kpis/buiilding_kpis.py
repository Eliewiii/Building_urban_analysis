"""
Compute the KPIs of a building.
"""

import logging

from copy import deepcopy

user_logger = logging.getLogger("user")
dev_logger = logging.getLogger("dev")


class BuildingKPIs:
    """
    Class to perform the energy simulation of a building using the EnergyPlus software and saves the results in a
    dictionary.
    """

    def __init__(self, building_id):
        """
        Initialize the BuildingKPIs class.
        :param building_id: str, id of the building the object belongs to
        """

        self.building_id = building_id
        # Parameters

        # Flags
        self.has_run = False
        # Environmental KPIs
        self.eroi = None
        self.energy_payback_time = None
        self.ghg_emissions_intensity = None
        self.ghg_emissions_payback_time = None
        # Energy KPIs
        self.harvested_energy_density = None
        self.net_energy_compensation = None
        self.energy_comsumption_density = None
        # todo : need proper KPIs for the energy, that are independent of the building/urban size
        # Economic KPIs
        self.net_economical_benefit = None
        self.net_economical_benefit_density = None  # ?
        self.economical_payback_time = None
        self.initial_investment_per_area = None  # something like this


