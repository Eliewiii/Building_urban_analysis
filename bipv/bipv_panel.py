"""
Panel class, modeling solar panels, to track the age and energy production of panels on buildings
"""

# todo @Julius and Elie, make a small documentation to explain how we compute the time of failure
#  plus all the hypothesis

from libraries_addons.solar_panels.pv_efficiency_functions import get_efficiency_loss_function_from_string


class BipvPanel:
    """ """

    def __init__(self, index, pv_technology_object):
        """
        initialize a panel
        index : identifies the panel
        age : number of years the pv has been working
        lifetime : number of years it will work since its installation (deduced by the probabilistic law of weibull)
        During the initialization, we suppose that age = None and lifetime = None ie. the panel has not begun to work yet
        panel_technology_object : a PanelTechnology object """

        self.index = index
        self.age = None
        self.life_expectancy = None
        self.panel_technology_object = pv_technology_object

    def is_panel_working(self):
        """ If the panel's life expectancy is different from None, it means it has been switched on and that it is
        working (True)
        Else, if its life expectancy is None, then the panel is not working (False)"""
        return self.life_expectancy is not None

    def initialize_or_replace_panel_old(self):
        """
        Initialize a panel or replace the panel with a new one, leading the LCA carbon footprint
        :return lca_cradle_to_installation_primary_energy: float: the energy manufacturing this new panel caused
        """
        # Get a life expectancy according to the life expectancy distribution of the pv technology
        self.life_expectancy = self.panel_technology_object.get_life_expectancy_of_a_panel()
        # put back the age to 0
        self.age = 0
        # get the LCA carbon footprint for one panel according to its pv technology
        lca_cradle_to_installation_primary_energy = self.panel_technology_object.primary_energy_manufacturing

        return lca_cradle_to_installation_primary_energy

    def initialize_or_replace_panel(self):
        """
        Initialize the panel
        """
        # Get a life expectancy according to the life expectancy distribution of the pv technology
        self.life_expectancy = self.panel_technology_object.get_life_expectancy_of_a_panel()
        # put back the age to 0
        self.age = 0

    def panel_failed(self):
        """
        Switch off the panel by initializing its age and its life expectancy to None and return the waste caused by its
        failing
        """
        self.age = None
        self.life_expectancy = None

    def energy_harvested_in_one_year(self, solar_radiation_year_value, performance_ratio=0.75):
        """
        Return the energy harvested in one year by a functioning panel
        :param solar_radiation_year_value: float: radiation received by a panel during an entire year in Wh/m2/year
        :param performance_ratio: float: performance ratio of the pv, on average equals to 0.75
        :return energy_harvested: float: energy harvested by the panel during the year, in kWh/panel/year
        """
        efficiency_loss_function = get_efficiency_loss_function_from_string(self.panel_technology_object.
                                                                            efficiency_function)
        initial_efficiency = self.panel_technology_object.initial_efficiency
        area = self.panel_technology_object.panel_area
        energy_harvested = efficiency_loss_function(initial_efficiency,
                                                    self.age) * solar_radiation_year_value * area \
                           * performance_ratio / 1000
        return energy_harvested

    def energy_harvested_in_one_year(self, irradiance, **kwargs):
        """
        Return the energy harvested in one year by a functioning panel
        :param irradiance: float: radiation received by a panel during a year or a timestep  in Wh/m2
        :return energy_harvested: float: energy harvested by the panel during the year, in Wh/panel
        """
        energy_harvested = self.panel_technology_object.get_energy_harvested_by_panel(irradiance=irradiance,
                                                                                      age=self.age, **kwargs)
        return energy_harvested

    def increment_age_by_one_year(self):
        """
        Simulate a year passing for a panel, making it fail eventually
        """
        if self.is_panel_working():
            self.age += 1
            if self.age is self.life_expectancy:
                self.panel_failed()
