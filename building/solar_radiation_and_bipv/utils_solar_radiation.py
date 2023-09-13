"""
Utils functions for the generation of SensorGrids objects
"""

import logging
import os
import shutil
import subprocess

from ladybug.futil import write_to_file
from honeybee.config import folders
from honeybee_radiance.postprocess.annualdaylight import _process_input_folder
from pollination_handlers.outputs.helper import read_sensor_grid_result

from lbt_recipes.settings import RecipeSettings
from lbt_recipes.recipe import Recipe

user_logger = logging.getLogger("user")
dev_logger = logging.getLogger("dev")


def run_hb_model_annual_irradiance_simulation(hb_model_obj, path_folder_run, path_weather_file,
                                              overwrite=False,
                                              timestep=1, visible=False, north=0,
                                              grid_filter=None,
                                              radiance_parameters='-ab 2 -ad 5000 -lw 2e-05',
                                              silent=False):
    """
    Run the Honeybee annual irradiance simulation on a Honeybee Model.
    :param model : A HB model for which Annual Irradiance will be simulated ( this model must have grids assigned to it)
    :param path_weather_file : A Wea object produced from the Wea components that are under the Light sources tab. Can also be a path to
    a .wea or a .epw file
    :param run_settings : Settings from the "HB recipe Settings" component that specify how the recipe should be run. This
    can also be a text string of recipe settings.
    :param timestep : An integer for the timestep of the input _wea. This value is used to compute average irradiance and
    cumulative radiation.
    :param visible : Boolean to indicate the type of irradiance output, which can be solar (False) or visible (True).
    The output value will still be irradiance (W/m2) when "visible" is selected but these irradiance values will be
    just for the visible portion of the electromagnetic spectrum. The visible irradiance values can be converted into
    illuminance by multiplying them by the Radiance luminous efficacy factor of 179. (Default=False)
    :param north : A number between -360 and 360 for the counterclockwise difference between the North qnd the Y-axis in
    degrees. (Default:0)
    :param grid_filter : Text for a grid identifier or a pattern to filter the sensor grids of the model that are simulated.
    For instance, the sensor grids that have an identifier that starts with first_floor. By default, all grids in the
    model will be simulated.
    :param radiance_parameters : Text for the radiance parameters to be used for ray tracing. (Default : -ab 2 -ad 5000 -lw 2e-05)
    :param run : Set to True to run the Recipe and get results. This input can also be the integer 2 to run the recipe
    silently
    """

    # @ credit LBT

    # Generate the recipe settings
    run_settings = RecipeSettings(folder=path_folder_run, workers=None, reload_old=not overwrite,
                                  report_out=False)

    # create the recipe and set the input arguments
    recipe = Recipe('annual-irradiance')
    recipe.input_value_by_name('model', hb_model_obj)
    recipe.input_value_by_name('wea', path_weather_file)
    recipe.input_value_by_name('timestep', timestep)
    recipe.input_value_by_name('output-type', visible)
    recipe.input_value_by_name('north', north)
    recipe.input_value_by_name('grid-filter', grid_filter)
    recipe.input_value_by_name('radiance-parameters', radiance_parameters)
    # run the recipe
    project_folder = recipe.run(run_settings, radiance_check=True, silent=silent)
    # Compute the cumulative annual irradiance
    path_result = os.path.join(project_folder, "annual_irradiance", "results", "total")
    annual_cum_values = hb_ann_cum_values(path_results=[path_result])

    return annual_cum_values


def move_annual_irr_hb_radiance_results(path_temp_ill_result_file, path_temp_sun_hours_file,
                                        new_ill_file_name, new_sun_hours_file_name, path_result_folder):
    """
    Move the result file from the temp folder to the result folder
    :param path_temp_ill_result_file : Path to the ill result file in the temporary folder
    :param path_temp_sun_hours_file : Path to the sun hours file in the temporary folder
    :param new_ill_file_name : New name for the .ill file
    :param new_sun_hours_file_name : New name for the sun hours file
    :param path_result_folder : Path to the result folder
    """
    # Create the result folder if it doesn't exist
    if not os.path.isdir(path_result_folder):
        os.makedirs(path_result_folder)
    # Delete the file if it already exist to overwrite it
    if os.path.isfile(os.path.join(path_result_folder, new_ill_file_name)):
        os.remove(os.path.join(path_result_folder, new_ill_file_name))
    if os.path.isfile(os.path.join(path_result_folder, new_sun_hours_file_name)):
        os.remove(os.path.join(path_result_folder, new_sun_hours_file_name))
    # move the files
    shutil.move(path_temp_ill_result_file, os.path.join(path_result_folder, new_ill_file_name))
    shutil.move(path_temp_sun_hours_file, os.path.join(path_result_folder, new_sun_hours_file_name))


def hb_ann_cum_values(path_results, hoys=None, grid_filter=None):
    """
    Compute cumulative values from annual irradiance results.
    :param path_results : A list of Annual Radiance result files from either the "HB Annual Daylight" or the "HB Annual
    Irradiance" component (containing the.ill files and the sun-up-hours.text). This can also be just the path to the
    folder containing these result files.
    If it's a path, it must be in a list. For instance : [path_folder]
    :param hoys : An optional number or list of numbers to select the hours of the year (HOYs) for which results will be
    computed. These HOYs can be obtained from the "LB calculate HOY" or the "LB Analysis Period" components. If None,
    all hours of the day will be used.
    :param grid_filter : The name of a grid or a pattern to filter the grids. For instance, first_floor* will simulate only
    the sensor grids that have an identifier that starts with first_floor/ By default, all the grids will be processed.
    :return: A list of cumulative values for each grid in the model. The cumulative values are a list of 8760 values
    """
    # @ credit LBT

    # set up the default values
    grid_filter_ = '*' if grid_filter is None else grid_filter
    hoys_ = [] if hoys is None else hoys
    res_folder = os.path.dirname(path_results[0]) if os.path.isfile(path_results[0]) \
        else path_results[0]

    # check to see if results use the newer numpy arrays
    if os.path.isdir(os.path.join(res_folder, '__static_apertures__')):
        cmds = [folders.python_exe_path, '-m', 'honeybee_radiance_postprocess',
                'post-process', 'cumulative-values', res_folder, '-sf', 'metrics']
        if len(hoys_) != 0:
            hoys_str = '\n'.join(str(h) for h in hoys_)
            hoys_file = os.path.join(res_folder, 'hoys.txt')
            write_to_file(hoys_file, hoys_str)
            cmds.extend(['--hoys-file', hoys_file])
        if grid_filter_ != '*':
            cmds.extend(['--grids-filter', grid_filter_])
        use_shell = True if os.name == 'nt' else False
        process = subprocess.Popen(
            cmds, cwd=res_folder, shell=use_shell,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout = process.communicate()  # wait for the process to finish
        if stdout[-1] != '':
            print(stdout[-1])
            raise ValueError('Failed to compute cumulative values.')
        avg_dir = os.path.join(res_folder, 'metrics', 'cumulative_values')
        if os.path.isdir(avg_dir):
            values = read_sensor_grid_result(avg_dir, 'cumulative', 'full_id', False)

    else:
        # extract the timestep if it exists
        timestep = 1
        tstep_file = os.path.join(res_folder, 'timestep.txt')
        if os.path.isfile(tstep_file):
            with open(tstep_file) as tf:
                timestep = int(tf.readline())

        # parse the sun-up-hours
        grids, sun_up_hours = _process_input_folder(res_folder, grid_filter_)
        su_pattern = parse_sun_up_hours(sun_up_hours, hoys_, timestep)

        # compute the average values
        values = []
        for grid_info in grids:
            ill_file = os.path.join(res_folder, '%s.ill' % grid_info['full_id'])
            dgp_file = os.path.join(res_folder, '%s.dgp' % grid_info['full_id'])
            if os.path.isfile(dgp_file):
                cumul = cumulative_values(dgp_file, su_pattern, timestep)
            else:
                cumul = cumulative_values(ill_file, su_pattern, timestep)
            values.append(cumul)

    return values


def parse_sun_up_hours(sun_up_hours, hoys, timestep):
    """Parse the sun-up hours from the result file .txt file.
    @ credit LBT
    Args:
        sun_up_hours: A list of integers for the sun-up hours.
        hoys: A list of 8760 * timestep values for the hoys to select. If an empty
            list is passed, None will be returned.
        timestep: Integer for the timestep of the analysis.
    """
    if len(hoys) != 0:
        schedule = [False] * (8760 * timestep)
        for hr in hoys:
            schedule[int(hr * timestep)] = True
        su_pattern = [schedule[int(h * timestep)] for h in sun_up_hours]
        return su_pattern


def cumulative_values(ill_file, su_pattern, timestep):
    """Compute average values for a given result file."""
    # @ credit LBT
    cumul_vals = []
    with open(ill_file) as results:
        if su_pattern is None:  # no HOY filter on results
            for pt_res in results:
                values = [float(r) for r in pt_res.split()]
                cumul_vals.append(sum(values) / timestep)
        else:
            for pt_res in results:
                values = [float(r) for r, is_hoy in zip(pt_res.split(), su_pattern) if is_hoy]
                cumul_vals.append(sum(values) / timestep)
    return cumul_vals
