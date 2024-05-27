"""Get the path to sample data from the library folder
    Inputs:
        _run : Plug in a boolean toggle to run the component and load the samples
    Output:
        path_sample_gis : list of the gis file in the library folder
        path_sample_epw_file : list of the path to the epw files
        path_sample_folder_hbjson : path to the folder containing the hbjon files
        path_sample_hbjson_list : list of the path to the honeybee json files
        sample_hb_model_list : list of the path to the honeybee models"""

__author__ = "elie-medioni"
__version__ = "2024.05.27"

from ghpythonlib.componentbase import executingcomponent as component


ghenv.Component.Name = "BUA Get Sample Data For Example File"
ghenv.Component.NickName = 'GetSampleDataForExampleFile'
ghenv.Component.Message = '1.1.0'
ghenv.Component.Category = 'BUA'
ghenv.Component.SubCategory = '7 :: General'

import os

from honeybee.model import Model

if _run:
    # Get Appdata\local folder
    local_appdata = os.environ['LOCALAPPDATA']
    path_tool = os.path.join(local_appdata, "Building_urban_analysis")
    path_data_libraries_samples = os.path.join(path_tool, "Libraries","Samples_for_example_file")

    # Get the list of the gis files
    path_gis_folder = os.path.join(path_data_libraries_samples, "gis")
    path_sample_gis = [os.path.join(path_gis_folder, gis_file_name) for gis_file_name in os.listdir(path_gis_folder)][0]

    # Get the epw files
    path_epw_folder = os.path.join(path_data_libraries_samples, "epw")
    path_sample_epw_file = [os.path.join(path_epw_folder, epw_file_name) for epw_file_name in os.listdir(path_epw_folder)][0]

    # Get the hbjson files
    path_sample_folder_hbjson = os.path.join(path_data_libraries_samples, "hbjson_models")
    path_sample_hbjson_list = [os.path.join(path_sample_folder_hbjson, hbjson_file_name) for hbjson_file_name in
                        os.listdir(path_sample_folder_hbjson)]

    # Get the hb models
    sample_hb_model_list = [Model.from_hbjson(path_hbjson) for path_hbjson in path_sample_hbjson_list]
