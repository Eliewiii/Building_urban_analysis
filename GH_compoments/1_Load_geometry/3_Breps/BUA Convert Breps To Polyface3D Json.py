"""Convert a list of closed breps to Polyface3D stored in a json file (mostly to send them to the urban canopy)
    Inputs:
        _close_brep_list: List of closed breps to convert to Polyface3D stored in a json file
        (mostly to send them to the urban canopy)
        _prefix: Prefix to add to the identifier of the Polyface3D object. Make sure it is unique to this project
        _file_name_ : Name of the json file to create without extension (Default: polyface3d)
        _path_folder: True if you want to keep the context of the HB Model of the hbjsons. (Default: False)
        _run: Plug in a button to run the component
    Output:
        path_polyface3d_json_file: path to the json file containing the polyface3d object"""

ghenv.Component.Name = "BUA Convert Breps To Polyface3D Json"
ghenv.Component.NickName = 'ConvertBrepsToPolyface3DJson'
ghenv.Component.Message = '0.0.0'
ghenv.Component.Category = 'BUA'
ghenv.Component.SubCategory = '1 :: Load geometry'

import os
import json

from ladybug_rhino.togeometry import to_polyface3d


def clean_path(path):
    path = path.replace("\\", "/")
    return (path)



if _path_folder is not None and os.path.isdir(clean_path(_path_folder)):
    if _file_name_ is None or _file_name_ == "":
        _file_name_ = "polyface3d"
    path_polyface3d_json_file = os.path.join(clean_path(_path_folder), _file_name_ + ".json")
else:
    path_polyface3d_json_file = None
    print("The folder path is not valid")

if _run and _close_brep_list is not None and _close_brep_list != [] and _prefix is not None and _prefix != "" and path_polyface3d_json_file is not None:
    # Initialize the list of polyface3d
    polyface3d_dict = {}
    # Convert the closed breps to polyface3d
    for index, brep in enumerate(_close_brep_list):
        polyface3d_dict["{}_{}".format(_prefix, index)] = to_polyface3d(brep).to_dict()  # todo: finish this

    # Create the json file
    with open(path_polyface3d_json_file, 'w') as outfile:
        json.dump(polyface3d_dict, outfile)
