"""
Panel class, modeling solar panels, to track the age and energy production of panels on buildings
"""

# todo @Julius and Elie, make a small documentation to explain how we compute the time of failure
#  plus all the hypothesis

from math import log, ceil
import random

from solar_panel.pv_panel_technology import PvPanelTechnology


class PvPanel:
    """ """

    def __init__(self, index, pv_technology_object):
        """ initialize a panel
        index : identifies the panel
        age : number of years the pv has been working
        lifetime : number of years it will work since its installation (deduced by the probabilistic law of weibull)
        During the initialization, we suppose that age = 0 and lifetime = 0 ie. the panel has not begun to work yet
        panel_technology_object : a PanelTechnology object """

        self.index = index
        self.age = None
        self.life_expectancy = None
        self.panel_technology_object = pv_technology_object

    def is_panel_working(self):
        """ If the panel's life expectancy is different from 0, it means it has been switched on and that it is
        working (True)
        Else, if its life expectancy equals 0, then the panel is not working (False)"""
        return self.life_expectancy is not None

    def panel_not_in_last_year(self):
        """ The PV is working but its also not in its last year of functioning, ie. it doesn't need to be switched
        off"""
        self.is_panel_working() and self.age < self.life_expectancy

    def switch_on_panel(self):
        """ Switch on the panel by calculating its lifetime thanks to the law of weibull"""
        pv_technology = self.panel_technology_object
        # todo @Hilany, attention ! pas besoin d'appeler la classe !, on appelle la classe que pour les @classmethods, l'objet en lui meme connait ses propres methodes
        #  it suffit d'ecrire  pv_technology.get_life_expectancy_of_a_panel()
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

        # todo New functions to me (Elie)

    def is_panel_working(self):
        """ If the panel's life expectancy is different from 0, it means it has been switched on and that it is
        working (True)
        Else, if its life expectancy equals 0, then the panel is not working (False)"""
        return self.life_expectancy is not 0

    def panel_failed(self):
        """ Switch off the panel by initializing its age and its life expectancy to 0"""
        self.age = None
        self.life_expectancy = None
        dmfa_waste = None  # todo @Hilany, put the proper function that computes the waste (a priori a function of PvTechnology)
        return dmfa_waste

    def pass_year(self, year):
        """
        Simulate a year passing for a panel
        :param year: year of the simulation, could impact the efficiency of the panel, if we assume tha the efficiency
        of the new panels is increasing every through the years
        :return energy_produced: float : energy produced by the panel through the year
        :return dmfa_waste: float : dmfa waste generate by the panel when it fails


        """
        energy_produced, dmfa_waste = 0., 0.

        if self.is_panel_working():
            # get the energy produced by the panel over the year with the proper efficiency
            energy_produced = None  # todo @Hilany, add the function to compute the energy produced during this year by the panel
            #  might need to add an input
            #  for now, let's take the total energy received by the panel over the year (contained in one of the files from HB radiance)
            #  and apply the proper efficiency that depends on the age of the panel, we'll complexify later

            # increase the age
            self.age += 1

            # If panel reach life expectancy, it fails and generate dmfa waste
            if self.age is self.life_expectancy:
                dmfa_waste = self.panel_failed()

        return energy_produced, dmfa_waste

    def replace_panel(self):
        """
        Replace the panel with a new one, leading the LCA carbon footprint
        """
        # Get a life expectancy according to the life expectancy distribution of the pv technology
        self.life_expectancy = self.panel_technology_object.get_life_expectancy_of_a_panel()
        # put back the age to 0
        self.age = 0
        # get the LCA carbon footprint for one panel according to its pv technology
        lca_carbon_footprint = self.pv_technology.carbon_footprint_manufacturing

        return lca_carbon_footprint
