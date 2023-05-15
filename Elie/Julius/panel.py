"""
Panel class, modeling solar panels, to track the age and energy production of panels on buildings
"""

# todo @Julius and Elie, make a small documentation to explain how we compute the time of failure
#  plus all the hypothesis

from math import log,ceil


class Panel:
    """ """
    def __init__(self, index):
        self.index = index
        self.failure_scenario_list = []

    def compute_failure_scenario(self, lambda_para, k, nb_of_year_building, number_of_scenario_to_compute):
        """
        Computes different failure scenarios for the panel and creates a list for each one
        """

        total_list = []
        for i in range(0, number_of_scenario_to_compute):
            panel_list = []
            while True:
                y = random.random()
                time_of_failure = math.ceil(lambda_para * (-(1 / k) * math.log(1 - y)) ** (1 / k))
                if sum(panel_list) + time_of_failure <= nb_of_year_building:
                    panel_list.append(time_of_failure)
                else:
                    time_of_failure = nb_of_year_building - sum(panel_list)
                    panel_list.append(time_of_failure)
                    break
            total_list.append(panel_list)

        @staticmethod
        def weibull_cumulative_distribution(lambda_para,k_para,probability):
            """

            """