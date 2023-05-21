"""
Panel class, modeling solar panels, to track the age and energy production of panels on buildings
"""

# todo @Julius and Elie, make a small documentation to explain how we compute the time of failure
#  plus all the hypothesis

from math import log, ceil
import random

from solar_panel.pvmaterial import PanelTechnology


class Panel:
    """ """

    def __init__(self, index, pv_technology):
        """ initialize a panel
        index : identifies the panel
        age : number of years the pv has been working
        lifetime : number of years it will work since its installation (deduced by the probabilistic law of weibull)
        During the initialization, we suppose that age = 0 and lifetime = 0 ie. the panel has not begun to work yet
        panel_technology_object : a PanelTechnology object """

        self.index = index
        self.age = 0
        self.life_expectancy = 0
        self.panel_technology_object = pv_technology

    def is_panel_working(self):
        """ If the panel's life expectancy is different from 0, it means it has been switched on and that it is
        working (True)
        Else, if its life expectancy equals 0, then the panel is not working (False)"""
        return self.life_expectancy != 0

    def panel_not_in_last_year(self):
        """ The PV is working but its also not in its last year of functioning, ie. it doesn't need to be switched
        off"""
        self.is_panel_working() and self.age < self.life_expectancy

    def switch_on_panel(self):
        """ Switch on the panel by calculating its lifetime thanks to the law of weibull"""
        pv_technology = self.panel_technology_object
        life_expectancy = pv_technology.PanelTechnology.get_life_expectancy_of_a_panel()
        self.life_expectancy = life_expectancy

    def switch_off_panel(self):
        """ Switch off the panel by initializing its age and its life expectancy to 0"""
        self.age = 0
        self.life_expectancy = 0

    def add_year_to_panel(self):
        """ Add one year to the panel
        If the panel's age equals its life expectancy, then the panel is switched off"""
        if self.is_panel_working() and self.panel_not_in_last_year():
            self.age += 1
