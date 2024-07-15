"""
Panel class, modeling solar panels, to track the age and energy production of panels on buildings
"""

from bua.bipv.bipv_technology import BipvTechnology


class BipvPanel:
    """ """

    def __init__(self, index, pv_technology_object: BipvTechnology):
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

    def initialize_or_replace_panel(self, pv_tech_obj=None):
        """
        Initialize the panel
        """
        if pv_tech_obj is not None:
            self.panel_technology_object = pv_tech_obj
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

    def get_hourly_power_generation_over_a_year(self, hourly_irradiance_list, **kwargs):
        """
        Return the hourly power generation of a panel over a year.
        The hourly irradiance covers only the sun hours, thus it does not contain the usual 8760 hours of a year.
        :param hourly_irradiance_list: float: hourly radiation received by a panel during a year or a timestep  in Wh/m2
        :return energy_harvested: float: energy harvested by the panel during the year, in Wh/panel
        """
        if self.is_panel_working():
            hourly_power_generation_list = self.panel_technology_object.get_hourly_power_generation_over_a_year_by_panel(
                hourly_irradiance_list=hourly_irradiance_list,
                age=self.age, **kwargs)
        else:
            hourly_power_generation_list = [0. for i in hourly_irradiance_list]
        return hourly_power_generation_list

    def increment_age_by_one_year(self):
        """
        Simulate a year passing for a panel, making it fail eventually
        """
        if self.is_panel_working():
            self.age += 1
            if self.age is self.life_expectancy:
                self.panel_failed()
