"""
Compute the KPIs of a building.
"""

import logging

from copy import deepcopy

from building.solar_radiation_and_bipv.solar_rad_and_BIPV import compute_cumulative_and_total_value_bipv_result_dict

user_logger = logging.getLogger("user")
dev_logger = logging.getLogger("dev")

empty_sub_bipv_uc_kpi_results_dict = {
    "electricity_harvested_density": {"zone": {"yearly": [], "cumulative": [], "total": 0.0},
                                      "conditioned_apartment": {"yearly": [], "cumulative": [], "total": 0.0}},
    "eroi": {"cumulative": []},
    "ghg_emissions_intensity": {"cumulative": []},
    "electricity_cost": {"cumulative": []},
    "ghg_emissions_offset_from_the_grid": {"yearly": [], "cumulative": [], "total": 0.0},
    "primary_energy_offset_from_the_grid": {"yearly": [], "cumulative": [], "total": 0.0},
    "net_building_electricity_compensation": {"yearly": [], "cumulative": [], "total": 0.0},
    "net_economical_benefit": {"yearly": [], "cumulative": [], "total": 0.0},
    "net_economical_benefit_density": {"zone": {"yearly": [], "cumulative": [], "total": 0.0},
                                       "conditioned_apartment": {"yearly": [], "cumulative": [], "total": 0.0}}
}

empty_bipv_uc_kpi_results_dict = {
    "roof": deepcopy(empty_sub_bipv_uc_kpi_results_dict),
    "facades": deepcopy(empty_sub_bipv_uc_kpi_results_dict),
    "total": deepcopy(empty_sub_bipv_uc_kpi_results_dict)
}


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

        # Location related parameters
        self.grid_ghg_intensity = {"roof": None, "facades": None, "total": None}
        self.grid_energy_intensity = {"roof": None, "facades": None, "total": None}
        self.grid_electricity_cost = {"roof": None, "facades": None, "total": None}
        self.grid_electricity_sell_price = {"roof": None, "facades": None, "total": None}
        self.ubes_electricity_consumption = {"roof": None, "facades": None, "total": None}
        # Zone related parameters
        self.zone_area = None
        self.conditioned_apartment_area = None
        # Flags
        self.has_run = False
        # Intermediate result dictionary
        self.bipv_uc_kpi_results_dict = deepcopy(empty_bipv_uc_kpi_results_dict)
        # Environmental KPIs
        self.eroi = {"roof": None, "facades": None, "total": None}
        self.energy_payback_time = {"roof": None, "facades": None, "total": None}
        self.ghg_emissions_intensity = {"roof": None, "facades": None, "total": None}
        self.ghg_emissions_payback_time = {"roof": None, "facades": None, "total": None}
        # Energy KPIs
        self.harvested_energy_density = {"zone": {"roof": None, "facades": None, "total": None},
                                         "conditioned_apartment": {"roof": None, "facades": None, "total": None}}
        self.net_energy_compensation = {"roof": None, "facades": None, "total": None}
        self.energy_comsumption_density = {"roof": None, "facades": None, "total": None}
        # todo : need proper KPIs for the energy, that are independent of the building/urban size
        # Economic KPIs
        self.net_economical_benefit = {"roof": None, "facades": None, "total": None}
        self.net_economical_benefit_density = {"zone": {"roof": None, "facades": None, "total": None},
                                               "conditioned_apartment": {"roof": None, "facades": None, "total": None}}
        self.economical_payback_time = {"roof": None, "facades": None, "total": None}
        self.initial_investment_per_area = None  # something like this

    def set_parameters(self, grid_ghg_intensity, grid_energy_intensity, grid_electricity_cost,
                       grid_electricity_sell_price, ubes_electricity_consumption, zone_area,
                       conditioned_apartment_area):
        """
        Set the parameters needed for the computation of the KPIs
        :param grid_ghg_intensity: float: the ghg intensity of the grid in kgCO2eq/kWh
        :param grid_energy_intensity: float: the primary energy intensity of the grid in kWh/kWh
        :param grid_electricity_cost: float: the cost of the electricity in USD/kWh
        :param grid_electricity_sell_price: float: the sell price of the electricity in USD/kWh
        :param ubes_electricity_consumption: float: the electricity consumption of the building in kWh
        :param zone_area: float: the area of the zone in m2
        :param conditioned_apartment_area: float: the area of the conditioned apartment in m2
        """
        # Location related parameters
        self.grid_ghg_intensity = grid_ghg_intensity
        self.grid_energy_intensity = grid_energy_intensity
        self.grid_electricity_cost = grid_electricity_cost
        self.grid_electricity_sell_price = grid_electricity_sell_price
        self.ubes_electricity_consumption = ubes_electricity_consumption
        # Area related parameters
        self.zone_area = zone_area
        self.conditioned_apartment_area = conditioned_apartment_area

        # todo, other parameter to consider changes through year of these values, especially due to inflation
        #  and changes in the electricity mix

    def compute_intermediate_results_dict(self, bipv_results_dict):
        """
        Compute the intermediate results of the building.
        :param bipv_results_dict: dictionary, the results of the BIPV simulation
        """
        self.bipv_uc_kpi_results_dict["roof"] = self.compute_intermediate_sub_results_dict(
            bipv_result_dict=bipv_results_dict["roof"])
        self.bipv_uc_kpi_results_dict["facades"] = self.compute_intermediate_sub_results_dict(
            bipv_result_dict=bipv_results_dict["facades"])
        self.bipv_uc_kpi_results_dict["total"] = self.compute_intermediate_sub_results_dict(
            bipv_result_dict=bipv_results_dict["total"])

        self.bipv_uc_kpi_results_dict = compute_cumulative_and_total_value_bipv_result_dict(
            bipv_results_dict=self.bipv_uc_kpi_results_dict)

    def compute_kpis(self, bipv_results_dict):
        """
        Compute the KPIs of the building.
        :param bipv_results_dict: dictionary, the results of the BIPV simulation
        """
        # Elecitricity harvested

        # Primary energy

        # GHG emissions

        # Economical

    def compute_intermediate_sub_results_dict(self, bipv_result_dict):
        """
        Compute the intermediate results of the building.
        :param bipv_result_dict: dictionary, the results of the BIPV simulation
        """
        sub_bipv_uc_kpi_results_dict = deepcopy(empty_sub_bipv_uc_kpi_results_dict)
        # Electricity harvested density
        sub_bipv_uc_kpi_results_dict["electricity_harvested_density"]["zone"]["yearly"] = [
            electricity_harvested / self.zone_area for electricity_harvested in
            bipv_result_dict["energy_harvested"]["zone"]["yearly"]]
        sub_bipv_uc_kpi_results_dict["electricity_harvested_density"]["conditioned_apartment"]["yearly"] = [
            energy_harvested / self.conditioned_apartment_area for energy_harvested in
            bipv_result_dict["energy_harvested"]["conditioned_apartment"]["yearly"]]
        # Intnesity
        sub_bipv_uc_kpi_results_dict["eroi"]["yearly"] = [electricity_harvested / primary_energy_cost for
                                                          electricity_harvested, primary_energy_cost in
                                                          zip(bipv_result_dict["energy_harvested"]["cumulative"],
                                                              bipv_result_dict["primary_energy"]["total"][
                                                                  "cumulative"])]
        sub_bipv_uc_kpi_results_dict["ghg_emissions_intensity"]["yearly"] = [ghg_emissions / electricity_harvested for
                                                                             ghg_emissions, electricity_harvested in
                                                                             zip(bipv_result_dict["ghg_emissions"][
                                                                                     "cumulative"],
                                                                                 bipv_result_dict["energy_harvested"][
                                                                                     "cumulative"])]
        sub_bipv_uc_kpi_results_dict["electricity_cost"]["yearly"] = [bipv_cost / electricity_harvested for
                                                                      bipv_cost, electricity_harvested in
                                                                      zip(bipv_result_dict["cost"]["total"][
                                                                              "cumulative"],
                                                                          bipv_result_dict["energy_harvested"][
                                                                              "cumulative"])]
        # Spared ghg emissions from the grid
        sub_bipv_uc_kpi_results_dict["ghg_emissions_offset_from_the_grid"]["yearly"] = [
            electricity_harvested * self.grid_ghg_intensity for electricity_harvested in
            bipv_result_dict["energy_harvested"]["yearly"]]
        sub_bipv_uc_kpi_results_dict["primary_energy_offset_from_the_grid"]["yearly"] = [
            electricity_harvested * self.grid_energy_intensity for electricity_harvested in
            bipv_result_dict["energy_harvested"]["yearly"]]
        # Net building electricity compensation
        sub_bipv_uc_kpi_results_dict["net_building_electricity_compensation"]["yearly"] = [
            electricity_harvested / self.ubes_electricity_consumption for electricity_harvested in
            bipv_result_dict["energy_harvested"]["yearly"]]
        # Net economical benefit
        sub_bipv_uc_kpi_results_dict["net_economical_benefit"]["yearly"] = [
            electricity_harvested * self.grid_electricity_sell_price - bipv_cost for electricity_harvested, bipv_cost in
            zip(bipv_result_dict["energy_harvested"]["yearly"], bipv_result_dict["cost"]["total"]["yearly"])]
        sub_bipv_uc_kpi_results_dict["net_economical_benefit_density"]["zone"]["yearly"] = [
            net_economical_benefit / self.zone_area for net_economical_benefit in
            sub_bipv_uc_kpi_results_dict["net_economical_benefit"]["yearly"]]
        sub_bipv_uc_kpi_results_dict["net_economical_benefit_density"]["conditioned_apartment"]["yearly"] = [
            net_economical_benefit / self.conditioned_apartment_area for net_economical_benefit in
            sub_bipv_uc_kpi_results_dict["net_economical_benefit"]["yearly"]]

        return sub_bipv_uc_kpi_results_dict
