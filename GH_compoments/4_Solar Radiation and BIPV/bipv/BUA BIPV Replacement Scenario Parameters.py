"""Parameters for the BIPV replacement scenarios.
    Inputs:
        _replacement_scenario_id: Identifier of the bipv replacement scenario to use.
        _replacement_frequency_: Replacement frequency of the panels in years.
        _minimal_panel_age_: Minimum age of the panels to be replaced (to be implemented if relevant).
    Output:
        replacement_scenario_parameters_dict: Dictionary containing the parameters for the BIPV replacement scenarios"""

__author__ = "elie-medioni"
__version__ = "2023.09.06"

ghenv.Component.Name = "BUA BIPV Replacement Scenario Parameter"
ghenv.Component.NickName = 'BIPVReplacementScenarioParameter'
ghenv.Component.Message = '0.0.0'
ghenv.Component.Category = 'BUA'
ghenv.Component.SubCategory = '4 :: Solar Radiation and BIPV'
ghenv.Component.AdditionalHelpFromDocStrings = "1"

import json

# List of replacement without parameters
replacement_scenario_without_parameters_list = ["no_replacement"]
# List of the replacement scenarios that are implemented with replacement frequencies
replacement_scenario_implemented_with_replacement_frequencies_list = ["replace_failed_panels_every_X_years",
                                                                      "replace_all_panels_every_X_years",
                                                                      "uc_replace_failed_panels_every_X_years",
                                                                      "uc_replace_all_panels_every_X_years"]
# List of the replacement scenarios that are not implemented with replacement frequencies
replacement_scenario_not_implemented_with_replacement_frequencies_and_minimum_panel_age_list = [
    "replace_failed_panels_and_panels_above_X_years_every_Y_years",
    "uc_replace_failed_panels_and_panels_above_X_years_every_Y_years"]

# Initialize the replacement scenario parameter dictionary
replacement_scenario_parameters_dict = {
    "replacement_scenario_id": None,
    "replacement_frequency": None,
    "minimal_panel_age": None,
}

# Check if the parameters and combinations of parameters are valid
if _replacement_scenario_id is not None:
    if _replacement_scenario_id not in replacement_scenario_without_parameters_list + \
            replacement_scenario_implemented_with_replacement_frequencies_list + \
            replacement_scenario_not_implemented_with_replacement_frequencies_and_minimum_panel_age_list:
        raise ValueError(
            "The replacement scenario is not valid, use one of the values from the replacement scenarios list of values")
    elif _replacement_scenario_id in replacement_scenario_implemented_with_replacement_frequencies_list + replacement_scenario_not_implemented_with_replacement_frequencies_and_minimum_panel_age_list:
        if _replacement_frequency_ is None:
            raise ValueError("The replacement frequency is not defined")
        elif _replacement_frequency_ <= 0:
            raise ValueError("The replacement frequency cannot be negative")
        else:
            replacement_scenario_parameters_dict["replacement_scenario_id"] = _replacement_scenario_id
            replacement_scenario_parameters_dict["replacement_frequency"] = _replacement_frequency_
        if _replacement_scenario_id in replacement_scenario_not_implemented_with_replacement_frequencies_and_minimum_panel_age_list:
            if _minimal_panel_age_ is None:
                raise ValueError("The minimal panel age is not defined")
            elif _minimal_panel_age_ <= 0:
                raise ValueError("The minimal panel age cannot be negative")
            else:
                replacement_scenario_parameters_dict["minimal_panel_age"] = _minimal_panel_age_
    else: # if the replacement scenario is in the replacement_scenario_without_parameters_list
        replacement_scenario_parameters_dict["replacement_scenario_id"] = _replacement_scenario_id

replacement_scenario_parameters = json.dumps(replacement_scenario_parameters_dict)