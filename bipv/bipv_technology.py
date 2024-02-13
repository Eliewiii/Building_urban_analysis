"""

"""
import os
import json
import random

from math import log, ceil

temp_ref = 25  # temperature reference for the efficiency of the panel


class BipvTechnology:
    """

    Example of a json file containing the data of the pv technologies
      "  "mitrex_facades c-Si Solar Siding 350W - Dove Grey china": {
            "id": "mitrex_facades c-Si Solar Siding 350W - Dove Grey china",
            "type": "pv_technology",
            "pv_type": "facade",
            "manufacturing_country": "china",
            "manufacturer": "mitrex",
            "model": "c-Si Solar Siding 350W - Dove Grey",
            "max_power_output_per_panel": 350,
            "physical_parameters": {
              "panel_area": 2.03,
              "panel_weight": 22,
              "panel_volume": null
            },
            "failure_parameters": {
              "weibull_scale_parameter": 30,
              "weibull_shape_parameter": 2.49
            },
            "efficiency_parameters": {
              "initial_efficiency": 0.173,
              "first_year_degrading_rate": 0.02,
              "degrading_rate": 0.005,
              "infrastructure_performance_ratio": 0.8,
              "efficiency_function": "degrading_rate_efficiency_loss",
              "other_parameters": null
            },
            "lca_ghg_emission": {
              "manufacturing_in_kgCO2eq_per_panel": 904,
              "end_of_life_in_kgCO2eq_per_panel": 8.14
            },
            "lca_primary_energy_use": {
              "manufacturing_in_kWh_per_panel": 2840,
              "end_of_life_in_kWh_per_panel": 17
            },
            "economic_parameters": {
              "costs": {
                "total_investment_in_USD_per_panel": 1.4,
                "recycling_in_USD_per_panel": 1.06145,
                "values_in_other_units":{
                    "total_investment_in_USD_per_Wp": 1.4,
                    "annual_maintenance_in_USD_per_Wp": 0.05,
                    "recycling_in_USD_per_kg": 1.06145
                }
              },
              "revenues": {
                "substituted_construction_material_roof_in_USD_per_panel": 142,
                "substituted_construction_material_facade_in_USD_per_panel": 251,
                "material_recovery_in_USD_per_panel": 1.562,
                "values_in_other_units":{
                    "substituted_construction_material_roof_in_USD_per_m^2": 142,
                    "substituted_construction_material_facade_in_USD_per_m^2": 251,
                    "material_recovery_factor_in_USD_per_kg": 1.562
                }
              }
            },
            "annual_maintenance": {
                "primary_energy_use_in_kWh_per_panel": 0.1,
                "ghg_emission_in_kgCO2eq_per_panel": 0.1,
                "cost_in_USD_per_panel": 0.1
                },
            "inverter": {
              "estimated_ghg_emission_in_fraction_of_manufacturing": 0.1,
              "estimated_primary_energy_use_in_fraction_of_manufacturing": 0.1,
              "estimated_cost_in_fraction_investement_cost": 0.1
            },
            "gate_to_gate_transportation": {
              "included_in_ghg_emission": false,
              "included_in_primary_energy_use": false,
              "included_in_investements": true
            }
            "recycling_transportation": {
                "included_in_ghg_emission": false,
                "included_in_primary_energy_use": false,
                "included_in_investements": true
                }
          }
  """

    def __init__(self, identifier):
        # General information
        self.identifier = identifier
        self.pv_type = None  # Roof or facade
        # Peak power generation (nominal power)
        self.max_power_output = None  # Nominal power of the panel in Watt
        # Physical properties
        self.panel_area = None  # In square meter
        self.weight = None  # In kg per module meter
        self.volume = None  # In cubic meter per module (including packaging,for transportation only)
        # Failure
        self.weibull_law_failure_parameters = {"lifetime": None, "shape": None}
        # Efficiency
        self.efficiency_function = None
        self.initial_efficiency = None
        self.first_year_degrading_rate = None
        self.degrading_rate = None
        self.infrastructure_performance_ratio = None
        # LCA primary energy
        self.primary_energy_manufacturing = None  # In kWh per panel
        self.primary_energy_recycling = None  # In kWh per panel
        # LCA greenhouse gas emission
        self.ghg_manufacturing = None  # In kgCO2eq per panel
        self.ghg_recycling = None  # In kgCO2eq per panel
        # Economical parameters
        self.cost_investment = None  # In USD per panel
        self.cost_recycling = None  # In USD per kg
        self.revenue_substituted_construction_material_roof = None  # In USD per panel
        self.revenue_substituted_construction_material_facade = None  # In USD per panel
        self.revenue_material_recovery = None  # In USD per panel
        # Annual maintenance
        self.primary_energy_annual_maintenance = None  # In kWh per panel per year
        self.ghg_annual_maintenance = None  # In kgCO2eq per panel per year
        self.cost_annual_maintenance = None  # In USD per panel per year
        # Inverter estimation parameters for the whole life time
        self.estimated_ghg_inverter = None  # In kgCO2eq per panel
        self.estimated_primary_energy_inverter = None  # In kWh per panel
        self.estimated_cost_inverter = None  # In USD per panel
        # Transport, gate to gate and recycling, if included in manufacturing or recycling
        self.gtg_transportation = {"ghg_included": None, "primary_energy_included": None, "cost_included": None}
        self.recycling_transportation = {"ghg_included": None, "primary_energy_included": None, "cost_included": None}

    @classmethod
    def load_pv_technologies_from_json_to_dictionary(cls, bipv_technology_obj_dict, path_json_folder):
        """
        Create the PanelTechnology objects from json file and save them in a dictionary.
        :param bipv_technology_obj_dict: dictionary of the technologies
        :param path_json_folder: path to the folder containing the json file
        :return pv_technologies_dict: dictionary of the technologies
        """
        for json_file in os.listdir(path_json_folder):  # for every json file in the folder
            if json_file.endswith(".json"):
                path_json_file = os.path.join(path_json_folder, json_file)  # get the path to the json file
                with open(path_json_file) as f:  # open and load the json file
                    data = json.load(f)
                    for key, value in data.items():  # for every technology in the json, we create and load the
                        if value.type != "pv_technology":
                            continue  # skip to the next element
                        # Load general information and Initialize the object
                        identifier = value["id"]
                        pv_tech_obj = cls(identifier)
                        pv_tech_obj.pv_type = value["pv_type"]
                        # Load peak power generation
                        pv_tech_obj.max_power_output = value["max_power_output_per_panel"]
                        # Load physical parameters
                        pv_tech_obj.panel_area = value["physical_parameters"]["panel_area"]
                        pv_tech_obj.weight = value["physical_parameters"]["panel_weight"]
                        pv_tech_obj.volume = value["physical_parameters"]["panel_volume"]
                        # Load failure parameters
                        pv_tech_obj.weibull_law_failure_parameters["lifetime"] = value["failure_parameters"][
                            "weibull_scale_parameter"]
                        pv_tech_obj.weibull_law_failure_parameters["shape"] = value["failure_parameters"][
                            "weibull_shape_parameter"]
                        # Load efficiency parameters
                        pv_tech_obj.initial_efficiency = value["efficiency_parameters"]["initial_efficiency"]
                        pv_tech_obj.first_year_degrading_rate = value["efficiency_parameters"][
                            "first_year_degrading_rate"]
                        pv_tech_obj.degrading_rate = value["efficiency_parameters"]["degrading_rate"]
                        pv_tech_obj.infrastructure_performance_ratio = value["efficiency_parameters"][
                            "infrastructure_performance_ratio"]
                        efficiency_function_name = value["efficiency_parameters"]["efficiency_function"]
                        pv_tech_obj.efficiency_function = getattr(pv_tech_obj, efficiency_function_name)
                        # Load LCA primary energy parameters
                        pv_tech_obj.primary_energy_manufacturing = value["lca_primary_energy_use"][
                            "manufacturing_in_kWh_per_panel"]
                        pv_tech_obj.primary_energy_recycling = value["lca_primary_energy_use"][
                            "end_of_life_in_kWh_per_panel"]
                        # Load LCA greenhouse gas emission parameters
                        pv_tech_obj.ghg_manufacturing = value["lca_ghg_emission"]["manufacturing_in_kgCO2eq_per_panel"]
                        pv_tech_obj.ghg_recycling = value["lca_ghg_emission"]["end_of_life_in_kgCO2eq_per_panel"]
                        # Load economical parameters
                        pv_tech_obj.cost_investment = value["economic_parameters"]["costs"][
                            "total_investment_in_USD_per_panel"]
                        pv_tech_obj.cost_recycling = value["economic_parameters"]["costs"]["recycling_in_USD_per_panel"]
                        pv_tech_obj.revenue_substituted_construction_material_roof = \
                            value["economic_parameters"]["revenues"][
                                "substituted_construction_material_roof_in_USD_per_panel"]
                        pv_tech_obj.revenue_substituted_construction_material_facade = \
                            value["economic_parameters"]["revenues"][
                                "substituted_construction_material_facade_in_USD_per_panel"]
                        pv_tech_obj.revenue_material_recovery_factor = value["economic_parameters"]["revenues"][
                            "material_recovery_in_USD_per_panel"]
                        # Annual maintenance
                        pv_tech_obj.primary_energy_annual_maintenance = value["Annual maintenance"][
                            "primary_energy_use_in_kWh_per_panel"]
                        pv_tech_obj.ghg_annual_maintenance = value["annual_maintenance"][
                            "ghg_emission_in_kgCO2eq_per_panel"]
                        pv_tech_obj.cost_annual_maintenance = value["annual_maintenance"]["cost_in_USD_per_panel"]
                        # Load inverter estimation parameters
                        pv_tech_obj.estimated_ghg_inverter = value["inverter"][
                                                                 "estimated_ghg_emission_in_fraction_of_manufacturing"] * pv_tech_obj.ghg_manufacturing
                        pv_tech_obj.estimated_primary_energy_inverter = value["inverter"][
                                                                            "estimated_primary_energy_use_in_fraction_of_manufacturing"] * pv_tech_obj.primary_energy_manufacturing
                        pv_tech_obj.estimated_cost_inverter = value["inverter"][
                                                                  "estimated_cost_in_fraction_investement_cost"] * pv_tech_obj.cost_investment
                        # Load transport parameters
                        pv_tech_obj.gtg_transportation["ghg_included"] = value["gate_to_gate_transportation"][
                            "included_in_ghg_emission"]
                        pv_tech_obj.gtg_transportation["primary_energy_included"] = \
                            value["gate_to_gate_transportation"]["included_in_primary_energy_use"]
                        pv_tech_obj.gtg_transportation["cost_included"] = value["gate_to_gate_transportation"][
                            "included_in_investements"]
                        pv_tech_obj.recycling_transportation["ghg_included"] = value["recycling_transportation"][
                            "included_in_ghg_emission"]
                        pv_tech_obj.recycling_transportation["primary_energy_included"] = \
                            value["recycling_transportation"]["included_in_primary_energy_use"]
                        pv_tech_obj.recycling_transportation["cost_included"] = value["recycling_transportation"][
                            "included_in_investements"]
                        # Save the object in the dictionary if it does not exist
                        if pv_tech_obj.identifier not in bipv_technology_obj_dict:
                            bipv_technology_obj_dict[identifier] = pv_tech_obj
                        else:
                            raise ValueError(f"The pv technology object{identifier} already exists, it must have "
                                             f"been duplicated in the json file")

        return bipv_technology_obj_dict

    def compute_transportation_lca_and_cost(self, bipv_transportation_obj):
        """
        Compute the transportation ghg, primary energy and cost of a panel according the source and destination if not
        included in the manufacturing or recycling process.
        :param bipv_transportation_obj: BipvTransportation object
        :return gtg_transportation_dict: dictionary of the gate to gate transportation
        :return recycling_recycling_dict: dictionary of the recycling transportation
        """
        gtg_transportation_dict = {"ghg": 0, "primary_energy": 0, "cost": 0}
        recycling_recycling_dict = {"ghg": 0, "primary_energy": 0, "cost": 0}
        if not self.gtg_transportation["ghg_included"]:
            gtg_transportation_dict["ghg"] = bipv_transportation_obj.gate_to_gate["ghg_emission"]
        if not self.gtg_transportation["primary_energy_included"]:
            gtg_transportation_dict["primary_energy"] = bipv_transportation_obj.gate_to_gate["pe_consumption"]
        if not self.gtg_transportation["cost_included"]:
            gtg_transportation_dict["cost"] = bipv_transportation_obj.gate_to_gate["cost"]
        if not self.recycling_transportation["ghg_included"]:
            recycling_recycling_dict["ghg"] = bipv_transportation_obj.recycling["ghg_emission"]
        if not self.recycling_transportation["primary_energy_included"]:
            recycling_recycling_dict["primary_energy"] = bipv_transportation_obj.recycling["pe_consumption"]
        if not self.recycling_transportation["cost_included"]:
            recycling_recycling_dict["cost"] = bipv_transportation_obj.recycling["cost"]

        return gtg_transportation_dict, recycling_recycling_dict

    def get_life_expectancy_of_a_panel(self):
        """
        Get the probabilistic time failure of a panel using the inverse of the quantile (inverse of the cumulative
        distribution0) function for the Weibull distribution
        return life_expectancy: life expectancy of a panel according to the probabilistic law of Weibull
        """

        y = random.random()  # we randomly choose a value between 0 and 1
        shape = self.weibull_law_failure_parameters["shape"]  # extract the failure parameters
        lifetime = self.weibull_law_failure_parameters["lifetime"]
        # Quantile function for the Weibull distribution
        life_expectancy = ceil(lifetime * (-log(1 - y)) ** (1 / shape))
        return life_expectancy

    def get_hourly_power_generation_over_a_year_by_panel(self, hourly_irradiance_list, age, **kwargs):
        """
        Get the energy harvested by a panel in Watt
        :param hourly_irradiance_list: list of hourly irradiance on the panel during a year
        :param age: age of the panel
        :param kwargs: kwargs


        :return: energy_harvested: energy harvested by the panel
        """

        # Check if the efficiency function is defined in the kwargs
        if "efficiency_function" in kwargs and kwargs["efficiency_function"] in [
            getattr(self, method_name) for method_name in dir(self) if callable(getattr(self, method_name))]:
            """ The efficiency function can be defined in the kwargs. If it is not defined, the default efficiency function
                    is used. If it is defined, the efficiency function is used. The efficiency function must be a method of the
                    class."""
            efficiency_function = getattr(self, kwargs["efficiency_function"])
            efficiency = efficiency_function(age=age, hourly_irradiance_list=hourly_irradiance_list, **kwargs)
        else:
            efficiency = self.efficiency_function(age=age, hourly_irradiance_list=hourly_irradiance_list, **kwargs)

        # Compute the irradiance that would generate the maximum output power of the panel
        max_irradiance = self.max_power_output / self.panel_area / efficiency
        # Initialize energy harvested
        hourly_power_generation_list = 0
        for hourly_irradiance in hourly_irradiance_list:
            # cap the irradiance to the maximum output power of the panel if necessary (in case of over irradiance)
            if hourly_irradiance / self.panel_area > max_irradiance:
                hourly_irradiance = max_irradiance
            hourly_power_generation_list += hourly_irradiance * efficiency * self.panel_area * self.infrastructure_performance_ratio

        return hourly_power_generation_list

    def constant_efficiency(self, **kwargs):
        """ Constant efficiency through the life of the panel """
        return self.initial_efficiency

    def degrading_rate_efficiency_loss(self, age, **kwargs):
        """ loose 2% efficiency the first year and then 0.5% every year"""
        if age == 0:
            return self.initial_efficiency
        else:
            return self.initial_efficiency * (
                    1 - self.first_year_degrading_rate - self.degrading_rate * (age - 1))

    def irradiance_dependent_efficiency(self, irradiance, **kwargs):
        """ todo: this one is just an example, to be changed"""
        return self.initial_efficiency * irradiance * self.param_1_irradiance + self.param_2_irradiance * irradiance ** 2

    def irradiance_temperature_and_age_dependent_efficiency(self, irradiance, age,
                                                            outdoor_temperature=temp_ref, **kwargs):
        """ todo: this one is just an example, to be changed"""
        return self.initial_efficiency * irradiance * self.param_1_irradiance + self.param_2_irradiance * irradiance ** 2

    # todo to delete
    # def get_efficiency_loss_function_from_string(self,fucntion_name):
    #     """todo"""
    #     if fucntion_name == "degrading_rate_efficiency_loss":
    #         return self.degrading_rate_efficiency_loss
