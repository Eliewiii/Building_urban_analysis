"""
BuildingModeled class, representing one building in an urban canopy that will be converted in HB models
as they will be simulated
"""
import os.path

from building.utils_building import *
from building.building_basic import \
    BuildingBasic  # todo: cannot be imported from building.utils because of circular import (building.building_basic import utils)

from libraries_addons.solar_radiations.add_sensorgrid_hb_model import *
from libraries_addons.solar_radiations.hb_recipe_settings import hb_recipe_settings
from libraries_addons.solar_radiations.annual_irradiance_simulation import hb_ann_irr_sim
from libraries_addons.solar_radiations.annual_cumulative_value import hb_ann_cum_values

from solar_panel.pv_panel_technology import PanelTechnology
from solar_panel.pv_panel import Panel

from libraries_addons.solar_panels.useful_functions_solar_panel import load_panels_on_sensor_grid, \
    loop_over_the_years_for_solar_panels
from libraries_addons.solar_panels import pv_efficiency_functions
from libraries_addons.solar_panels import pv_efficiency_functions


class BuildingModeled(BuildingBasic):
    """BuildingBasic class, representing one building in an urban canopy."""

    # todo :make the LB_face_footprint optional in the BuildingBasic class
    def __init__(self, identifier, LB_face_footprint=None, urban_canopy=None, building_index_in_GIS=None, **kwargs):
        # Initialize with the inherited attributes from the BuildingBasic parent class
        super().__init__(identifier, LB_face_footprint, urban_canopy, building_index_in_GIS)
        # get the values from the original BuildingBasic object (if there is one) through **kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)

        self.HB_model_obj = None
        self.HB_model_dict = None
        self.sensor_grid_dict = {'Roof': None, 'Facades': None}
        self.panels = {"Roof": None, "Facade": None}
        self.to_simulate = False
        self.is_target = False

    def load_HB_attributes(self):
        """
        Load the attributes that cannot be pickled from equivalent attribute dict.
        """
        # Convert the HB_model_dict to HB_model_obj
        self.HB_model_obj = Model.from_dict(self.HB_model_dict)  # todo: test if it works
        self.HB_model_dict = None

    def pickle_HB_attributes(self):
        """
        Convert the HB_model_obj to HB_model_dict to be able to pickle it.
        """
        # Convert the HB_model_obj to HB_model_dict
        self.HB_model_dict = self.HB_model_obj.to_dict()  # todo: test if it works
        self.HB_model_obj = None
        # todo : maybe add more properties to modify before pickling to avoid locked class issue

    @classmethod
    def convert_buildingbasic_to_buildingmodeled(cls, building_obj, layout_from_typology=False,
                                                 automatic_subdivision=True,
                                                 properties_from_typology=True):
        """
        Create a BuildingModeled object from a BuildingBasic object
        :return: building_HB_model : BuildingModeled object
        """
        # Make the HB model from the building object
        # todo @Sharon : how to try to make the model ? and if it work we go further ? otherwise we return None ?
        HB_model = building_obj.to_HB_model(layout_from_typology=layout_from_typology,
                                            automatic_subdivision=automatic_subdivision,
                                            properties_from_typology=properties_from_typology)
        # get the attributes of the building_obj (it extract all attributes, even the ones that are used
        # to create the object), but it doesn't matter, it is just a bit redundant
        kwargs = {attr: getattr(building_obj, attr) for attr in dir(building_obj) if not attr.startswith('__')}
        # create the BuildingModeled object from the BuildingBasic object
        building_HB_model = cls(building_obj.id, building_obj.LB_face_footprint, building_obj.urban_canopy,
                                building_obj.index_in_GIS, **kwargs)
        # todo : @Sharon, check if the code is correct to create object from super class, should it be that way or though a to_buildingHBmodel function in the BuildingBasic class?

        return building_HB_model
        # todo : change if needed where the dictionary of the urban canopy is pointing, to point to the new object

    @classmethod
    def make_buildingmodeled_from_hbjson(cls, path_hbjson, is_target=False, urban_canopy=None):
        """
        Create a BuildingModeled object from a HBJSON file
        :return: building_HB_model : BuildingModeled object
        """
        # Load the HB model from the hbjson file
        HB_model = Model.from_hbjson(path_hbjson)
        # get the identifier the
        identifier = HB_model.identifier
        # create the BuildingModeled object from the HB model
        building_modeled_obj = cls(identifier)
        # Try to extract certain characteristics of the model from the HB_model
        elevation, height = HbAddons.elevation_and_height_from_HB_model(HB_model)
        # # set the attributes of the BuildingModeled object
        building_modeled_obj.HB_model_obj = HB_model
        building_modeled_obj.urban_canopy = urban_canopy
        building_modeled_obj.elevation = elevation
        building_modeled_obj.height = height
        building_modeled_obj.is_target = is_target
        # todo @Elie : make the LB_face_footprint from the HB_model
        building_modeled_obj.LB_face_footprint = HbAddons.make_LB_face_footprint_from_HB_model(HB_model=HB_model)
        # todo @Elie : finish the function (and check if it works)
        building_modeled_obj.moved_to_origin = True  # we assumed that the HB model is already in the proper place within the urban canopy

        return building_modeled_obj, identifier

    def select_context_surfaces_for_shading_computation(self, context_building_list, full_urban_canopy_Pyvista_mesh,
                                                        minimum_vf_criterion):
        """ Select the context surfaces that will be used for the shading simulation of the current building.
        :param context_building_list: list of BuildingModeled objects
        :param minimum_vf_criterion: minimum view factor between surfaces to be considered as context surfaces
        in the first pass of the algorithm
        """
        # todo @ Elie: finish the function
        # Initialize variables
        list_building_kept_first_pass = []
        HB_Face_surfaces_kept_second_pass = []
        # First pass
        for context_building_obj in context_building_list:
            if context_building_obj.id != self.id:  # does not take itself into account
                if is_bounding_box_context_using_mvfc_criterion(
                        target_LB_polyface3d_extruded_footprint=self.LB_polyface3d_extruded_footprint,
                        context_LB_polyface3d_oriented_bounding_box=context_building_obj.LB_polyface3d_oriented_bounding_box,
                        minimum_vf_criterion=minimum_vf_criterion):
                    None
                    # todo @Elie : add the buoiliding to the list of building kept in the first pass
                    # add the building to the list of building for the second path

                    # convert the buildingbasics into buildingmodeled (with typo identifier when it will work, put an empty function for now
                    # use the honeybee model to have the proper caracteristics of the surfsace

        # Second pass

        # for context_building_obj in list_building_kept_first_pass:
        #      for HB_face_surface in context_building_obj.HB_model_obj:
        #          if not is_HB_Face_context_surface_obstructed_for_target_LB_polyface3d(target_LB_polyface3d_extruded_footprint=self.LB_polyface3d_extruded_footprint , context_HB_Face_surface=HB_face_surface):
        #              None
        #             #todo

    def move(self, vector):
        """
        Move the building
        :param vector:
        :return:
        """
        # move the LB footprint
        if self.LB_face_footprint is not None:
            self.LB_face_footprint = self.LB_face_footprint.move(
                Vector3D(vector[0], vector[1], 0))  # the footprint is moved only in the x and y directions
        # adjust the elevation
        if self.elevation is not None:
            self.elevation = self.elevation + vector[2]
        # make it moved
        self.HB_model_obj.move(Vector3D(vector[0], vector[1], vector[2]))  # the model is moved fully
        self.moved_to_origin = True

    def add_sensor_grid_to_hb_model(self, name=None, grid_size=1, offset_dist=0.1, on_roof=True, on_facades=True):
        """Create a HoneyBee SensorGrid from a HoneyBe model for the roof, the facades or both and add it to the
        model"""
        """Args :
        name : Name 
        grid_size : Number for the size of the test grid
        offset_dist : Number for the distance to move points from the surfaces of the geometry of the model. Typically, this
        should be a small positive number to ensure points are not blocked by the mesh.
        name : Name """

        assert isinstance(self.HB_model_obj, Model), \
            'Expected Honeybee Model. Got {}.'.format(type(self.HB_model_obj))

        if on_roof and on_facades:
            faces_roof = get_hb_faces_roof(self.HB_model_obj)
            mesh_roof = get_lb_mesh(faces_roof, grid_size, offset_dist)
            sensor_grid_roof = create_sensor_grid_from_mesh(mesh_roof, name)
            self.sensor_grid_dict['Roof'] = sensor_grid_roof.to_dict()

            faces_facades = get_hb_faces_facades(self.HB_model_obj)
            mesh_facades = get_lb_mesh(faces_facades, grid_size, offset_dist)
            sensor_grid_facades = create_sensor_grid_from_mesh(mesh_facades, name)
            self.sensor_grid_dict['Facades'] = sensor_grid_facades.to_dict()

        elif on_roof and not on_facades:
            faces_roof = get_hb_faces_roof(self.HB_model_obj)
            mesh_roof = get_lb_mesh(faces_roof, grid_size, offset_dist)
            sensor_grid_roof = create_sensor_grid_from_mesh(mesh_roof, name)
            self.sensor_grid_dict['Roof'] = sensor_grid_roof.to_dict()

        elif on_facades and not on_roof:
            faces_facades = get_hb_faces_facades(self.HB_model_obj)
            mesh_facades = get_lb_mesh(faces_facades, grid_size, offset_dist)
            sensor_grid_facades = create_sensor_grid_from_mesh(mesh_facades, name)
            self.sensor_grid_dict['Facades'] = sensor_grid_facades.to_dict()

        else:
            logging.warning(f"You did not precise whether you want to run the simulation on the roof, "
                            f"the facades or both")

    def solar_radiations(self, name, path_folder_simulation, path_weather_file, grid_size=1, offset_dist=0.1,
                         on_roof=True, on_facades=True):
        """Create and add a sensor grid to the HB model of the building then run the annual irradiance simulation on
        it"""

        # Add the sensor grids to the building modeled
        self.add_sensor_grid_to_hb_model(name, grid_size, offset_dist, on_roof, on_facades)

        if on_roof and not on_facades:
            # generate the sensor grid from the dict
            sensor_grid_roof = SensorGrid.from_dict(self.sensor_grid_dict['Roof'])
            # duplicate the model so that no changes will be made on the original model
            model_sensor_grid_roof = self.HB_model_obj.duplicate()
            if len(sensor_grid_roof) != 0:
                # add the sensor grid to the hb model duplicate
                model_sensor_grid_roof.properties.radiance.add_sensor_grid(sensor_grid_roof)
                # run the solar radiation simulation on the roof
                path_folder_simulation_roof = os.path.join(path_folder_simulation, "Roof")
                settings = hb_recipe_settings(path_folder_simulation_roof)
                project_folder = hb_ann_irr_sim(model_sensor_grid_roof, path_weather_file, settings)
            return hb_ann_cum_values([os.path.join(project_folder, "annual_irradiance", "results", "total")])

        elif on_facades and not on_roof:
            # generate the sensor grid from the dict
            sensor_grid_facades = SensorGrid.from_dict(self.sensor_grid_dict['Facades'])
            # duplicate the model so that no changes will be made on the original model
            model_sensor_grid_facades = self.HB_model_obj.duplicate()
            if len(sensor_grid_facades) != 0:
                # add the sensor grid to the hb model duplicate
                model_sensor_grid_facades.properties.radiance.add_sensor_grid(sensor_grid_facades)
                # run the solar radiation simulation on the roof
                path_folder_simulation_facades = os.path.join(path_folder_simulation, "Facades")
                settings = hb_recipe_settings(path_folder_simulation_facades)
                project_folder = hb_ann_irr_sim(model_sensor_grid_facades, path_weather_file, settings)
            return hb_ann_cum_values([os.path.join(project_folder, "annual_irradiance", "results", "total")])

    def load_panels_roof(self, pv_tech_roof):
        """
        Load the panels to the mesh of the roof.
        :param pv_tech_roof: PVPanelTechnology objectT
        """
        # we only add the panels if the sensor grid already exists
        if self.sensor_grid_dict["Roof"] is not None:
            # get the sensor grid then load the panels
            sensor_grid_roof = SensorGrid.from_dict(self.sensor_grid_dict["Roof"])
            panels_roof = load_panels_on_sensor_grid(sensor_grid_roof, pv_tech_roof)
            self.panels["Roof"] = panels_roof
        else:
            pass

    def load_panels_facades(self, pv_tech_facades):
        """
        Load the panels to the mesh of the facades.
        :param pv_tech_facades: PVPanelTechnology objectT
        """
        # we only add the panels if the sensor grid already exist
        if self.sensor_grid_dict["Facades"] is not None:
            # get the sensor grid then the mesh from the dictionary
            sensor_grid_facades = SensorGrid.from_dict(self.sensor_grid_dict["Facades"])
            panels_facades = load_panels_on_sensor_grid(sensor_grid_facades, pv_tech_facades)
            self.panels["Facades"] = panels_facades
        else:
            pass

    def panels_simulation_roof(self, path_folder_simulation_building, pv_technologies_dictionary,
                               study_duration_in_years=50, id_pv_tech="mitrex_roof c-Si",
                               replacement_scenario="yearly", **kwargs):
        pv_technology = pv_technologies_dictionary[id_pv_tech]
        self.load_panels_roof(pv_technology)
        if self.panels["Roofs"] is not None:
            path_folder_roof_values_path = os.path.join(path_folder_simulation_building, "Roof",
                                                        "annual_irradiance_values.txt")
            with open(path_folder_roof_values_path, "r") as f:
                data_values = f.read()
                data_values_in_string = data_values.split(",")
                radiation_values_in_list = list(map(float, data_values_in_string))
            energy_production_per_year_list_roof, lca_energy_used_per_year_list_roof, \
                dmfa_waste_generated_per_year_list_roof = loop_over_the_years_for_solar_panels(
                self.panels["Roof"], radiation_values_in_list, study_duration_in_years, replacement_scenario, **kwargs)
            return energy_production_per_year_list_roof, lca_energy_used_per_year_list_roof, \
                dmfa_waste_generated_per_year_list_roof

    def panels_simulation_facades(self, path_folder_simulation_building, pv_technologies_dictionary,
                                  study_duration_in_years=50, id_pv_tech="metsolar_facades c-Si",
                                  replacement_scenario="yearly", **kwargs):
        pv_technology = pv_technologies_dictionary[id_pv_tech]
        self.load_panels_facades(pv_technology)
        if self.panels["Facades"] is not None:
            path_folder_facades_values_path = os.path.join(path_folder_simulation_building, "Facades",
                                                           "annual_irradiance_values.txt")
            with open(path_folder_facades_values_path, "r") as f:
                data_values = f.read()
                data_values_in_string = data_values.split(",")
                radiation_values_in_list = list(map(float, data_values_in_string))
            energy_production_per_year_list_facades, lca_energy_used_per_year_list_facades, \
                dmfa_waste_generated_per_year_list_facades = loop_over_the_years_for_solar_panels(
                self.panels["Facades"], radiation_values_in_list, study_duration_in_years, replacement_scenario,
                **kwargs)
            return energy_production_per_year_list_facades, lca_energy_used_per_year_list_facades, \
                dmfa_waste_generated_per_year_list_facades

    def panel_simulation_building(self, path_folder_simulation_building, pv_technologies_dictionary,
                                  study_duration_in_years=50, id_pv_tech_roof="mitrex_roof c-Si",
                                  id_pv_tech_facades="metsolar_facades c-Si",
                                  replacement_scenario="yearly", **kwargs):
        roof_results = self.panels_simulation_roof(path_folder_simulation_building, pv_technologies_dictionary,
                                                   study_duration_in_years, id_pv_tech_roof, replacement_scenario,
                                                   **kwargs)
        facades_results = self.panels_simulation_facades(path_folder_simulation_building, pv_technologies_dictionary,
                                                         study_duration_in_years, id_pv_tech_facades,
                                                         replacement_scenario, **kwargs)
        total_results = [roof_results, facades_results, roof_results+facades_results]
        return total_results
