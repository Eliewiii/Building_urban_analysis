

import os
import json


from time import time
from copy import deepcopy

from honeybee.model import Model
from honeybee_energy.run import to_openstudio_osw, run_osw, run_idf
from honeybee.model import Model


path_hbjson = r"C:\Users\elie-medioni\OneDrive\OneDrive - Technion\Ministry of Energy Research\Papers\CheckContext\Simulations_Elie\Inputs\UBES_mvfc\Residential\context_1\Res_5-flrs_NoContext-1.hbjson"

path_hbjson_simulation_parameters = "C:\\Users\\elie-medioni\\AppData\\Local\\Building_urban_analysis\\Simulation_temp\\temporary_files\\BES_temp_simulation\\uc_ubes_hb_simulation_parameters.json"
path_epw_file = "C:\\Users\\elie-medioni\\AppData\\Local\\Building_urban_analysis\\Simulation_temp\\temporary_files\\BES_temp_simulation\\uc_epw_ubes.epw"
path_building_bes_temp_folder = "C:\\Users\\elie-medioni\\OneDrive\\OneDrive - Technion\\Ministry of Energy Research\\Papers\\CheckContext\\Simulations_Elie\\trash"
hb_model = Model.from_hbjson(path_hbjson)
hb_model_copy = hb_model.duplicate()
if len(hb_model_copy.stories) == 0 and len(hb_model_copy.rooms) != 0:
    hb_model_copy.assign_stories_by_floor_height()

hb_model_dict = hb_model_copy.to_dict(triangulate_sub_faces=True)
hb_model_copy.properties.energy.add_autocal_properties_to_dict(hb_model_dict)

path_hbjson_file = os.path.join(path_building_bes_temp_folder, '{}.hbjson'.format(hb_model.identifier))

with open(path_hbjson_file, 'w') as fp:
    json.dump(hb_model_dict, fp)

# Export the Honeybee Model to a hbjson file in the path_building_bes_temp_folder
# path_hbjson_file = hb_model_obj.to_hbjson(name=self.building_id, folder=path_building_bes_temp_folder)
silent =False
osw = to_openstudio_osw(osw_directory=path_building_bes_temp_folder,
                        model_path=path_hbjson_file,
                        sim_par_json_path=path_hbjson_simulation_parameters,
                        epw_file=path_epw_file)
## Run simulation in OpenStudio to generate IDF ##
(path_osm, path_idf) = run_osw(osw, silent=silent)

run_idf(idf_file_path=path_idf, epw_file_path=path_epw_file, silent=silent)
