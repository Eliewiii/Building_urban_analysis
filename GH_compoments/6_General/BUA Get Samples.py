"""Get the path to sample data from the library folder
    Output:
        gis_file_list : list of the gis file in the library folder
        path_folder_hbjson : path to the folder containing the hbjon files
        path_hbjson_list : list of the path to the honeybee json files
        path_epw_file_list : list of the path to the epw files
        hb_model_list : list of the path to the honeybee models"""

__author__ = "elie-medioni"
__version__ = "2023.09.06"

ghenv.Component.Name = "BUA Get Sample Data"
ghenv.Component.NickName = 'GetSampleData0'
ghenv.Component.Message = '0.0.0'
ghenv.Component.Category = 'BUA'
ghenv.Component.SubCategory = '6 :: General'
ghenv.Component.AdditionalHelpFromDocStrings = "1"

import os

from honeybee.model import Model

# Get Appdata\local folder
local_appdata = os.environ['LOCALAPPDATA']
path_tool = os.path.join(local_appdata, "Building_urban_analysis")
path_data_libraries = os.path.join(path_tool, "Libraries")

# Get the list of the gis files
path_gis_folder = os.path.join(path_data_libraries, "GIS")
gis_file_list = [os.path.join(path_gis_folder,gis_file_name) for gis_file_name in os.listdir(path_gis_folder)]

# Get the hbjson files
path_folder_hbjson = os.path.join(path_data_libraries, "hbjson_models")
path_hbjson_list = [os.path.join(path_folder_hbjson,hbjson_file_name) for hbjson_file_name in os.listdir(path_folder_hbjson)]

# Get the epw files
path_epw_folder = os.path.join(path_data_libraries, "EPW")
path_epw_file_list = [os.path.join(path_epw_folder,epw_file_name) for epw_file_name in os.listdir(path_epw_folder)]

# Get the hb models
hb_model_list = [ Model.from_hbjson(path_hbjson) for path_hbjson in path_hbjson_list]
