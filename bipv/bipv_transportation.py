"""

"""
import os
import json
import random

from math import log, ceil


class BipvTransportation:
    """

    Example of a json file containing the data of the transport
      "Transport China - Israel": {
        "id": "China -Israel",
        "type": "transportation",
        "source": "China",
        "destination": "Israel",
        "from_factory_to_construction_site": {
          "ghg_emission_in_kgCo2_per_panel": 0.0001,
          "pe_consumption_in_kWh_per_panel": 0.0001,
          "cost_in_USD_per_panel": 0.0,
          "values_in_other_units":{
              "ghg_emission_in_kgCo2_per_kg": 0.0001,
              "pe_consumption_in_kWh_per_kg": 0.0001,
              "cost_in_USD_per_kg": 0.0,
              "cost_in_USD_per_m3": 0.0
          }
        },
        "from_construction_site_to_recycling_factory": {
          "shipping_parameters": {
            "type": "truck",
            "transportation_distance_in_km": 100,
            "volume_shipping_unit_in_m^3": 55,
            "transportation_to_recycling_in_USD_per_shipping_unit": 440
          },
          "ghg_emission_in_kgCo2_per_panel": 0.0001,
          "pe_consumption_in_kWh_per_panel": 0.0001,
          "cost_in_USD_per_panel": 0.0,
          "values_in_other_units":{
              "ghg_emission_in_kgCo2_per_kg": 0.0001,
              "pe_consumption_in_kWh_per_kg": 0.0001,
              "cost_in_USD_per_kg": 0.0,
              "cost_in_USD_per_m3": 0.0
          }
        }

    }
  """

    def __init__(self, identifier):
        self.identifier = identifier
        #
        self.source = None
        self.destination = None
        # Impacts, ghg emission in kgCO2eq, primary energy in kWh, cost in USD, all values are per panel
        self.gate_to_gate = {"ghg_emission": None, "pe_consumption": None, "cost": None}
        self.recycling = {"ghg_emission": None, "pe_consumption": None, "cost": None}

    @classmethod
    def load_transportation_obj_from_json_to_dictionary(cls, transportation_obj_dict,path_json_folder):
        """
        Create the BipvTransportation objects from json file and save them in a dictionary.
        :param transportation_obj_dict: dictionary of the transportation objects
        :param path_json_folder: path to the folder containing the json file
        :return inverter_dict: dictionary of the inverters
        """
        for file in os.listdir(path_json_folder):
            if file.endswith(".json"):
                with open(os.path.join(path_json_folder, file), "r") as f:
                    data = json.load(f)
                    for key, value in data.items():
                        if value.type != "transportation":
                            continue  # skip to the next element
                        transportation_obj = cls(value["id"])
                        transportation_obj.source = value["source"]
                        transportation_obj.destination = value["destination"]
                        # Gate to gate environmental impacts and cost of transport
                        transportation_obj.gate_to_gate["ghg_emission"] = \
                            value["from_factory_to_construction_site"]["ghg_emission_in_kgCo2_per_panel"]
                        transportation_obj.gate_to_gate["pe_consumption"] = \
                            value["from_factory_to_construction_site"]["pe_consumption_in_kWh_per_panel"]
                        transportation_obj.gate_to_gate["cost"] = \
                            value["from_factory_to_construction_site"]["cost_in_USD_per_panel"]
                        # Recycling environmental impacts and cost of transport
                        transportation_obj.recycling["ghg_emission"] = \
                            value["from_construction_site_to_recycling_factory"]["ghg_emission_in_kgCo2_per_panel"]
                        transportation_obj.recycling["pe_consumption"] = \
                            value["from_construction_site_to_recycling_factory"]["pe_consumption_in_kWh_per_panel"]
                        transportation_obj.recycling["cost"] = \
                            value["from_construction_site_to_recycling_factory"]["cost_in_USD_per_panel"]
                        if (transportation_obj.source, transportation_obj.destination) \
                                not in transportation_obj_dict:
                            transportation_obj_dict[(transportation_obj.source,
                                                 transportation_obj.destination)] = transportation_obj
                        else:
                            raise ValueError(
                                f"The transportation object{transportation_obj.identifier} already exists, "
                                f"it must have been duplicated in the json file")

        return transportation_obj_dict

