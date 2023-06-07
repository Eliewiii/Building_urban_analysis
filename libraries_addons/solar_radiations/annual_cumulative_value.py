import os
import subprocess
from libraries_addons.utils_libraries_addons import *
from honeybee_radiance.postprocess.annualdaylight import _process_input_folder


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


def hb_ann_cum_values(path_results, hoys=None, grid_filter=None):
    """Args:
    path_results : A list of Annual Radiance result files from either the "HB Annual Daylight" or the "HB Annual
    Irradiance" component (containing the.ill files and the sun-up-hours.text). This can also be just the path to the
    folder containing these result files.
    If it's a path, it must be in a list. For instance : [path_folder]
    hoys : An optional number or list of numbers to select the hours of the year (HOYs) for which results will be
    computed. These HOYs can be obtained from the "LB calculate HOY" or the "LB Analysis Period" components. If None,
    all hours of the day will be used.
    grid_filter : The name of a grid or a pattern to filter the grids. For instance, first_floor* will simulate only
    the sensor grids that have an identifier that starts with first_floor/ By default, all the grids will be processed.
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
