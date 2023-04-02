try:
    from lbt_recipes.recipe import Recipe
except ImportError as e:
    raise ImportError('\nFailed to import lbt_recipes:\n\t{}'.format(e))


def hb_ann_irr_sim(_model, _wea, run_settings_, _timestep_=1, visible_=False, north_=0, grid_filter_=None, radiance_par_='-ab 2;-ad 5000,-lw 2e-05', _run=True):

    """Args
    _model : A HB model for which Annual Irradiance will be simulated ( this model must have grids assigned to it)
     _wea : A Wea object produced from the Wea components that are under the Light sources tab. Can also be a path to
     a .wea or a .epw file
     _timestep_ : An integer for the timestep of the input _wea. This value is used to compute average irradiance and
     cumulative radiation.
     visible_ : Boolean to indicate the type of irradiance output, which can be solar (False) or visible (True).
     The output value will still be irradiance (W/m2) when "visible" is selected but these irradiance values will be
     just for the visible portion of the electromagnetic spectrum. The visible irradiance values can be converted into
     illuminance by multiplying them by the Radiance luminous efficacy factor of 179. (Default=False)
     north_ : A number between -360 and 360 for the counterclockwise difference between the North qnd the Y-axis in
     degrees. (Default:0)
     grid_filter_ : Text for a grid identifier or a pattern to filter the sensor grids of the model that are simulated.
     For instance, the sensor grids that have an identifier that starts with first_floor. By default, all grids in the
     model will be simulated.
     radiance_par_ : Text for the radiance parameters to be used for ray tracing. (Default : -ab 2 -ad 5000 -lw 2e-05)
     run_settings_ : Settings from the "HB recipe Settings" component that specify how the recipe should be run. This
     can also be a text string of recipe settings.
      _run : Set to True to run the Recipe and get results. This input can also be the integer 2 to run the recipe
      silently"""

    # create the recipe and set the input arguments
    recipe = Recipe('annual-irradiance')
    recipe.input_value_by_name('model', _model)
    recipe.input_value_by_name('wea', _wea)
    recipe.input_value_by_name('timestep', _timestep_)
    recipe.input_value_by_name('output-type', visible_)
    recipe.input_value_by_name('north', north_)
    recipe.input_value_by_name('grid-filter', grid_filter_)
    recipe.input_value_by_name('radiance-parameters', radiance_par_)

    # run the recipe
    silent = True if _run > 1 else False
    project_folder = recipe.run(run_settings_, radiance_check=True, silent=silent)


    return project_folder
