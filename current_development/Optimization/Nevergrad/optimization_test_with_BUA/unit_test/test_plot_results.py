"""
Test the plotting of the results
"""

import os

from current_development.Optimization.Nevergrad.optimization_test_with_BUA.json_result_dict_methods import \
    plot_fitness_value_through_it, plot_kpi_through_it, plot_parameter_through_it

path_test_json_results_file = os.path.join(r"..\Saved_results\results_test_Nicolo.json")

def test_plot_fitness_value_through_it():
    """
    Test the plotting of the results
    """
    plot_fitness_value_through_it(path_test_json_results_file)

def test_plot_kpi_through_it(kpi_name: str= "eroi"):
    """
    Test the plotting of the results
    """
    plot_kpi_through_it(path_test_json_results_file, kpi_name)

def test_plot_parameter_through_it():
    """
    Test the plotting of the results
    """
    parameter_name: str = "min_panel_eroi"
    plot_parameter_through_it(path_test_json_results_file, parameter_name)
    parameter_name: str = "roof_inverter_sizing_ratio"
    plot_parameter_through_it(path_test_json_results_file, parameter_name)
    parameter_name: str = "facades_inverter_sizing_ratio"
    plot_parameter_through_it(path_test_json_results_file, parameter_name)
    parameter_name: str = "replacement_frequency"
    plot_parameter_through_it(path_test_json_results_file, parameter_name)
    parameter_name: str = "roof_panel_id"
    plot_parameter_through_it(path_test_json_results_file, parameter_name)
    parameter_name: str = "facades_panel_id"
    plot_parameter_through_it(path_test_json_results_file, parameter_name)

