"""Parameters for the merging face algorithm.
    Inputs:
        _orient_roof_according_to_building_orientation_: bool: default=True if True, the roof mesh will be oriented
        according to the building orientation, usefull especially when generating a mesh for the solar radiation.
        _north_angle_: float : default=0: angle of the north in degrees compared to orientation of the HB model
        _overwrite_: bool: default=False: if True, the existing merged faces will be overwritten
    Output:
        replacement_scenario_parameters_dict: Dictionary containing the parameters for the BIPV replacement scenarios"""

__author__ = "elie-medioni"
__version__ = "2023.09.06"

ghenv.Component.Name = "BUA Merge Face Parameters"
ghenv.Component.NickName = 'MergeFaceParameters'
ghenv.Component.Message = '0.0.0'
ghenv.Component.Category = 'BUA'
ghenv.Component.SubCategory = '3 :: Building manipulation'

import json

# Check if the parameters are valid
if _north_angle_ is not None and not 0<=_north_angle_<=360:
    raise ValueError("The north angle is not valid, it should be between 0 and 360 degrees")

merge_face_parameters= {"orient_roof_according_to_building_orientation": _orient_roof_according_to_building_orientation_,
                        "north_angle": _north_angle_,
                        "overwrite": _overwrite_}

merge_face_parameters = json.dumps(merge_face_parameters)