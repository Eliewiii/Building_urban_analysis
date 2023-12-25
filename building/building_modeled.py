"""
BuildingModeled class, representing one building in an urban canopy that will be converted in HB models
as they will be simulated
"""

import os
import logging
import matplotlib.pyplot as plt

from ladybug_geometry.geometry3d import Vector3D
from honeybee.model import Model
from honeybee_radiance.sensorgrid import SensorGrid

from building.building_basic import BuildingBasic
from building.context_filter.building_shading_context import BuildingShadingContextFilter
# from building.context_filter.building_lwr_context import BuildingLWRContext  # Useful later
from building.solar_radiation_and_bipv.solar_rad_and_BIPV import SolarRadAndBipvSimulation
from building.merge_hb_model_faces.merge_hb_model_faces import merge_facades_and_roof_faces_in_hb_model

from libraries_addons.hb_model_addons import HbAddons
from libraries_addons.solar_radiations.add_sensorgrid_hb_model import get_hb_faces_facades, get_hb_faces_roof, \
    get_lb_mesh, get_lb_mesh_BUA, create_sensor_grid_from_mesh
from libraries_addons.solar_radiations.hb_recipe_settings import hb_recipe_settings
from libraries_addons.solar_radiations.annual_irradiance_simulation import hb_ann_irr_sim
from libraries_addons.solar_radiations.annual_cumulative_value import hb_ann_cum_values
from libraries_addons.solar_panels.useful_functions_solar_panel import load_panels_on_sensor_grid, \
    loop_over_the_years_for_solar_panels, beginning_end_of_life_lca_results_in_lists, \
    results_from_lists_to_dict, \
    get_cumul_values, add_elements_of_two_lists, transform_to_linear_function, find_intersection_functions, \
    generate_step_function

user_logger = logging.getLogger("user")
dev_logger = logging.getLogger("dev")


class BuildingModeled(BuildingBasic):
    """BuildingBasic class, representing one building in an urban canopy."""

    # todo :make the lb_face_footprint optional in the BuildingBasic class
    def __init__(self, identifier, lb_face_footprint=None, urban_canopy=None, building_index_in_gis=None,
                 **kwargs):
        # Initialize with the inherited attributes from the BuildingBasic parent class
        super().__init__(identifier, lb_face_footprint, urban_canopy, building_index_in_gis)
        # get the values from the original BuildingBasic object (if there is one) through **kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)
        # Honeybee model
        self.hb_model_obj = None
        self.hb_model_dict = None
        self.merged_faces_hb_model_dict = None  # todo @Elie IMPORTANT, move this obj as well
        # Status of the building
        self.to_simulate = False
        self.is_target = False
        # Shading computation
        self.shading_context_obj = BuildingShadingContextFilter()

        # Solar and panel radiation
        self.solar_radiation_and_bipv_simulation_obj = SolarRadAndBipvSimulation()

        self.sensor_grid_dict = {'roof': None, 'facades': None}
        self.panels = {"roof": None, "facades": None}
        self.results_panels = {"roof": None, "facades": None, "Total": None}

    def load_HB_attributes(self):
        """
        Load the attributes that cannot be pickled from equivalent attribute dict.
        """
        # Convert the hb_model_dict to hb_model_obj
        self.hb_model_obj = Model.from_dict(self.hb_model_dict)  # todo: test if it works
        self.hb_model_dict = None
        # Load attributes in the context filter object after pickling
        self.shading_context_obj.load_from_pkl()

    def pickle_HB_attributes(self):
        """
        Convert the hb_model_obj to hb_model_dict to be able to pickle it.
        """
        # Convert the hb_model_obj to hb_model_dict
        self.hb_model_dict = self.hb_model_obj.to_dict()  # todo: test if it works
        self.hb_model_obj = None
        # Prepare attributes in the context filter objects
        self.shading_context_obj.prepare_for_pkl()

        # todo : maybe add more properties to modify before pickling to avoid locked class issue

    @classmethod
    def from_building_basic(cls, building_obj, is_target=False, is_simulated=False,
                            layout_from_typology=False, automatic_floor_subdivision=False,
                            properties_from_typology=True):
        """
        Create a BuildingModeled object from a BuildingBasic object
        :return: building_HB_model : BuildingModeled object
        """
        if isinstance(building_obj, cls):
            return building_obj
        else:
            # Make the HB model from the building object
            HB_model = building_obj.to_HB_model(layout_from_typology=layout_from_typology,
                                                automatic_subdivision=automatic_floor_subdivision,
                                                properties_from_typology=properties_from_typology)
            # get the attributes of the building_obj (it extract all attributes, even the ones that are used
            # to create the object), but it doesn't matter, it is just a bit redundant
            kwargs = {attr: getattr(building_obj, attr) for attr in dir(building_obj) if
                      not attr.startswith('__')}
            # create the BuildingModeled object from the BuildingBasic object
            building_HB_model = cls(building_obj.id, building_obj.lb_face_footprint,
                                    building_obj.urban_canopy,
                                    building_obj.index_in_gis, **kwargs)

            #
            building_HB_model.to_simulate = is_simulated
            building_HB_model.is_target = is_target

            building_HB_model.hb_model_obj = HB_model

            return building_HB_model
            # todo : change if needed where the dictionary of the urban canopy is pointing, to point to the new object

    @classmethod
    def make_buildingmodeled_from_hbjson(cls, path_hbjson, is_target=False, keep_context=False, urban_canopy=None):
        """
        Create a BuildingModeled object from a HBJSON file
        :return: building_hb_model : BuildingModeled object
        """
        # Load the HB model from the hbjson file
        hb_model = Model.from_hbjson(path_hbjson)
        # get the identifier the
        identifier = hb_model.identifier
        # create the BuildingModeled object from the HB model
        building_modeled_obj = cls(identifier)
        try:
            # Try to extract certain characteristics of the model from the hb_model
            elevation, height = HbAddons.elevation_and_height_from_HB_model(hb_model)
        except:
            # todo @Elie: Check if this is the correct message.
            err_message = "Cannot extract elevation and height from the Honeybee model."
            user_logger.error(err_message)
            dev_logger.error(err_message, exc_info=True)
            raise AttributeError(err_message)
        # Keep the context of the building
        if keep_context and (hb_model.shades != [] and hb_model.shades is not None):
            building_modeled_obj.shading_context_obj.get_hb_shades_from_hb_model(hb_model)
        hb_model.remove_all_shades()
        # Set the attributes of the BuildingModeled object
        building_modeled_obj.hb_model_obj = hb_model
        building_modeled_obj.urban_canopy = urban_canopy
        building_modeled_obj.elevation = elevation
        building_modeled_obj.height = height
        building_modeled_obj.is_target = is_target

        try:
            # todo @Elie : make the lb_face_footprint from the hb_model
            building_modeled_obj.lb_face_footprint = HbAddons.make_LB_face_footprint_from_HB_model(
                HB_model=hb_model)
        except:
            # todo @Elie: Check if this is the correct message.
            err_message = "Cannot make the Ladybug face footprint from the Honeybee model."
            user_logger.error(err_message)
            # dev_logger.error(err_message, exc_info=True)
            raise AttributeError(err_message)
        # todo @Elie : finish the function (and check if it works)
        building_modeled_obj.moved_to_origin = True  # we assumed that the HB model is already in the proper place within the urban canopy

        return building_modeled_obj, identifier

    def move(self, vector):
        """
        Move the building
        :param vector:
        :return:
        """
        # move the LB footprint
        if self.lb_face_footprint is not None:
            self.lb_face_footprint = self.lb_face_footprint.move(
                Vector3D(vector[0], vector[1], 0))  # the footprint is moved only in the x and y directions
        # adjust the elevation
        if self.elevation is not None:
            self.elevation = self.elevation + vector[2]
        # make it moved
        moving_vector = Vector3D(vector[0], vector[1], vector[2])
        self.hb_model_obj.move(moving_vector)  # the model is moved fully
        self.merged_faces_hb_model_dict = Model.from_dict(self.merged_faces_hb_model_dict).move(
            moving_vector).to_dict()  # todo check
        self.moved_to_origin = True

    def make_merged_faces_hb_model(self, orient_roof_mesh_to_according_to_building_orientation=True,
                                   north_angle=0):
        """
        Make a HB model with the faces merged. Useful for mesh generation and to simplify the geometry of the model
        for context shading computation.
        :param orient_roof_mesh_to_according_to_building_orientation: bool: default=True, if True, the roof mesh
            will be oriented according to the orientation of the building
        :param north_angle: float: default=0, angle of the north in degree
        """
        merged_faces_hb_model_obj = merge_facades_and_roof_faces_in_hb_model(hb_model_obj=self.hb_model_obj,
                                                                             orient_roof_mesh_to_according_to_building_orientation=orient_roof_mesh_to_according_to_building_orientation,
                                                                             north_angle=north_angle)
        self.merged_faces_hb_model_dict = merged_faces_hb_model_obj.to_dict()

    def perform_first_pass_context_filtering(self, uc_building_id_list, uc_building_bounding_box_list,
                                             min_vf_criterion=0.01, overwrite=True):
        """
        Perform the first pass of the context filtering algorithm on the building.
        :param uc_building_id_list: list of str: list of the building IDs in the urban canopy
        :param uc_building_bounding_box_list: list of Ladybug Polyface3D: list of the bounding boxes of the buildings
            in the urban canopy
        :param min_vf_criterion: float: default=0.01, minimum view factor criterion for the first pass of the
            context filtering algorithm
        :param overwrite: bool: default=False, if True, overwrite the context building list of the building
        if it already exists
        :return context_building_id_list: list of str: list of the IDs of the buildings that are context for the
            current building
        :return duration: float: duration of the simulation in seconds
        """
        # overwrite context filtering object if needed
        if overwrite:
            self.shading_context_obj.overwrite_filtering(overwrite_first_pass=True)
        # check if the first pass was already done and run it (if it was overwritten, it will be run again)
        if not self.shading_context_obj.first_pass_done:
            # Set the min VF criterion
            self.shading_context_obj.set_mvfc(min_vf_criterion=min_vf_criterion)
            # Convert HB model to LB Polyface3D, keeping only the faces with outdoor boundary condition
            target_lb_polyface3d_of_outdoor_faces = self.shading_context_obj. \
                get_lb_polyface3d_of_outdoor_faces_from_hb_model(hb_model=self.hb_model_obj)

            # Perform the first pass of the context filtering algorithm
            selected_context_building_id_list, duration = self.shading_context_obj. \
                select_context_building_using_the_mvfc(
                target_lb_polyface3d_of_outdoor_faces=target_lb_polyface3d_of_outdoor_faces,
                target_building_id=self.id,
                uc_building_id_list=uc_building_id_list,
                uc_building_bounding_box_list=uc_building_bounding_box_list)

        # Return the list of context buildings
        return selected_context_building_id_list, duration

    def perform_second_pass_context_filtering(self, uc_shade_manager, uc_building_dictionary,
                                              full_urban_canopy_pyvista_mesh, number_of_rays=3, consider_windows=False,
                                              keep_shades_from_user=False, no_ray_tracing=False,
                                              use_merged_face_hb_model=True, overwrite=True,
                                              flag_use_envelop=False):
        """
        Perform the second pass of the context filtering for the shading computation. It selects the context surfaces
        for the shading computation using the ray tracing method.

        """
        # Check if the first pass was done, if not second pass cannot be performed
        if not self.shading_context_obj.first_pass_done:
            dev_logger.info(
                f"The first pass of the context filtering was not done for the building {self.id}, it will be ignored")
            user_logger.info(
                f"The first pass of the context filtering was not done for the building {self.id}, it will be ignored")
            return
            # overwrite context filtering object if needed

        # Check if the context building selected with the first pass have are BuildingModeled, if not send a warning
        if not flag_use_envelop:
            for context_building_id in self.shading_context_obj.selected_context_building_id_list:
                if not isinstance(uc_building_dictionary[context_building_id], BuildingModeled):
                    user_logger.warning(
                        f"At least one context building is not a BuildingModeled, and thus doesn't have a "
                        f"Honeybee Model. Thus, their envelops will be used instead for the context shading computation with"
                        f" default reflective properties, ignoring the windows as the nevelop does not have any")
                    flag_use_envelop = True
                    break

        if overwrite:
            self.shading_context_obj.overwrite_filtering(overwrite_second_pass=True)
        # check if the first pass was already done and run it (if it was overwritten, it will be run again)
        if not self.shading_context_obj.second_pass_done:
            # Set the min VF criterion
            self.shading_context_obj.set_number_of_rays(number_of_rays=number_of_rays, no_ray_tracing=no_ray_tracing)
            self.shading_context_obj.set_consider_windows(consider_windows=consider_windows)
            # Get the list of the HB models or LB Polyface3d of the context buildings
            context_hb_model_or_lb_polyface3d_list_to_test = []
            for building_id in self.shading_context_obj.selected_context_building_id_list:
                building_obj = uc_building_dictionary[building_id]
                if isinstance(building_obj, BuildingModeled):
                    # use the merged faces HB model if it exists, otherwise use the original HB model
                    if building_obj.merged_faces_hb_model_dict is not None and use_merged_face_hb_model:
                        context_hb_model_or_lb_polyface3d_list_to_test.append(
                            Model.from_dict(building_obj.merged_faces_hb_model_dict))
                    else:
                        context_hb_model_or_lb_polyface3d_list_to_test.append(building_obj.hb_model_obj)
                elif isinstance(building_obj, BuildingBasic):
                    context_hb_model_or_lb_polyface3d_list_to_test.append(
                        building_obj.lb_polyface3d_extruded_footprint)
                else:
                    raise ValueError(
                        f"The building {building_obj.id} is not a BuildingModeled or a BuildingBasic, it cannot be "
                        f"handled by the context filter")

            # Perform the first pass of the context filtering algorithm
            nb_context_faces, duration = self.shading_context_obj.select_non_obstructed_context_faces_with_ray_tracing(
                uc_shade_manager=uc_shade_manager,
                target_lb_polyface3d_extruded_footprint=self.lb_polyface3d_extruded_footprint,
                context_hb_model_or_lb_polyface3d_list_to_test=context_hb_model_or_lb_polyface3d_list_to_test,
                full_urban_canopy_pyvista_mesh=full_urban_canopy_pyvista_mesh,
                keep_shades_from_user=keep_shades_from_user, no_ray_tracing=no_ray_tracing)

        # Return the list of context buildings
        return nb_context_faces, duration, flag_use_envelop

    def generate_sensor_grid(self, bipv_on_roof=True, bipv_on_facades=True,
                             roof_grid_size_x=1, facades_grid_size_x=1, roof_grid_size_y=1,
                             facades_grid_size_y=1, offset_dist=0.1, overwrite=False):
        """
        Generate Honeybee SensorGrid on the roof and/or on the facades for the building.
        It does not add the SendorgGrid to the HB model.
        :param bipv_on_roof: Boolean to indicate if the simulation should be done on the roof
        :param bipv_on_facades: Boolean to indicate if the simulation should be done on the facades
        :param roof_grid_size_x: Number for the size of the test grid on the roof in the x direction
        :param facades_grid_size_x: Number for the size of the test grid on the facades in the x direction
        :param roof_grid_size_y: Number for the size of the test grid on the roof in the y direction
        :param facades_grid_size_y: Number for the size of the test grid on the facades in the y direction
        :param offset_dist: Number for the distance to move points from the surfaces of the geometry of the model.
        :param overwrite: Boolean to indicate if the existing SensorGrid should be overwritten
        """
        # Do not generate the SensorGrid if the building is not a target
        if not self.is_target:
            dev_logger.info(f"The building {self.id} is not target, no SensorGrid will be generated."
                            f"Please set the building as target if you want to generate the mesh and perform "
                            f"BIPV simulation ")
            return

        # Use the merged faces HB model if it exists, otherwise use the original HB model
        if self.merged_faces_hb_model_dict is not None:
            hb_model_obj = Model.from_dict(self.merged_faces_hb_model_dict)
        else:
            hb_model_obj = self.hb_model_obj
        # generate the sensor grid
        self.solar_radiation_and_bipv_simulation_obj.generate_sensor_grid(hb_model_obj=hb_model_obj,
                                                                          bipv_on_roof=bipv_on_roof,
                                                                          bipv_on_facades=bipv_on_facades,
                                                                          roof_grid_size_x=roof_grid_size_x,
                                                                          facades_grid_size_x=facades_grid_size_x,
                                                                          roof_grid_size_y=roof_grid_size_y,
                                                                          facades_grid_size_y=facades_grid_size_y,
                                                                          offset_dist=offset_dist,
                                                                          overwrite=overwrite)

    def run_annual_solar_irradiance_simulation(self, path_simulation_folder, path_weather_file, overwrite=False,
                                               north_angle=0, silent=False):
        """
        Run the annual solar radiation simulation for the building on the roof and/or on the facades if a Honeybee SensorGrid
        was generated on them.
        :param path_simulation_folder: Path to the simulation folder
        :param path_weather_file: Path to the epw file
        :param overwrite: bool: default=False, if True, overwrite the simulation files if they already exist
        :param north_angle: float : north angle of the building in degrees
        :param silent: bool: default=False
        """
        #         # check if the solar radiation and BIPV simulation object was initialized
        if self.solar_radiation_and_bipv_simulation_obj.roof_sensorgrid_dict is None and self.solar_radiation_and_bipv_simulation_obj.facades_sensorgrid_dict is None:
            dev_logger.info(
                f"The SenssorGrid of building {self.id} was not generated, it will be ignored")
            user_logger.info(
                f"No mesh was generated on the building {self.id}, please generate one. In the meantime it will be ignored")
            return
        # check if the epw file exists (should be check in the components in Grasshopper as well)
        if not os.path.isfile(path_weather_file):
            dev_logger.info(f"The epw file {path_weather_file} does not exist, the simulation will be ignored")
            user_logger.info(
                f"The building {self.id} was not simulated for the annual solar radiation simulation no mesh for the PVs was generated")
            return
        # check if the building has context
        if self.shading_context_obj is None or self.shading_context_obj.context_shading_hb_shade_list == []:
            dev_logger.info(
                f"The building {self.id} does not have shades. consider running the shading simulation first or add your shades manually")
            user_logger.info(
                f"The building {self.id} does not have shades. consider running the shading simulation first or add your shades manually")

        # Create list of shading surfaces
        hb_shades_list = self.shading_context_obj.context_shading_hb_shade_list + self.shading_context_obj.forced_hb_shades_from_user_list

        # run the annual solar radiation simulation
        self.solar_radiation_and_bipv_simulation_obj.run_annual_solar_irradiance_simulation(
            path_simulation_folder=path_simulation_folder, building_id=self.id, hb_model_obj=self.hb_model_obj,
            context_shading_hb_shade_list=hb_shades_list,
            path_weather_file=path_weather_file, overwrite=overwrite,
            north_angle=north_angle, silent=silent)

    def building_run_bipv_panel_simulation(self, path_simulation_folder, roof_pv_tech_obj, facades_pv_tech_obj,
                                           uc_start_year,
                                           uc_current_year, uc_end_year, efficiency_computation_method="yearly",
                                           minimum_panel_eroi=1.2,
                                           replacement_scenario="replace_failed_panels_every_X_years",
                                           continue_simulation=False, **kwargs):
        """
        Run the BIPV simulation for the building on the roof and/or on the facades of the buildings.
        :param path_simulation_folder: Path to the simulation folder
        :param roof_pv_tech_obj: PVTechnology object: PV technology for the roof
        :param facades_pv_tech_obj: PVTechnology object: PV technology for the facades
        :param uc_start_year: int: start year of the use phase
        :param uc_current_year: int: current year of the use phase
        :param uc_end_year: int: end year of the use phase
        :param efficiency_computation_method: str: default="yearly", method to compute the efficiency of the panels
            during the use phase. Can be "yearly" or "cumulative"
        :param minimum_panel_eroi: float: default=1.2, minimum EROI of the panels to be considered as efficient
        :param replacement_scenario: str: default="replace_failed_panels_every_X_years", scenario for the replacement
            of the panels. Can be "replace_failed_panels_every_X_years" or "replace_all_panels_every_X_years"
        :param continue_simulation: bool: default=False, if True, continue the simulation from the last year
        :param kwargs: dict: other arguments for the simulation
        """

        # Run the simulation
        self.solar_radiation_and_bipv_simulation_obj.run_bipv_panel_simulation(
            path_simulation_folder=path_simulation_folder, building_id=self.id, roof_pv_tech_obj=roof_pv_tech_obj,
            facades_pv_tech_obj=facades_pv_tech_obj, uc_end_year=uc_end_year, uc_start_year=uc_start_year,
            uc_current_year=uc_current_year, efficiency_computation_method=efficiency_computation_method,
            minimum_panel_eroi=minimum_panel_eroi, replacement_scenario=replacement_scenario,
            continue_simulation=continue_simulation, **kwargs)
        # Write the results in a csv file
        self.solar_radiation_and_bipv_simulation_obj.write_bipv_results_to_csv(
            path_simulation_folder=path_simulation_folder,
            building_id=self.id)

    def plot_panels_energy_results(self, path_simulation_folder_building, study_duration_years):
        """
        Todo @Elie, delete this function after making a new version....
        """
        # plot energy
        cum_energy_harvested_roof = get_cumul_values(self.results_panels["roof"]["energy_harvested"]["list"])
        cum_energy_harvested_roof = [i / 1000 for i in cum_energy_harvested_roof]

        cum_primary_energy_roof = add_elements_of_two_lists(
            get_cumul_values(
                self.results_panels["roof"]["lca_cradle_to_installation_primary_energy"]["list"]),
            get_cumul_values(self.results_panels["roof"]["lca_recycling_primary_energy"]["list"]))
        cum_primary_energy_roof = [i / 1000 for i in cum_primary_energy_roof]

        cum_energy_harvested_facades = get_cumul_values(
            self.results_panels["facades"]["energy_harvested"]["list"])
        cum_energy_harvested_facades = [i / 1000 for i in cum_energy_harvested_facades]

        cum_primary_energy_facades = add_elements_of_two_lists(
            get_cumul_values(
                self.results_panels["facades"]["lca_cradle_to_installation_primary_energy"]["list"]),
            get_cumul_values(self.results_panels["facades"]["lca_recycling_primary_energy"]["list"]))
        cum_primary_energy_facades = [i / 1000 for i in cum_primary_energy_facades]

        cum_energy_harvested_total = get_cumul_values(
            self.results_panels["Total"]["energy_harvested"]["list"])
        cum_energy_harvested_total = [i / 1000 for i in cum_energy_harvested_total]

        cum_primary_energy_total = add_elements_of_two_lists(
            get_cumul_values(
                self.results_panels["Total"]["lca_cradle_to_installation_primary_energy"]["list"]),
            get_cumul_values(self.results_panels["Total"]["lca_recycling_primary_energy"]["list"]))
        cum_primary_energy_total = [i / 1000 for i in cum_primary_energy_total]

        years = list(range(study_duration_years))
        fig = plt.figure()
        plt.plot(years, cum_energy_harvested_roof, 'gd', markersize=4,
                 label="Cumulative energy harvested on the roof")
        plt.plot(years, cum_energy_harvested_facades, 'g.',
                 label="Cumulative energy harvested on the facades")
        plt.plot(years, cum_energy_harvested_total, 'g', label="Total cumulative energy harvested")
        plt.plot(years, cum_primary_energy_roof, 'rd', markersize=4, label="Cumulative primary energy, roof")
        plt.plot(years, cum_primary_energy_facades, 'r.', label="Cumulative primary energy, facades")
        plt.plot(years, cum_primary_energy_total, 'r', label="Total cumulative primary energy")

        # get the intersection when energy harvested becomes higher thant primary energy
        slope, intercept = transform_to_linear_function(years, cum_energy_harvested_total)

        def cum_energy_harvested_eq(x):
            return slope * x + intercept

        cum_primary_energy_total_fun = generate_step_function(years, cum_primary_energy_total)

        intersection = find_intersection_functions(cum_energy_harvested_eq, cum_primary_energy_total_fun,
                                                   years[0],
                                                   years[-1])
        plt.axhline(round(intersection[1]), color='k')
        plt.axvline(intersection[0], color='k')
        plt.text(-2, round(intersection[1]), f'y={round(intersection[1])}', va='bottom', ha='left')
        plt.text(round(intersection[0], 1), 0, f'x={round(intersection[0], 1)}', va='bottom', ha='left')

        # get the intersection point when all the energy used has been reimbursed
        asymptote_value = round(cum_primary_energy_total[-1])

        def asymptote_eq(x):
            return asymptote_value

        interp_point = find_intersection_functions(cum_energy_harvested_eq, asymptote_eq, years[0], years[-1])
        plt.axvline(x=round(interp_point[0], 1), color='k')
        plt.text(round(interp_point[0], 1) - 3, -80000, f'x={round(interp_point[0], 1)}', va='bottom',
                 ha='left')
        plt.axhline(asymptote_value, color='k')
        plt.text(round(interp_point[0]), asymptote_value, f'y={asymptote_value}', va='bottom', ha='left')

        plt.xlabel('Time (years)')
        plt.ylabel('Energy (MWh)')
        plt.title('Cumulative harvested energy and primary energy used during the study')
        plt.grid(True)
        plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.2), ncol=2)
        file_name = 'cumulative_energy_harvested_and_primary_energy.pdf'
        fig.savefig(f'{path_simulation_folder_building}/{file_name}', bbox_inches='tight')
        plt.show()

    def plot_panels_ghg_results(self, path_simulation_folder_building, study_duration_years,
                                country_ghe_cost):

        # get the data we need to plot the graphs
        cum_carbon_emissions_roof = add_elements_of_two_lists(
            get_cumul_values(self.results_panels["roof"]["lca_cradle_to_installation_carbon"]["list"]),
            get_cumul_values(self.results_panels["roof"]["lca_recycling_carbon"]["list"]))
        cum_carbon_emissions_roof = [i / 1000 for i in cum_carbon_emissions_roof]

        avoided_carbon_emissions_list_roof = [i * country_ghe_cost for i in self.results_panels["roof"][
            "energy_harvested"]["list"]]
        avoided_carbon_emissions_list_roof = [i / 1000 for i in avoided_carbon_emissions_list_roof]

        cum_avoided_carbon_emissions_roof = get_cumul_values(avoided_carbon_emissions_list_roof)

        cum_carbon_emissions_facades = add_elements_of_two_lists(
            get_cumul_values(self.results_panels["facades"]["lca_cradle_to_installation_carbon"]["list"]),
            get_cumul_values(self.results_panels["facades"]["lca_recycling_carbon"]["list"]))
        cum_carbon_emissions_facades = [i / 1000 for i in cum_carbon_emissions_facades]

        avoided_carbon_emissions_list_facades = [i * country_ghe_cost for i in self.results_panels["facades"][
            "energy_harvested"]["list"]]
        avoided_carbon_emissions_list_facades = [i / 1000 for i in avoided_carbon_emissions_list_facades]

        cum_avoided_carbon_emissions_facades = get_cumul_values(avoided_carbon_emissions_list_facades)

        cum_carbon_emissions_total = add_elements_of_two_lists(
            get_cumul_values(self.results_panels["Total"]["lca_cradle_to_installation_carbon"]["list"]),
            get_cumul_values(self.results_panels["Total"]["lca_recycling_carbon"]["list"]))
        cum_carbon_emissions_total = [i / 1000 for i in cum_carbon_emissions_total]

        avoided_carbon_emissions_list_total = [i * country_ghe_cost for i in self.results_panels["Total"][
            "energy_harvested"]["list"]]
        avoided_carbon_emissions_list_total = [i / 1000 for i in avoided_carbon_emissions_list_total]

        cum_avoided_carbon_emissions_total = get_cumul_values(avoided_carbon_emissions_list_total)

        # plot the data
        years = list(range(study_duration_years))
        fig = plt.figure(figsize=(8, 6))
        plt.plot(years, cum_avoided_carbon_emissions_roof, 'gd', markersize=4,
                 label="Cumulative avoided GHG emissions, roof")
        plt.plot(years, cum_avoided_carbon_emissions_facades, 'go', markersize=4,
                 label="Cumulative avoided GHG emissions, facades")
        plt.plot(years, cum_avoided_carbon_emissions_total, 'g',
                 label="Total cumulative avoided GHG emissions")
        plt.plot(years, cum_carbon_emissions_roof, 'rd', markersize=4,
                 label="Cumulative GHG emissions, roof")
        plt.plot(years, cum_carbon_emissions_facades, 'ro', markersize=4,
                 label="Cumulative GHG emissions, facades")
        plt.plot(years, cum_carbon_emissions_total, 'r',
                 label="Total cumulative GHG emissions")

        slope, intercept = transform_to_linear_function(years, cum_avoided_carbon_emissions_total)

        def cum_avoided_carbon_emissions_eq(x):
            return slope * x + intercept

        # get the intersection point when all the energy used has been reimbursed
        asymptote_value = round(cum_carbon_emissions_total[-1])

        def asymptote_eq(x):
            return asymptote_value

        interp_point = find_intersection_functions(cum_avoided_carbon_emissions_eq, asymptote_eq, years[0],
                                                   years[-1])
        plt.axvline(x=round(interp_point[0], 1), color='k')
        plt.text(round(interp_point[0], 1) - 2, -60000, f'x={round(interp_point[0], 1)}', va='bottom',
                 ha='left')
        plt.axhline(asymptote_value, color='k')
        plt.text(round(interp_point[0]) - 6, asymptote_value, f'y={asymptote_value}', va='bottom', ha='left')

        plt.xlabel('Time (years)')
        plt.ylabel('GHE emissions (tCO2eq)')
        plt.title('Cumulative GHG emissions during the study ')
        plt.grid(True)
        plt.subplots_adjust(bottom=0.5)
        plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.2), ncol=2)
        file_name = 'cumulative_ghg_emissions.pdf'
        fig.savefig(f'{path_simulation_folder_building}/{file_name}', bbox_inches='tight')
        plt.show()

    def plot_panels_results_ghe_per_kwh(self, path_simulation_folder_building, study_duration_years):
        # plot price in GHG emissions by kWh harvested

        cum_energy_harvested_total = get_cumul_values(
            self.results_panels["Total"]["energy_harvested"]["list"])
        cum_carbon_emissions_total = add_elements_of_two_lists(
            get_cumul_values(self.results_panels["Total"]["lca_cradle_to_installation_carbon"]["list"]),
            get_cumul_values(self.results_panels["Total"]["lca_recycling_carbon"]["list"]))

        ghg_per_kWh = [(x / y) * 1000 for x, y in zip(cum_carbon_emissions_total, cum_energy_harvested_total)]

        years = list(range(study_duration_years))
        fig = plt.figure()
        plt.plot(years, ghg_per_kWh)
        plt.xlabel('Time (years)')
        plt.ylabel('GHE emissions (gCO2eq/kWh)')
        plt.title("Evolution of the cost in GHG emissions for each kWh harvested during the study")
        plt.grid(True)
        file_name = 'ghg_per_kWh_plot.pdf'
        fig.savefig(f'{path_simulation_folder_building}/{file_name}', bbox_inches='tight')

    def plot_panels_results_eroi(self, path_simulation_folder_building, study_duration_years):
        # plot EROI
        cum_primary_energy_total = add_elements_of_two_lists(
            get_cumul_values(
                self.results_panels["Total"]["lca_cradle_to_installation_primary_energy"]["list"]),
            get_cumul_values(self.results_panels["Total"]["lca_recycling_primary_energy"]["list"]))
        cum_energy_harvested_total = get_cumul_values(
            self.results_panels["Total"]["energy_harvested"]["list"])
        eroi = [x / y for x, y in zip(cum_energy_harvested_total, cum_primary_energy_total)]

        years = list(range(study_duration_years))
        fig = plt.figure()
        plt.plot(years, eroi)
        plt.xlabel('Time (years)')
        plt.ylabel('EROI')
        plt.title("Evolution of the EROI during the study")
        plt.grid(True)
        file_name = 'eroi.pdf'
        fig.savefig(f'{path_simulation_folder_building}/{file_name}', bbox_inches='tight')
