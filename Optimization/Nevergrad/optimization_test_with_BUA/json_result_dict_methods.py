"""
This file contains the methods to initialize and update  the json file that will contain the results of the optimization
"""

import json




def init_json_results_dict(path_json_file: str):
    """
    Initialize the json file with the result from each iteration
    """
    with open(path_json_file, 'w') as json_file:
        json_dict = {"itaration_nb": 0, "iteration_results": []}
        json.dump({}, json_file)

def update_json_results_dict(path_json_file: str, fitness_value: float,kpi_dict: dict):
    """
    Update the json file with the result from each iteration
    """
    # Load the json file
    with open(path_json_file, 'r') as json_file:
        json_dict = json.load(json_file)
    # Update the json file
    json_dict["itaration_nb"] += 1
    json_dict["iteration_results"].append({"fitness_value": fitness_value, "kpi_dict": kpi_dict})
    # Save the updated json file
    with open(path_json_file, 'w') as json_file:
        json.dump(json_dict, json_file)

