""" Class containing all the urban canopy (buildings, surfaces etc...) """

import os
import subprocess

from honeybee_energy import run
from honeybee_energy.config import folders
from ladybug.futil import write_to_file




def run_idf_windows_modified(idf_file_path, epw_file_path=None, expand_objects=True,
                             silent=False, path_energyplus_exe=None):
    """Run an IDF file through energyplus on a Windows-based operating system.

    A batch file will be used to run the simulation.

    Modified by @Elie
    BATCH FILE MODIFIED FROM THE ORIGINAL VERSION
    I ADDED ONE MORE OPTION TO GET CSV FILE AS OUTPUTS AAS WELL

    Args:
        idf_file_path: The full path to an IDF file.
        epw_file_path: The full path to an EPW file. Note that inputting None here
            is only appropriate when the simulation is just for design days and has
            no weather file run period. (Default: None).
        expand_objects: If True, the IDF run will include the expansion of any
            HVAC Template objects in the file before beginning the simulation.
            This is a necessary step whenever there are HVAC Template objects in
            the IDF but it is unnecessary extra time when they are not
            present. (Default: True).
        silent: Boolean to note whether the simulation should be run silently
            (without the batch window). If so, the simulation will be run using
            subprocess with shell set to True. (Default: False).
        path_energyplus_exe: The full path to the EnergyPlus executable, not the modified version
            from the LBT, the last version downloaded from the official website.


    Returns:
        Path to the folder out of which the simulation was run.
    """
    # check and prepare the input files
    directory = run.prepare_idf_for_simulation(idf_file_path, epw_file_path)

    if not silent:  # run the simulations using a batch file
        # generate various arguments to pass to the energyplus command
        epw_str = '-w "{}"'.format(os.path.abspath(epw_file_path)) \
            if epw_file_path is not None else ''
        # idd_str = '-i "{}"'.format(folders.energyplus_idd_path)
        idf_str = '-r {}'.format("in.idf")
        working_drive = directory[:2]
        # write the batch file
        batch = '{}\ncd "{}"\n"{}" {} {}'.format(
            working_drive, directory, path_energyplus_exe, epw_str,
            idf_str)
        batch_file = os.path.join(directory, 'in.bat')
        write_to_file(batch_file, batch, True)
        os.system('"{}"'.format(batch_file))  # run the batch file
    else:  # run the simulation using subprocess
        cmds = [folders.energyplus_exe, '-i ', folders.energyplus_idd_path, '-r ', idf_file_path]
        if epw_file_path is not None:
            cmds.append('-w')
            cmds.append(os.path.abspath(epw_file_path))
        if expand_objects:
            cmds.append('-x')
        process = subprocess.Popen(
            cmds, cwd=directory, stdout=subprocess.PIPE, shell=True)
        process.communicate()  # prevents the script from running before command is done

    return directory


"""
Other option to run idf directly through honeybee-energy :
in honeybee-energy\honeybee_energy\\run.py

run_idf(idf_file_path, epw_file_path=None, expand_objects=True, silent=False)

"""