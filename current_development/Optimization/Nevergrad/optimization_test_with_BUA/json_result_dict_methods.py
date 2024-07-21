"""
This file contains the methods to initialize and update  the json file that will contain the results of the optimization
"""

import json


def init_json_results_dict(path_json_file: str):
    """
    Initialize the json file with the result from each iteration
    :param path_json_file: str, path to the json file to initialize
    """
    with open(path_json_file, 'w') as json_file:
        json_dict = {"iteration_nb": 0, "iteration_results": [], "recommendation": {}}
        json.dump(json_dict, json_file)


def update_json_results_dict(path_json_file: str, fitness_value: float, kpi_dict: dict,**kwargs):
    """
    Update the json file with the result from each iteration
    :param path_json_file: str, path to the json file to update
    :param fitness_value: float, fitness value of the iteration
    :param kpi_dict: dict, dictionary containing the KPIs values of the iteration
    """
    # Load the json file
    with open(path_json_file, 'r') as json_file:
        json_dict = json.load(json_file)
    # Update the json file
    parameter_dict = {}
    for key, value in kwargs.items():
        parameter_dict[key] = value
    json_dict["iteration_results"].append(
        {"iteration": json_dict["iteration_nb"],"parameters":parameter_dict, "fitness_value": fitness_value, "kpi_dict": kpi_dict})
    json_dict["iteration_nb"] += 1
    # Save the updated json file
    with open(path_json_file, 'w') as json_file:
        json.dump(json_dict, json_file)


def finalize_json_results_dict(path_json_file: str, recommendation):
    """
    Update the json file with the final recommendation
    :param path_json_file: str, path to the json file to update
    :param recommendation: nevergrad recommendation object, recommendation of the optimization
    """
    # Load the json file
    with open(path_json_file, 'r') as json_file:
        json_dict = json.load(json_file)
    # Update the json file
    json_dict["recommendation"] = {}
    for variable in list(recommendation.kwargs):
        json_dict["recommendation"][variable] = recommendation.kwargs[variable]
    # Save the updated json file
    with open(path_json_file, 'w') as json_file:
        json.dump(json_dict, json_file)
