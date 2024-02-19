"""
Compute the KPIs of a building.
"""

import logging

from copy import deepcopy

from building.solar_radiation_and_bipv.solar_rad_and_BIPV import \
    compute_cumulative_and_total_value_bipv_result_dict

user_logger = logging.getLogger("user")
dev_logger = logging.getLogger("dev")

empty_sub_bipv_uc_kpi_results_dict = {
    "electricity_harvested_density": {"zone": {"yearly": [], "cumulative": [], "total": 0.0},
                                      "conditioned_apartment": {"yearly": [], "cumulative": [],
                                                                "total": 0.0}},
    "eroi": {"cumulative": []},
    "ghg_emissions_intensity": {"cumulative": []},
    "electricity_cost": {"cumulative": []},
    "ghg_emissions_offset_from_the_grid": {"yearly": [], "cumulative": [], "total": 0.0},
    "primary_energy_offset_from_the_grid": {"yearly": [], "cumulative": [], "total": 0.0},
    "net_building_electricity_compensation": {"yearly": [], "cumulative": [], "total": 0.0},
    "net_economical_income": {"yearly": [], "cumulative": [], "total": 0.0},
    "net_economical_benefit": {"yearly": [], "cumulative": [], "total": 0.0},
    "net_economical_benefit_density": {"zone": {"yearly": [], "cumulative": [], "total": 0.0},
                                       "conditioned_apartment": {"yearly": [], "cumulative": [],
                                                                 "total": 0.0}}
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
        self.grid_ghg_intensity = None
        self.grid_energy_intensity = None
        # self.grid_electricity_cost = None
        self.grid_electricity_sell_price = None
        # UBES related parameters
        self.ubes_electricity_consumption = None
        # Zone related parameters
        self.zone_area = None
        self.conditioned_apartment_area = None
        # Flags
        self.has_run = False
        # Intermediate result dictionary
        self.bipv_uc_kpi_results_dict = deepcopy(empty_bipv_uc_kpi_results_dict)
        # Environmental KPIs
        self.eroi = {"roof": None, "facades": None, "total": None}
        self.primary_energy_payback_time = {"roof": None, "facades": None, "total": None}
        self.ghg_emissions_intensity = {"roof": None, "facades": None, "total": None}
        self.ghg_emissions_payback_time = {"roof": None, "facades": None, "total": None}
        # Energy KPIs
        self.harvested_energy_density = {"zone": {"roof": None, "facades": None, "total": None},
                                         "conditioned_apartment": {"roof": None, "facades": None,
                                                                   "total": None}}
        self.net_energy_compensation = {"roof": None, "facades": None, "total": None}
        # todo : need proper KPIs for the energy, that are independent of the building/urban size
        # Economic KPIs
        self.net_economical_benefit = {"roof": None, "facades": None, "total": None}
        self.net_economical_benefit_density = {"zone": {"roof": None, "facades": None, "total": None},
                                               "conditioned_apartment": {"roof": None, "facades": None,
                                                                         "total": None}}
        self.economical_payback_time = {"roof": None, "facades": None, "total": None}
        self.initial_investment_per_area = None  # something like this

    def set_parameters(self, grid_ghg_intensity, grid_energy_intensity, grid_electricity_sell_price,
                       ubes_electricity_consumption, zone_area, conditioned_apartment_area):
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
        # self.grid_electricity_cost = grid_electricity_cost
        self.grid_electricity_sell_price = grid_electricity_sell_price
        self.ubes_electricity_consumption = ubes_electricity_consumption
        # Area related parameters
        self.zone_area = zone_area
        self.conditioned_apartment_area = conditioned_apartment_area

        # todo, other parameter to consider changes through year of these values, especially due to inflation
        #  and changes in the electricity mix

    def to_dict(self):
        """
        Convert the object to a dictionary to save it in a json file.
        :return: dict, the dictionary representing the object
        """
        # todo @Elie

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
        # Roof
        self.compute_sub_kpis(bipv_result_dict=bipv_results_dict["roof"], sub_type="roof")
        # Facades
        self.compute_sub_kpis(bipv_result_dict=bipv_results_dict["facades"], sub_type="facades")
        # Total
        self.compute_sub_kpis(bipv_result_dict=bipv_results_dict["total"], sub_type="total")

    def compute_sub_kpis(self, bipv_result_dict, sub_type):
        """

        """
        # Elecitricity harvested
        self.harvested_energy_density["zone"][sub_type] = \
            self.bipv_uc_kpi_results_dict[sub_type]["electricity_harvested_density"]["zone"][
                "cumulative"][-1]
        self.harvested_energy_density["conditioned_apartment"][sub_type] = \
            self.bipv_uc_kpi_results_dict[sub_type]["electricity_harvested_density"][
                "conditioned_apartment"]["cumulative"][-1]
        self.net_energy_compensation[sub_type] = \
            self.bipv_uc_kpi_results_dict[sub_type]["net_energy_compensation"]["cumulative"][-1]
        # Primary energy
        self.primary_energy_payback_time[sub_type] = self.compute_primary_energy_payback_time(
            cumulative_annual_cost_list=bipv_result_dict["primary_energy"]["total"]["cumulative"],
            cumulative_annual_offset_list=
            self.bipv_uc_kpi_results_dict[sub_type]["primary_energy_offset_from_the_grid"][
                "cumulative"])
        self.eroi[sub_type] = self.bipv_uc_kpi_results_dict[sub_type]["eroi"]["cumulative"][-1]
        # GHG emissions
        self.ghg_emission_payback_time[sub_type] = self.compute_ghg_emission_payback_time(
            cumulative_annual_cost_list=bipv_result_dict["ghg"]["total"]["cumulative"],
            cumulative_annual_offset_list=
            self.bipv_uc_kpi_results_dict[sub_type]["ghg_emissions_offset_from_the_grid"][
                "cumulative"])
        self.ghg_emissions_intensity[sub_type] = \
            self.bipv_uc_kpi_results_dict[sub_type]["ghg_emissions_intensity"][
                "cumulative"][-1]
        # Economical
        self.economical_benefit[sub_type] = self.compute_net_economical_benefit(
            cumulative_annual_cost_list=bipv_result_dict["cost"]["total"]["cumulative"],
            cumulative_annual_offset_list=self.bipv_uc_kpi_results_dict[sub_type]["net_economical_income"][
                "cumulative"])
        self.net_economical_benefit[sub_type] = \
            self.bipv_uc_kpi_results_dict[sub_type]["net_economical_benefit"][
                "cumulative"][-1]
        self.net_economical_benefit_density[sub_type] = self.bipv_uc_kpi_results_dict[sub_type][
            "net_economical_benefit_density"]["cumulative"][-1]

    def compute_intermediate_sub_results_dict(self, bipv_result_dict):
        """
        Compute the intermediate results of the building.
        :param bipv_result_dict: dictionary, the results of the BIPV simulation
        """
        sub_bipv_uc_kpi_results_dict = deepcopy(empty_sub_bipv_uc_kpi_results_dict)
        # Electricity harvested density
        if self.zone_area is not None:
            sub_bipv_uc_kpi_results_dict["electricity_harvested_density"]["zone"]["yearly"] = [
                electricity_harvested / self.zone_area for electricity_harvested in
                bipv_result_dict["energy_harvested"]["zone"]["yearly"]]
        sub_bipv_uc_kpi_results_dict["electricity_harvested_density"]["conditioned_apartment"]["yearly"] = [
            energy_harvested / self.conditioned_apartment_area for energy_harvested in
            bipv_result_dict["energy_harvested"]["conditioned_apartment"]["yearly"]]
        # Intensity
        sub_bipv_uc_kpi_results_dict["eroi"]["cumulative"] = [electricity_harvested / primary_energy_cost for
                                                              electricity_harvested, primary_energy_cost in
                                                              zip(bipv_result_dict["energy_harvested"][
                                                                      "cumulative"],
                                                                  bipv_result_dict["primary_energy"]["total"][
                                                                      "cumulative"])]
        sub_bipv_uc_kpi_results_dict["ghg_emissions_intensity"]["cumulative"] = [
            ghg_emissions / electricity_harvested for
            ghg_emissions, electricity_harvested in
            zip(bipv_result_dict["ghg_emissions"][
                    "cumulative"],
                bipv_result_dict["energy_harvested"][
                    "cumulative"])]
        sub_bipv_uc_kpi_results_dict["electricity_cost"]["cumulative"] = [bipv_cost / electricity_harvested
                                                                          for
                                                                          bipv_cost, electricity_harvested in
                                                                          zip(bipv_result_dict["cost"][
                                                                                  "total"][
                                                                                  "cumulative"],
                                                                              bipv_result_dict[
                                                                                  "energy_harvested"][
                                                                                  "cumulative"])]
        # Spared ghg emissions from the grid
        sub_bipv_uc_kpi_results_dict["ghg_emissions_offset_from_the_grid"]["yearly"] = [
            electricity_harvested * self.grid_ghg_intensity for electricity_harvested in
            bipv_result_dict["energy_harvested"]["yearly"]]
        sub_bipv_uc_kpi_results_dict["primary_energy_offset_from_the_grid"]["yearly"] = [
            electricity_harvested * self.grid_energy_intensity for electricity_harvested in
            bipv_result_dict["energy_harvested"]["yearly"]]
        # Net building electricity compensation
        if self.ubes_electricity_consumption > 0: # to avoid division by zero if UBES did not run
            ubes_electricity_consumption = self.ubes_electricity_consumption
        else:
            ubes_electricity_consumption = 1.
        sub_bipv_uc_kpi_results_dict["net_building_electricity_compensation"]["yearly"] = [
            electricity_harvested / ubes_electricity_consumption for electricity_harvested in
            bipv_result_dict["energy_harvested"]["yearly"]]
        # Net economical benefit
        sub_bipv_uc_kpi_results_dict["net_economical_income"]["yearly"] = [
            electricity_harvested * self.grid_electricity_sell_price for electricity_harvested in
            bipv_result_dict["energy_harvested"]["yearly"]]
        sub_bipv_uc_kpi_results_dict["net_economical_benefit"]["yearly"] = [
            electricity_harvested * self.grid_electricity_sell_price - bipv_cost for
            electricity_harvested, bipv_cost in
            zip(bipv_result_dict["energy_harvested"]["yearly"], bipv_result_dict["cost"]["total"]["yearly"])]
        if self.zone_area is not None:
            sub_bipv_uc_kpi_results_dict["net_economical_benefit_density"]["zone"]["yearly"] = [
                net_economical_benefit / self.zone_area for net_economical_benefit in
                sub_bipv_uc_kpi_results_dict["net_economical_benefit"]["yearly"]]
        sub_bipv_uc_kpi_results_dict["net_economical_benefit_density"]["conditioned_apartment"]["yearly"] = [
            net_economical_benefit / self.conditioned_apartment_area for net_economical_benefit in
            sub_bipv_uc_kpi_results_dict["net_economical_benefit"]["yearly"]]

        return sub_bipv_uc_kpi_results_dict

    @staticmethod
    def compute_pay_back_time(cumulative_annual_cost_list, cumulative_annual_offset_list):
        """
        Compute a payback time for the BIPV installation.
        :param cumulative_annual_cost_list: list, the cumulative annual cost (in primary energy, ghg or money)
         of the BIPV installation.
        :param cumulative_annual_offset_list: list, the cumulative annual offset of the BIPV installation
        """
        if cumulative_annual_offset_list[-1] < cumulative_annual_cost_list[-1]:
            return False
        for year in range(len(cumulative_annual_cost_list) - 2, -1,
                          -1):  # from the last year to the first year
            if cumulative_annual_cost_list[year] < cumulative_annual_offset_list[year]:
                """
                We need to shift the years by 1 because the indexes refer to what is produced/generated 
                during the year, and thus cumulated values are obtained at the end of each year.
                """
                # Linear interpolation to find the payback time
                line1 = ((year + 1, cumulative_annual_cost_list[year]),
                         (year + 2, cumulative_annual_cost_list[year + 1]))
                line2 = ((year + 1, cumulative_annual_offset_list[year]),
                         (year + 2, cumulative_annual_offset_list[year + 1]))
                [pay_back_time, cost] = line_intersection(line1, line2)
                return pay_back_time
        # If the payback time is not found it means the values were compensated at he begining
        return 0


def line_intersection(line1, line2):
    """
    Compute the intersection of two lines.
    :param line1: tuple of tuple, the first line ((x1,y1),(x2,y2))
    :param line2: tuple of tuple, the second line ((x3,y3),(x4,y4))
    :return: list, the intersection point
    """
    xdiff = (line1[0][0] - line1[1][0], line2[0][0] - line2[1][0])
    ydiff = (line1[0][1] - line1[1][1], line2[0][1] - line2[1][1])

    def det(a, b):
        return a[0] * b[1] - a[1] * b[0]

    div = det(xdiff, ydiff)
    if div == 0:
        raise Exception('lines do not intersect')

    d = (det(*line1), det(*line2))
    x = det(d, xdiff) / div
    y = det(d, ydiff) / div
    return [x, y]
