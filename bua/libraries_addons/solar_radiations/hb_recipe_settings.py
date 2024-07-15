from lbt_recipes.settings import RecipeSettings



def hb_recipe_settings(path_folder, workers=None, reload_old=True, report_out=False):

    """ Args
    path_folder : Path to a project folder in which the recipe will be executed. If None, the default folder for the Recipe
    will be used.
    workers : An integer to set the number of CPUs used in the execution of the recipe. This number should not exceed
    the number of CPUs on the machine and should be lower if other tasks are running while the simulation is running.
    If unspecified, it will automatically default to one less than the nuber of CPUs currently available on the machine.
    (Default : None)
    reload_old : A boolean to indicate whether existing results for a given model and recipe should be reloaded (if
    they are found) instead of re-running the entire recipe from the beginning. If False or None, any existing results
    will be overwritten by the new simulation.
    report_out : A boolean to indicate whether the recipe progress should be displayed in the cmd window (False) or
    output from the "report" recipe component (True). Outputting  from the component can be useful for debugging but
    recipe reports can often be very long, so it can slow grasshopper slightly. (Default : False)"""

    # create the settings
    settings = RecipeSettings(path_folder, workers, reload_old, report_out)
    return settings
