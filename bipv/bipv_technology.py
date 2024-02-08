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
            "type": "pv_techology",
            "pv_type": "facade",
            "manufacturing_country": "china",
            "manufacturer": "mitrex",
            "model": "c-Si Solar Siding 350W - Dove Grey",
            "peak_power_generation_per_panel": 350,
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
              "panel_performance_ratio": 0.8,
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
                "total_investment_in_USD_per_Wp": 1.4,
                "annual_maintenance_in_USD_per_Wp": 0.05,
                "recycling_in_USD_per_kg": 1.06145
              },
              "revenues": {
                "substituted_construction_material_roof_in_USD_per_m^2": 142,
                "substituted_construction_material_facade_in_USD_per_m^2": 251,
                "material_recovery_factor_in_USD_per_kg": 1.562
              }
            },
            "inverter": {
              "estimated_ghg_emission_in_fraction_of_manufacturing": 0.1,
              "estimated_primary_energy_use_in_fraction_of_manufacturing": 0.1,
              "estimated_cost_in_fraction_investement_cost": 0.1
            },
            "transport": {
              "transport_included_in_ghg_emission": false,
              "transport_included_in_primary_energy_use": false,
              "transport_included_in_investements": true
            }
          }
  """

    def __init__(self, identifier):
        # General information
        self.identifier = identifier
        self.pv_type = None  # Roof or facade
        # Peak power generation (nominal power)
        self.peak_power = None  # Nominal power of the panel in Watt
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
        self.panel_performance_ratio = None
        # LCA primary energy
        self.primary_energy_manufacturing = None  # In kWh per square meter
        self.primary_energy_recycling = None  # In kWh per square meter
        # LCA greenhouse gas emission
        self.ghg_manufacturing = None  # In kgCO2eq per square meter
        self.ghg_recycling = None  # In kgCO2eq per square meter
        # Economical parameters
        self.cost_investment = None  # In USD per Wp
        self.cost_annual_maintenance = None  # In USD per Wp per year
        self.cost_recycling = None  # In USD per kg
        self.revenue_substituted_construction_material_roof = None  # In USD per square meter
        self.revenue_substituted_construction_material_facade = None  # In USD per square meter
        self.revenue_material_recovery_factor = None  # In USD per kg
        # Inverter estimation parameters
        self.estimated_ghg_inverter = None  # In fraction of the manufacturing
        self.estimated_primary_energy_inverter = None  # In fraction of the manufacturing
        self.estimated_cost_inverter = None  # In fraction of the investment cost
        # Transport
        self.transport_included_in_ghg_emission = None
        self.transport_included_in_primary_energy_use = None
        self.transport_included_in_investments = None

    @classmethod
    def load_pv_technologies_from_json_to_dictionary(cls, path_json_folder):
        """
        Create the PanelTechnology objects from json file and save them in a dictionary
        :param path_json_folder: path to the folder containing the json file
        :return pv_technologies_dict: dictionary of the technologies
        """
        pv_technologies_dict = {}  # initialize the dictionary
        for json_file in os.listdir(path_json_folder):  # for every json file in the folder
            if json_file.endswith(".json"):
                path_json_file = os.path.join(path_json_folder, json_file)  # get the path to the json file
                with open(path_json_file) as f:  # open and load the json file
                    pv_dict_data = json.load(f)
                    for identifier_key in pv_dict_data:  # for every technology in the json, we create and load the
                        # Load general information and Initialize the object
                        identifier = pv_dict_data[identifier_key]["id"]
                        pv_tech_obj = cls(identifier)
                        pv_tech_obj.pv_type = pv_dict_data[identifier_key]["pv_type"]
                        # Load peak power generation
                        pv_tech_obj.peak_power = pv_dict_data[identifier_key]["peak_power_generation_per_panel"]
                        # Load physical parameters
                        pv_tech_obj.panel_area = pv_dict_data[identifier_key]["physical_parameters"][
                            "panel_area"]
                        pv_tech_obj.weight = pv_dict_data[identifier_key]["physical_parameters"][
                            "panel_weight"]
                        pv_tech_obj.volume = pv_dict_data[identifier_key]["physical_parameters"][
                            "panel_volume"]
                        # Load failure parameters
                        pv_tech_obj.weibull_law_failure_parameters["lifetime"] = pv_dict_data[identifier_key][
                            "failure_parameters"]["weibull_scale_parameter"]
                        pv_tech_obj.weibull_law_failure_parameters["shape"] = pv_dict_data[identifier_key][
                            "failure_parameters"]["weibull_shape_parameter"]
                        # Load efficiency parameters
                        pv_tech_obj.initial_efficiency = \
                            pv_dict_data[identifier_key]["efficiency_parameters"][
                                "initial_efficiency"]
                        pv_tech_obj.first_year_degrading_rate = \
                            pv_dict_data[identifier_key]["efficiency_parameters"][
                                "first_year_degrading_rate"]
                        pv_tech_obj.degrading_rate = pv_dict_data[identifier_key]["efficiency_parameters"][
                            "degrading_rate"]
                        pv_tech_obj.panel_performance_ratio = \
                            pv_dict_data[identifier_key]["efficiency_parameters"][
                                "panel_performance_ratio"]
                        efficiency_function_name = pv_dict_data[identifier_key]["efficiency_parameters"][
                            "efficiency_function"]
                        pv_tech_obj.efficiency_function = getattr(pv_tech_obj, efficiency_function_name)
                        # Load LCA primary energy parameters
                        pv_tech_obj.primary_energy_manufacturing = \
                            pv_dict_data[identifier_key]["lca_primary_energy_use"][
                                "manufacturing_in_kWh_per_panel"]
                        pv_tech_obj.primary_energy_recycling = \
                            pv_dict_data[identifier_key]["lca_primary_energy_use"][
                                "end_of_life_in_kWh_per_panel"]
                        # Load LCA greenhouse gas emission parameters
                        pv_tech_obj.ghg_manufacturing = pv_dict_data[identifier_key]["lca_ghg_emission"][
                            "manufacturing_in_kgCO2eq_per_panel"]
                        pv_tech_obj.ghg_recycling = pv_dict_data[identifier_key]["lca_ghg_emission"][
                            "end_of_life_in_kgCO2eq_per_panel"]
                        # Load economical parameters
                        pv_tech_obj.cost_investment = pv_dict_data[identifier_key]["economic_parameters"]["costs"][
                            "total_investment_in_USD_per_Wp"]
                        pv_tech_obj.cost_annual_maintenance = \
                            pv_dict_data[identifier_key]["economic_parameters"]["costs"][
                                "annual_maintenance_in_USD_per_Wp"]
                        pv_tech_obj.cost_recycling = pv_dict_data[identifier_key]["economic_parameters"]["costs"][
                            "recycling_in_USD_per_kg"]
                        pv_tech_obj.revenue_substituted_construction_material_roof = \
                            pv_dict_data[identifier_key]["economic_parameters"]["revenues"][
                                "substituted_construction_material_roof_in_USD_per_m^2"]
                        pv_tech_obj.revenue_substituted_construction_material_facade = \
                            pv_dict_data[identifier_key]["economic_parameters"]["revenues"][
                                "substituted_construction_material_facade_in_USD_per_m^2"]
                        pv_tech_obj.revenue_material_recovery_factor = \
                            pv_dict_data[identifier_key]["economic_parameters"]["revenues"][
                                "material_recovery_factor_in_USD_per_kg"]
                        # Load inverter estimation parameters
                        pv_tech_obj.estimated_ghg_inverter = pv_dict_data[identifier_key]["inverter"][
                            "estimated_ghg_emission_in_fraction_of_manufacturing"]
                        pv_tech_obj.estimated_primary_energy_inverter = pv_dict_data[identifier_key]["inverter"][
                            "estimated_primary_energy_use_in_fraction_of_manufacturing"]
                        pv_tech_obj.estimated_cost_inverter = pv_dict_data[identifier_key]["inverter"][
                            "estimated_cost_in_fraction_investement_cost"]
                        # Load transport parameters
                        pv_tech_obj.transport_included_in_ghg_emission = pv_dict_data[identifier_key]["transport"][
                            "transport_included_in_ghg_emission"]
                        pv_tech_obj.transport_included_in_primary_energy_use = \
                            pv_dict_data[identifier_key]["transport"][
                                "transport_included_in_primary_energy_use"]
                        pv_tech_obj.transport_included_in_investments = pv_dict_data[identifier_key]["transport"][
                            "transport_included_in_investements"]
                        # Save the object in the dictionary if it does not exist
                        if identifier_key not in pv_technologies_dict:
                            pv_technologies_dict[identifier_key] = pv_tech_obj
                        else:
                            raise ValueError(f"The pv technology object{identifier_key} already exists, it must have "
                                             f"been duplicated in the json file")

        return pv_technologies_dict

    def compute_transportation_lca_and_cost(self):
        """
        Compute the energy needed for the transportation of the panels

        """
        # todo

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

    def get_energy_harvested_by_panel(self, irradiance, age, **kwargs):
        """
        Get the energy harvested by a panel in Watt
        :param irradiance: irradiance on the panel
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
            efficiency_function = kwargs["efficiency_function"]
            efficiency = efficiency_function(age=age, irradiance=irradiance, **kwargs)
        else:
            efficiency = self.efficiency_function(age=age, irradiance=irradiance, **kwargs)

        energy_harvested = efficiency * irradiance * self.panel_performance_ratio * self.panel_area

        return energy_harvested

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
