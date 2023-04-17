try:
    from lbt_recipes.settings import RecipeSettings
except ImportError as e:
    raise ImportError('\nFailed to import lbt_recipes:\n\t{}'.format(e))


def hb_recipe_settings(_folder_, _workers_=None, reload_old_=True, report_out_=False):

    """ Args
    _folder_ : Path to a project folder in which the recipe will be executed. If None, the default folder for the Recipe
    will be used.
     _workers_ : An integer to set the number of CPUs used in the execution of the recipe. This number should not exceed
     the number of CPUs on the machine and should be lower if other tasks are running while the simulation is running.
     If unspecified, it will automatically default to one less than the nuber of CPUs currently available on the machine.
     (Default : None)
     reload_old_ : A boolean to indicate whether existing results for a given model and recipe should be reloaded (if
     they are found) instead of re-running the entire recipe from the beginning. If False or None, any existing results
     will be overwritten by the new simulation.
     report_out_ : A boolean to indicate whether the recipe progress should be displayed in the cmd window (False) or
     output from the "report" recipe component (True). Outputting  from the component can be useful for debugging but
     recipe reports can often be very long so it can slow grasshopper slightly. (Default : False)"""

    # create the settings
    settings = RecipeSettings(_folder_, _workers_, reload_old_, report_out_)
    return settings
