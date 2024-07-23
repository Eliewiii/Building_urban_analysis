"""
This file contains the methods to initialize and update  the json file that will contain the results of the optimization
"""

import json

import matplotlib.pyplot as plt

from current_development.Optimization.Nevergrad.optimization_test_with_BUA.design_variable_definition_and_boundaries import \
ROOF_PANEL_TECHNOLOGIES_REVERT_DICT, FACADES_PANEL_TECHNOLOGIES_REVERT_DICT


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


def plot_fitness_value_through_it(path_json_file: str):
    """
    Plot the fitness value through the iterations
    :param path_json_file: str, path to the json file to plot
    """
    # Load the json file
    with open(path_json_file, 'r') as json_file:
        json_dict = json.load(json_file)
    # Plot the fitness value through the iterations
    fitness_values = [iteration["fitness_value"] for iteration in json_dict["iteration_results"]]
    plt.plot(fitness_values)
    plt.xlabel("Iteration")
    plt.ylabel("Fitness value")
    plt.title("Fitness value through the iterations")
    plt.show()

def plot_kpi_through_it(path_json_file: str, kpi_name: str):
    """
    Plot the KPI value through the iterations
    :param path_json_file: str, path to the json file to plot
    :param kpi_name: str, name of the KPI to plot
    """
    # Load the json file
    with open(path_json_file, 'r') as json_file:
        json_dict = json.load(json_file)
    # Plot the KPI value through the iterations
    kpi_values = [iteration["kpi_dict"][kpi_name]["total"] for iteration in json_dict["iteration_results"]]
    plt.plot(kpi_values)
    plt.xlabel("Iteration")
    plt.ylabel(kpi_name)
    plt.title(f"{kpi_name} through the iterations")
    plt.show()

def plot_parameter_through_it(path_json_file: str, parameter_name: str):
    """
    Plot the parameter value through the iterations
    :param path_json_file: str, path to the json file to plot
    :param parameter_name: str, name of the parameter to plot
    """
    # Load the json file
    with open(path_json_file, 'r') as json_file:
        json_dict = json.load(json_file)
    # Plot the parameter value through the iterations
    parameter_values = [iteration["parameters"][parameter_name] for iteration in json_dict["iteration_results"]]
    if parameter_name == "roof_panel_id":
        parameter_values = [ROOF_PANEL_TECHNOLOGIES_REVERT_DICT[parameter] for parameter in parameter_values]
    elif parameter_name == "facades_panel_id":
        parameter_values = [FACADES_PANEL_TECHNOLOGIES_REVERT_DICT[parameter] for parameter in parameter_values]

    plt.plot(parameter_values)
    plt.xlabel("Iteration")
    plt.ylabel(parameter_name)
    plt.title(f"{parameter_name} through the iterations")
    plt.show()