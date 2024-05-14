"""Filter Context
    Inputs:
        path_simulation_folder_: Path to the folder. Default = Appdata\Local\Building_urban_analysis\Simulation_temp
        building_id_list_: list of ints: list of buildings we want to run the simulation on
        _path_weather_file: Path to the weather file. Default = todo
        _north_: A number between -360 and 360 for the counterclockwise
            difference between the North and the positive Y-axis in degrees.
            90 is West and 270 is East. (Default: 0)
        _overwrite_: bool: True if we want to rerun the simulation for buildings that were simulated before.
                Otherwise they will be skipped and speed up the computation. (Default: False)
    Output:
        report: report
        path_simulation_folder_: Path to the folder."""

__author__ = "Eliewiii"
__version__ = "2023.08.21"

ghenv.Component.Name = "BUA Filter Context"
ghenv.Component.NickName = 'FilterContext'
ghenv.Component.Message = '0.0.0'
ghenv.Component.Category = 'BUA'
ghenv.Component.SubCategory = '4 :: Context Selection'
ghenv.Component.AdditionalHelpFromDocStrings = "1"

def clean_path(path):
    path = path.replace("\\", "/")
    return (path)
