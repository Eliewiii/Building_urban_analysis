"""

"""

from mains_tool.utils_general import *
from mains_tool.step_methods.utils_step_methods import *
class SimulationPostProcessingAndPlots:
    """ todo @Elie"""
    @staticmethod
    def generate_hb_model_contains_all_building_envelopes_to_plot_Grasshopper(urban_canopy_object,path_folder_simulation):
        """
            todo @Elie, change it, so tha it is writen in the json file
        """
        urban_canopy_object.make_HB_model_envelops_from_buildings(path_folder=path_folder_simulation)
        logging.info("HB model for the building envelop created successfully")
