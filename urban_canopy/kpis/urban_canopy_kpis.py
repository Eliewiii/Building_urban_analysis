"""
Compute the KPIs of a building.
"""

import logging

from copy import deepcopy

user_logger = logging.getLogger("user")
dev_logger = logging.getLogger("dev")


class UrbanCanopyKPIs:
    """
    Class to perform the energy simulation of a building using the EnergyPlus software and saves the results in a
    dictionary.
    """

    def __init__(self):
        """
        Initialize the BuildingKPIs class.
        :param building_id: str, id of the building the object belongs to
        """

        # Parameters
        self.grid_ghg_intensity = None
        self.grid_energy_intensity = None
        self.grid_energy_cost = None
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

    def set_parameters(self, grid_ghg_intensity, grid_energy_intensity, grid_energy_cost):
        """
        Set the parameters needed for the computation of the KPIs
        """
        self.grid_ghg_intensity = grid_ghg_intensity
        self.grid_energy_intensity = grid_energy_intensity
        self.grid_energy_cost = grid_energy_cost

    def compute_kpis(self, bes_result_dict,bipv_results_dict ):
        """
        Compute the KPIs of the building.
        :param building_energy_simulation: BuildingEnergySimulation object, the energy simulation of the building
        """




