try:
    from lbt_recipes.recipe import Recipe
except ImportError as e:
    raise ImportError('\nFailed to import lbt_recipes:\n\t{}'.format(e))


def hb_ann_irr_sim(model, path_weather_file, run_settings, timestep=1, visible=False, north=0,
                   grid_filter=None, radiance_parameters='-ab 2 -ad 5000 -lw 2e-05', run=True):
    """Args
    model : A HB model for which Annual Irradiance will be simulated ( this model must have grids assigned to it)
    path_weather_file : A Wea object produced from the Wea components that are under the Light sources tab. Can also be a path to
    a .wea or a .epw file
    run_settings : Settings from the "HB recipe Settings" component that specify how the recipe should be run. This
    can also be a text string of recipe settings.
    timestep : An integer for the timestep of the input _wea. This value is used to compute average irradiance and
    cumulative radiation.
    visible : Boolean to indicate the type of irradiance output, which can be solar (False) or visible (True).
    The output value will still be irradiance (W/m2) when "visible" is selected but these irradiance values will be
    just for the visible portion of the electromagnetic spectrum. The visible irradiance values can be converted into
    illuminance by multiplying them by the Radiance luminous efficacy factor of 179. (Default=False)
    north : A number between -360 and 360 for the counterclockwise difference between the North qnd the Y-axis in
    degrees. (Default:0)
    grid_filter : Text for a grid identifier or a pattern to filter the sensor grids of the model that are simulated.
    For instance, the sensor grids that have an identifier that starts with first_floor. By default, all grids in the
    model will be simulated.
    radiance_par_ : Text for the radiance parameters to be used for ray tracing. (Default : -ab 2 -ad 5000 -lw 2e-05)
    run : Set to True to run the Recipe and get results. This input can also be the integer 2 to run the recipe
    silently"""

    # create the recipe and set the input arguments
    recipe = Recipe('annual-irradiance')
    recipe.input_value_by_name('model', model)
    recipe.input_value_by_name('wea', path_weather_file)
    recipe.input_value_by_name('timestep', timestep)
    recipe.input_value_by_name('output-type', visible)
    recipe.input_value_by_name('north', north)
    recipe.input_value_by_name('grid-filter', grid_filter)
    recipe.input_value_by_name('radiance-parameters', radiance_parameters)

    # run the recipe
    silent = True if run > 1 else False
    project_folder = recipe.run(run_settings, radiance_check=True, silent=silent)

    return project_folder
