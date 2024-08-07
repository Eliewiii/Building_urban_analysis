"""
Script to define the fitness functions to be used in the optimization process.
"""
from current_development.Optimization.Nevergrad.optimization_test_with_BUA.kpi_reference_values import *


def environmental_oriented_fitness_func(kpi_dict: dict):
    """
    Fitness function to maximize for environmental oriented optimization.
    The fitness function is a weighted sum of the EROI and GHG emissions intensity.
    The weights are defined in the function.
    :param kpi_dict: dict, dictionary containing the KPIs values.
    :return: float, fitness value to maximize.
    """
    # Extract the KPIs from the dict
    eroi = kpi_dict["eroi"]["total"]
    ghg_intensity = kpi_dict["ghg emissions intensity [kgCo2eq/kWh]"]["total"]

    # weights of each of the KPIs in the fitness function
    weight_eroi = 1.
    weight_ghg_intensity = - 1.

    # fitness value to maximize
    fitness_value = weight_eroi * eroi / EROI_REF_ENV - weight_ghg_intensity * ghg_intensity / GHGI_REF_ENV

    return - fitness_value


def eroi_only_fitness_func(kpi_dict: dict):
    """
    Fitness function to maximize for environmental oriented optimization.
    The fitness function is a weighted sum of the EROI and GHG emissions intensity.
    The weights are defined in the function.
    :param kpi_dict: dict, dictionary containing the KPIs values.
    :return: float, fitness value to maximize.
    """
    # Extract the KPIs from the dict
    eroi = kpi_dict["eroi"]["total"]

    # weights of each of the KPIs in the fitness function
    weight_eroi = 1.

    # fitness value to maximize
    fitness_value = weight_eroi * eroi / EROI_REF_ENV

    return - fitness_value