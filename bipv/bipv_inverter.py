"""

"""
import os
import json
import random

from math import log, ceil


class BipvInverter:
    """

    Example of a json file containing the data of the pv technologies
        "Inverters ref 1": {
            "id": "ref 1",
            "type": "inverter",
            "replacement_frequency_in_year": 10,
            "capacity_in_kW_vs_cost_in_USD": {
              "5": 1000,
              "10": 2000,
              "20": 3000,
              "30": 4000,
              "40": 5000
            },
            "environmental_impact": {
              "function": "linear",
              "coefficient_ghg_emission_in_kgCO2eq_per_kWp": 63.1,
              "offset_ghg_emission_in_kgCO2eq": 232
            },
            "primary_energy":{
              "function": "linear",
              "coefficient_primary_energy_in_kWh_per_kWp": 636,
              "offset_primary_energy_in_kWh": 0
            }
        }
  """

    def __init__(self, identifier):
        self.identifier = identifier
        # Characteristics
        self.replacement_frequency = None  # in years
        self.capacity_vs_cost = {}  # capacity in kWp and cost in USD
        # ghg emission
        self.ghg_function = None  # linear for now
        self.ghg_coefficient = None  # in kgCO2eq per kWp
        self.ghg_offset = None  # in kgCO2eq
        # primary energy
        self.primary_energy_function = None  # linear for now
        self.primary_energy_coefficient = None  # in kWh per kWp
        self.primary_energy_offset = None  # in kWh

    @classmethod
    def load_bipv_inverter_obj_from_json_to_dictionary(cls, inverter_obj_dict, path_json_folder):
        """
        Create the BipvInverter objects from json file and save them in a dictionary.
        :param inverter_obj_dict: dictionary of the inverters
        :param path_json_folder: path to the folder containing the json file
        :return inverter_dict: dictionary of the inverters
        """
        for file in os.listdir(path_json_folder):
            if file.endswith(".json"):
                with open(os.path.join(path_json_folder, file), "r") as f:
                    data = json.load(f)
                    for key, value in data.items():
                        if value["type"] != "inverter":
                            continue  # skip to the next element
                        inverter_obj = cls(value["id"])
                        inverter_obj.replacement_frequency = int(value["replacement_frequency_in_year"])
                        for k, v in value["capacity_in_kW_vs_cost_in_USD"].items():
                            inverter_obj.capacity_vs_cost[int(k)] = float(v)
                        if value["environmental_impact"]["function"] == "linear":
                            inverter_obj.ghg_function = inverter_obj.linear_ghg_emission
                            inverter_obj.ghg_function = value["environmental_impact"]["function"]
                            inverter_obj.ghg_coefficient = value["environmental_impact"][
                                "coefficient_ghg_emission_in_kgCO2eq_per_kWp"]
                            inverter_obj.ghg_offset = value["environmental_impact"][
                                "offset_ghg_emission_in_kgCO2eq"]
                        else:
                            raise ValueError("The environmental impact function is not implemented")
                        if value["primary_energy"]["function"] == "linear":
                            inverter_obj.primary_energy_function = inverter_obj.linear_primary_energy
                            inverter_obj.primary_energy_coefficient = value["primary_energy"][
                                "coefficient_primary_energy_in_kWh_per_kWp"]
                            inverter_obj.primary_energy_offset = value["primary_energy"][
                                "offset_primary_energy_in_kWh"]
                        else:
                            raise ValueError("The primary energy function is not implemented")

                        # Add the inverter object to the dictionary if it does not exist already
                        if inverter_obj.identifier not in inverter_obj_dict:
                            inverter_obj_dict[inverter_obj.identifier] = inverter_obj
                        else:
                            raise ValueError(f"The inverter object{inverter_obj.identifier} already exists, "
                                             f"it must have been duplicated in the json file")
        return inverter_obj_dict

    def linear_ghg_emission(self, capacity):
        """
        Calculate the ghg emission using a linear function
        :param capacity: capacity in kWp
        :return ghg: ghg emission in kgCO2eq
        """
        ghg = self.ghg_coefficient * capacity + self.ghg_offset
        return ghg

    def linear_primary_energy(self, capacity):
        """
        Calculate the primary energy using a linear function
        :param capacity: capacity in kWp
        :return ghg: ghg emission in kgCO2eq
        """
        primary_energy = self.primary_energy_coefficient * capacity + self.primary_energy_offset
        return primary_energy

    def get_primary_energy_ghg_and_cost_for_capacity_list(self, capacity_list):
        """
        Return the primary energy, ghg emission and cost for a list of capacities
        :param capacity_list: list of float: list of capacities in kWp
        :return primary_energy: float: primary energy of all the inverters in kWh
        :return ghg_emission: float: ghg emission of all the inverters in kgCO2eq
        :return cost: float: cost of all the inverters in USD
        """
        primary_energy_list = sum([self.primary_energy_function(capacity) for capacity in capacity_list])
        ghg_emission_list = sum([self.ghg_function(capacity) for capacity in capacity_list])
        cost_list = [self.capacity_vs_cost[capacity] for capacity in capacity_list]
        return primary_energy_list, ghg_emission_list, cost_list



    def size_inverter(self, peak_power, sizing_ratio):
        """
        Calculate the size of the inverter according to the peak power of the panels and a sizing ratio
        :param peak_power: float: peak power of the panels in kWp
        :param sizing_ratio: float: ratio to size the inverter
        :return total_capacity: float: size of the inverter in kWp
        :return sub_capacities_list: list of float: list of the individual sizes of the inverters used if necessary in kWp
        """
        # Ideal size of the inverter according to the peak power of the panels and a sizing ratio
        ideal_capacity = peak_power * sizing_ratio
        available_capacities = sorted([float(capacity) for capacity in self.capacity_vs_cost.keys()])
        # if the ideal capacity is smaller than the smallest available capacity
        if ideal_capacity <= available_capacities[-1]:
            for capacity in available_capacities:
                if capacity >= ideal_capacity:
                    total_capacity = capacity
                    sub_capacities_list = [capacity]
                    break
        # if the ideal capacity is larger than the largest available capacities
        else:
            multiplier = ceil(ideal_capacity / available_capacities[-1])
            for capacity in available_capacities:
                if capacity * multiplier >= ideal_capacity:
                    total_capacity = capacity * multiplier
                    sub_capacities_list = [capacity] * int(multiplier)  # the int is not mandatory, just in case
                    break

        return total_capacity, sub_capacities_list
