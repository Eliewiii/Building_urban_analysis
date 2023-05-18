"""
Panel class, modeling solar panels, to track the age and energy production of panels on buildings
"""

# todo @Julius and Elie, make a small documentation to explain how we compute the time of failure
#  plus all the hypothesis

from math import log, ceil
import random

from solar_panel.pvmaterial import PanelTechnology


class Panel(PanelTechnology):
    """ """

    def __init__(self, index, identifier):
        super.__init__(identifier)
        self.index = index
        self.failure_scenario_list = None
        self.panel_technology_identifier = identifier

    def compute_failure_scenario(self, nb_of_year_building=100, number_of_scenario_to_compute=1):
        """
        Computes different failure scenarios for the panel and creates a list for each one
        nb_of_year_building : nb of years the building is supposed to last, at least (Default:100 years)
        number_of_scenarios_to_compute : number of time the
        """

        total_list = []
        for i in range(number_of_scenario_to_compute):
            panel_list = []
            while True:
                # probabilistic time of failure
                time_of_failure = self.get_time_failure_of_a_panel()
                if sum(panel_list) + time_of_failure <= nb_of_year_building:  # if the panel fails before the
                    # 'destruction' of the building
                    panel_list.append(time_of_failure)
                else:
                    time_of_failure = nb_of_year_building - sum(panel_list)  # else, we only add the last years of
                    # life of the building
                    panel_list.append(time_of_failure)
                    break
            total_list.append(panel_list)
        # add the scenario list of lists to the attributes
        self.failure_scenario_list = total_list
        return total_list
