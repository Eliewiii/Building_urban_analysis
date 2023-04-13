"""
Additional methods for the Building class.
Deals with the context selection of the context.
"""
import copy
import time
import logging
import numpy as np

import pyvista as pv

from math import sqrt, atan, pi, log
from copy import deepcopy

from ladybug_geometry.geometry3d import Vector3D, Point3D, Face3D

from honeybee.model import Model
from honeybee.face import Face
from honeybee.shade import Shade

from ladybug_geometry.bounding import bounding_domain_x, bounding_domain_y, bounding_rectangle_extents, _orient_geometry


# from building_ubem._footprin_and_envelop_manipulation import extrude_lb_face_to_hb_room


class Mixin:

    def prepare_bounding_box_face_list(self):
        """
        Returns a a list that will be used for the context selection.
        return a list as followed:
        [  [face_obj, area, centroid], [], .... ]
        order from the smallest area to the biggest
        if reverse==True, it is sorted reverse

        """
        face_list = []  # list to return
        z_vertices = [Vector3D(0, 0, 1), Vector3D(0, 0, -1)]  # vertical vertices
        for face in self.hb_oriented_bounding_box:
            if face.normal not in z_vertices:  # do not keep the roof and ground
                face_list.append(
                    {"hb_face_obj": face, "area": face.geometry.area, "centroid_point3d": face.geometry.centroid})
            # sort the list according to the 2nd element = the area, from bigger to smaller for context building
            face_list.sort(key=lambda x: x["area"], reverse=True)
            self.bounding_box_face_list = deepcopy(face_list)

    def prepare_face_for_context(self, reverse=False):
        """
        Returns a a list that will be used for the context selection.
        return a list as followed:
        [  [face_obj, area, centroid], [], .... ]
        order from the smallest area to the biggest
        if reverse==True, it is sorted reverse

        """
        face_list = []  # list to return
        z_vertices = [Vector3D(0, 0, 1), Vector3D(0, 0, -1)]  # vertical vertices
        for face in self.HB_room_envelop.faces:
            if face.normal not in z_vertices:  # do not keep the roof and ground
                face_list.append([face, face.geometry.area, face.geometry.centroid])

        face_list.sort(key=lambda x: x[1], reverse=reverse)  # sort the list according to the 2nd element = the area
        return face_list

    def prepare_face_for_context_new(self, is_target=False):
        """
        Returns a a list that will be used for the context selection.
        return a list as followed:
        [  [face_obj, area, centroid], [], .... ]
        order from the smallest area to the biggest
        if reverse==True, it is sorted reverse

        """
        face_list = []  # list to return
        z_vertices = [Vector3D(0, 0, 1), Vector3D(0, 0, -1)]  # vertical vertices
        for face in self.HB_room_envelop.faces:
            if face.normal not in z_vertices:  # do not keep the roof and ground
                lower_corners = [point3d_to_numpy_array(face.geometry.lower_left_corner),
                                 point3d_to_numpy_array(face.geometry.lower_right_corner)]
                lower_corners = adjust_lower_corners(pt_left=lower_corners[0], pt_right=lower_corners[1])
                face_list.append(
                    {"hb_face_obj": face, "area": face.geometry.area, "centroid_point3d": face.geometry.centroid,
                     "lower_corner_points": {"left": lower_corners[0], "right": lower_corners[1],
                                             "center": (lower_corners[0] + lower_corners[1]) / 2.},
                     "height": self.height, "elevation": self.elevation})
            if is_target:
                face_list.sort(key=lambda x: x["area"],
                               reverse=False)  # sort the list according to the 2nd element = the area
                # from smaller to bigger for context building
                self.external_face_list_target = list(face_list)

            face_list.sort(key=lambda x: x["area"],
                           reverse=True)  # sort the list according to the 2nd element = the area
            # from bigger to smaller for context building
            self.external_face_list_context = deepcopy(face_list)

    def shading_context_bb_surfaces_selection(self, pre_processed_bb_building_surface_dict, mvfc=0.01, first_pass=True,
                                              second_pass=True, keep_all_context=True, keep_first_pass=True, keep_bb=True):
        """
        Select the surfaces from all the context that shade noticeably on the building.
        The filtering has 2 passes:
        - the minimum view factor criterion
        - obstruction detection with LCA
        It can go through only one or none of the passes if needed

        Args:
            pre_processed_surface_list [list]: list containing all the surfaces to test. Each element, representing a
                surface, is a dictionary with the following properties {"hb_face_obj", "area", "centroid":(Point3D),
                 "lower_corner_point3d":{"left","right"},"height"}
            mvfc [float]: value for the minimum view factor criteria. Check the shading_context_first_pass function
               for the detailed explanation. default value 0.01
            first_pass [boolean]: True if we want to use the first pass, False if not.
            second_pass [boolean]: True if we want to use the second pass, False if not.
        """
        logging.warning(f" building_{self.id} : start context filering")
        building_surfaces_dict_to_test = copy.deepcopy(pre_processed_bb_building_surface_dict)

        ## Initialization
        first_pass_duration = 0
        second_pass_duration = 0
        kept_surfaces_dict_list = []

        # kept_building_first_pass = []
        kept_surface_first_pass = []
        kept_surface_second_pass = []

        ## first pass
        if first_pass:
            first_pass_duration = time.time()
            kept_building_first_pass = self.shading_context_bb_first_pass(building_surfaces_dict_to_test, mvfc)
            first_pass_duration = time.time() - first_pass_duration
            logging.warning(f" building_{self.id} :  first pass duration :{round(first_pass_duration, 4)}s")
            # conversion into surface dict list
            kept_surfaces_dict_list = context_building_to_surface_kept(building_surfaces_dict_to_test,
                                                                       kept_building_first_pass)
            # conversion into HB surface list for EnergyPlus and plotting purposes
            kept_surface_first_pass = surface_dict_to_hb_faces(kept_surfaces_dict_list)
            if keep_first_pass:
                self.context_hb_kept_first_pass = list(kept_surface_first_pass)  # no deepcopy ! otherwise cannot
                # remove the surfaces from the second pass, the objects are not the same anymore
            # Save the context surfaces that were not kept by the first pass, to represent the rest of the context in Rhino
            if keep_all_context:
                all_context_surface_dict_list = context_building_to_surface_kept(building_surfaces_dict_to_test,
                                                                                 "all",building_not_to_keep=[self.id])
                all_context_hb_faces = surface_dict_to_hb_faces(all_context_surface_dict_list)
                # keep only the surfaces not kept by the first pass (so that they don't overlap)
                for face in all_context_hb_faces:
                    if face not in kept_surface_first_pass:
                        self.all_context_hb_faces.append(face)
                self.all_context_hb_faces = deepcopy(self.all_context_hb_faces)

            if keep_bb:
                all_context_surface_bb_dict_list = context_building_to_bb_kept(building_surfaces_dict_to_test,building_not_to_keep=[self.id])
                self.all_context_oriented_bb = surface_dict_to_hb_faces(all_context_surface_bb_dict_list)

            ## second pass
            if second_pass:
                second_pass_duration = time.time()
                kept_surfaces_dict_list = self.shading_context_second_pass(kept_surfaces_dict_list)
                second_pass_duration = time.time() - second_pass_duration
                logging.warning(f" building_{self.id} :  second pass duration :{round(second_pass_duration, 4)}s")

                kept_surface_second_pass = surface_dict_to_hb_faces(kept_surfaces_dict_list)
                # remove the surface kept in the second pass from the first pass
                if keep_first_pass:
                    for face in kept_surface_first_pass:
                        if face in kept_surface_second_pass:
                            self.context_hb_kept_first_pass.remove(face)
        ## second pass only
        elif second_pass:
            # convert the dictionary of building to a list of surfaces for the second pass only
            all_context_surface_dict_list = context_building_to_surface_kept(building_surfaces_dict_to_test,
                                                                             "all")
            second_pass_duration = time.time()
            kept_surfaces_dict_list = self.shading_context_second_pass(all_context_surface_dict_list)
            second_pass_duration = time.time() - second_pass_duration
            logging.warning(f" building_{self.id} :  second pass duration :{round(second_pass_duration, 4)}s")
            kept_surface_second_pass = surface_dict_to_hb_faces(kept_surfaces_dict_list)
            if keep_all_context:
                all_context_hb_faces = surface_dict_to_hb_faces(all_context_surface_dict_list)
                for face in all_context_hb_faces:
                    if face not in kept_surface_second_pass:
                        self.all_context_hb_faces.append(face)
                self.all_context_hb_faces = deepcopy(self.all_context_hb_faces)

        hb_context_faces = surface_dict_to_hb_faces(kept_surfaces_dict_list)

        self.context_shading_HB_faces = deepcopy(hb_context_faces)

        return (kept_surface_first_pass, kept_surface_second_pass, first_pass_duration, second_pass_duration)

    def shading_context_surfaces_selection(self, pre_processed_surface_list, mvfc=0.01, first_pass=True,
                                           second_pass=True, keep_all_context=True, keep_first_pass=True):
        """
        Select the surfaces from all the context that shade noticeably on the building.
        The filtering has 2 passes:
        - the minimum view factor criterion
        - obstruction detection with LCA
        It can go through only one or none of the passes if needed

        Args:
            pre_processed_surface_list [list]: list containing all the surfaces to test. Each element, representing a
                surface, is a dictionary with the following properties {"hb_face_obj", "area", "centroid":(Point3D),
                 "lower_corner_point3d":{"left","right"},"height"}
            mvfc [float]: value for the minimum view factor criteria. Check the shading_context_first_pass function
               for the detailed explanation. default value 0.01
            first_pass [boolean]: True if we want to use the first pass, False if not.
            second_pass [boolean]: True if we want to use the second pass, False if not.
        """
        logging.warning(f" building_{self.id} : start context filering")
        surface_to_test = copy.deepcopy(pre_processed_surface_list)

        ## Initialization
        first_pass_duration = 0
        second_pass_duration = 0
        kept_surfaces_dict_list = []

        kept_surface_first_pass = []
        kept_surface_second_pass = []

        ## first pass
        if first_pass:
            first_pass_duration = time.time()
            kept_surfaces_dict_list = self.shading_context_first_pass(surface_to_test, mvfc)
            first_pass_duration = time.time() - first_pass_duration
            logging.warning(f" building_{self.id} :  first pass duration :{round(first_pass_duration, 4)}s")
            kept_surface_first_pass = surface_dict_to_hb_faces(kept_surfaces_dict_list)
            if keep_first_pass:
                self.context_hb_kept_first_pass = list(kept_surface_first_pass)
            #
            if keep_all_context:
                all_context_hb_faces = surface_dict_to_hb_faces(surface_to_test)
                for face in all_context_hb_faces:
                    if face not in kept_surface_first_pass:
                        self.all_context_hb_faces.append(face)
                self.all_context_hb_faces = deepcopy(self.all_context_hb_faces)

            ## second pass
            if second_pass:
                second_pass_duration = time.time()
                kept_surfaces_dict_list = self.shading_context_second_pass(kept_surfaces_dict_list)
                second_pass_duration = time.time() - second_pass_duration
                logging.warning(f" building_{self.id} :  second pass duration :{round(second_pass_duration, 4)}s")

                kept_surface_second_pass = surface_dict_to_hb_faces(kept_surfaces_dict_list)
                # remove the surface kept in the second pass from the first pass
                if keep_first_pass:
                    for face in kept_surface_first_pass:
                        if face in kept_surface_second_pass:
                            self.context_hb_kept_first_pass.remove(face)

        ## second pass only
        elif second_pass:
            second_pass_duration = time.time()
            kept_surfaces_dict_list = self.shading_context_second_pass(surface_to_test)
            second_pass_duration = time.time() - second_pass_duration
            logging.warning(f" building_{self.id} :  second pass duration :{round(second_pass_duration, 4)}s")
            kept_surface_second_pass = surface_dict_to_hb_faces(kept_surfaces_dict_list)

        hb_context_faces = surface_dict_to_hb_faces(kept_surfaces_dict_list)

        self.context_shading_HB_faces = deepcopy(hb_context_faces)

        return (kept_surface_first_pass, kept_surface_second_pass, first_pass_duration, second_pass_duration)

    def shading_context_first_pass(self, pre_processed_surface_list, mvfc):
        """
        First pass of the selection of the shading surfaces from the context.
        Use the minimum view factor criterion (mvfc).
        An upper bound of the view factor between each couple of target and context surfaces is computed. If this value
        is higher than the mvfc, the surface is kept as it has potential to shade significantly on the target building.
        If it is lower, the context surface is not keep for the second pass (and thus the energy simulation)
        Args:
            pre_processed_surface_list [list]: list containing all the surfaces to test. Each element, representing a
                surface, is a dictionary with the following properties {"hb_face_obj", "area", "centroid":(Point3D),
                 "lower_corner_point3d":{"left","right"},"height"}
            mvfc [float]: value for the minimum view factor criteria.
        """
        kept_surfaces = []  # surfaces to keep after the first pass
        for test_face in pre_processed_surface_list:  # loop over all the context surfaces
            for target_face in self.external_face_list_target:  # loop over all the surfaces of the target building
                if max_VF(centroid_1=target_face["centroid_point3d"], area_1=target_face["area"],
                          centroid_2=test_face["centroid_point3d"], area_2=test_face["area"]) >= mvfc:  # mvf criterion
                    kept_surfaces.append(test_face)  # if criteria valid, add the surface to the kept surface
                    break  # if a surface is context for one of the target surface, it is kept and thus stop the loop

        return kept_surfaces

    def shading_context_bb_first_pass(self, pre_processed_bb_building_surface_dict, mvfc):
        """
        First pass of the selection of the shading surfaces from the context.
        Use the minimum view factor criterion (mvfc).
        An upper bound of the view factor between each couple of target and context surfaces is computed. If this value
        is higher than the mvfc, the surface is kept as it has potential to shade significantly on the target building.
        If it is lower, the context surface is not keep for the second pass (and thus the energy simulation)
        Args:
            pre_processed_surface_list [list]: list containing all the surfaces to test. Each element, representing a
                surface, is a dictionary with the following properties {"hb_face_obj", "area", "centroid":(Point3D),
                 "lower_corner_point3d":{"left","right"},"height"}
            mvfc [float]: value for the minimum view factor criteria.
        """
        kept_building = []  # surfaces to keep after the first pass
        for building_id in list(pre_processed_bb_building_surface_dict.keys()):
            if building_id != self.id:
                is_context = False
                for test_face in pre_processed_bb_building_surface_dict[building_id][
                    "bounding_box_faces"]:  # loop over all the context surfaces
                    for target_face in self.external_face_list_target:  # loop over all the surfaces of the target building
                        if max_VF(centroid_1=target_face["centroid_point3d"], area_1=target_face["area"],
                                  centroid_2=test_face["centroid_point3d"],
                                  area_2=test_face["area"]) >= mvfc:  # mvf criterion
                            kept_building.append(building_id)  # if criteria valid, add the surface to the kept surface
                            is_context = True  # if the mvfc is verified, the building is kept
                            break  # if a surface is context for one of the target surface, it is kept and thus stop the loop
                    if is_context == True:
                        # if the building is kept, no need to test the other surfaces
                        break
        return kept_building

    def shading_context_second_pass(self, pre_processed_surface_list):
        """
        + Second pass of the selection of the shading surfaces from the context.
        + Use raytracing to identify the obstructions among the context surfaces.
        + The context surfaces to test are generally pre-filtered by the first pass.
        + Rays are sent from the left, right and middle of each target building facade to the left, right and middle of
          target building facade.
        + The z coordinate of the receiver/context building vertices is the height of the context building.
        + The z coordinate of the sender/target building vertices is the minimum between the height of the target and
          the context building
        Args:
            pre_processed_surface_list [list]: list containing all the surfaces to test, usually pre filtered
                by the first pass. Each element, representing a surface, is a dictionary with the following properties
                 {"hb_face_obj", "area", "centroid":(Point3D), "lower_corner_point3d":{"left","right"},"height"}
        """
        # Initialization
        kept_surfaces = []  # surfaces to keep after the first pass
        # Preparation of the context in pyvista format
        list_hb_face_context = pre_processed_surface_list_to_hb_face_list(pre_processed_surface_list)
        context_mesh_pv = hb_face_list_to_pv_polydata(list_hb_face_context)

        # test
        # context_mesh_pv.plot(show_edges=True)

        for test_face in pre_processed_surface_list:  # loop over all the context surfaces
            for target_face in self.external_face_list_context:  # loop over all the surfaces of the target building
                # we use the _list_context as the surfaces are sorted from bigger to smaller and it is faster
                if is_obstructed(emitter=target_face, receiver=test_face, context=context_mesh_pv) == False:
                    kept_surfaces.append(test_face)  # if criteria valid, add the surface to the kept surface
                    break  # if a surface is context for one of the target surface, it is kept and thus stop the loop
            # print("surface checked")
        return kept_surfaces

    def correct_context_elevation(self):
        """ """
        for surface in self.context_hb_kept_first_pass:
            surface.move(Vector3D(0, 0, -self.elevation))

        for surface in self.context_shading_HB_faces:
            surface.move(Vector3D(0, 0, -self.elevation))

        for surface in self.all_context_hb_faces:
            surface.move(Vector3D(0, 0, -self.elevation))

        for surface in self.all_context_oriented_bb:
            surface.move(Vector3D(0, 0, -self.elevation))

    def context_surfaces_to_hbjson(self, path):
        """
        Convert HB_face context surface to HBjson file
        """
        surface_list = []
        for i, surface in enumerate(self.context_shading_HB_faces):
            surface_list.append(Face(("context_surface_{}_building_{}").format(i, self.id), surface.geometry))
        model = Model(identifier=("context_building_{}").format(self.id), orphaned_faces=surface_list)
        model.to_hbjson(name=("context_building_{}").format(self.id), folder=path)
        if self.context_hb_kept_first_pass!= []:
            surface_list = []
            for i, surface in enumerate(self.context_hb_kept_first_pass):
                surface_list.append(Face(("context_surface_{}_building_{}").format(i, self.id), surface.geometry))
            model = Model(identifier=("context_first_pass_building_{}").format(self.id), orphaned_faces=surface_list)
            model.to_hbjson(name=("first_pass_context_building_{}").format(self.id), folder=path)
        if self.all_context_hb_faces!= []:
            surface_list = []
            for i, surface in enumerate(self.all_context_hb_faces):
                surface_list.append(Face(("context_surface_{}_building_{}").format(i, self.id), surface.geometry))
            model = Model(identifier=("all_context_building_{}").format(self.id), orphaned_faces=surface_list)
            model.to_hbjson(name=("all_context_building_{}").format(self.id), folder=path)
        if self.all_context_oriented_bb != []:
            surface_list = []
            for i, surface in enumerate(self.all_context_oriented_bb):
                surface_list.append(Face(("context_surface_{}_building_{}").format(i, self.id), surface.geometry))
            model = Model(identifier=("all_context_bb_{}").format(self.id), orphaned_faces=surface_list)
            model.to_hbjson(name=("all_context_bb_{}").format(self.id), folder=path)

    def add_context_surfaces_to_HB_model(self):
        """
        Convert HB_face context surface to HBjson file
        """
        for i, surface in enumerate(self.context_shading_HB_faces):
            shade_obj = Shade(identifier=("shade_{}_building_{}").format(i, self.id), geometry=surface.geometry,
                              is_detached=True)
            self.HB_model.add_shade(shade_obj)


def distance_lb_geometry_point3d(pt_1, pt_2):
    """ Distance between 2 LB geometry Point3D """
    return sqrt((pt_1.x - pt_2.x) ** 2 + (pt_1.y - pt_2.y) ** 2 + (pt_1.z - pt_2.z) ** 2)


def max_VF(centroid_1, area_1, centroid_2, area_2):
    """
        Maximal view factor between the 2 surface, in the optimal configuration described in the context paper
        the faces are lists with following format :  [LB_face_obj,area, centroid]
    """
    ## distance between the centroids
    d = distance_lb_geometry_point3d(centroid_1, centroid_2)
    if d == 0:
        d = 0.01
    ## width of the optimal squares
    W_1 = sqrt(area_1)
    W_2 = sqrt(area_2)
    ## intermediary variable for the computation
    w_1 = W_1 / d
    w_2 = W_2 / d
    x = w_2 - w_1
    y = w_2 + w_1
    p = (w_1 ** 2 + w_2 ** 2 + 2) ** 2
    q = (x ** 2 + 2) * (y ** 2 + 2)
    u = sqrt(x ** 2 + 4)
    v = sqrt(y ** 2 + 4)
    s = u * (x * atan(x / u) - y * atan(y / u))
    t = v * (x * atan(x / v) - y * atan(y / v))
    return 1 / (pi * w_1 ** 2) * (log(p / q) + s - t)


def surface_dict_to_hb_faces(surface_dict_list):
    """ convert the list of dictionary surfaces to hb faces"""
    hb_surface_list = []  # if no surface return empty list
    if surface_dict_list != []:
        for surface_dict in surface_dict_list:
            hb_surface_list.append(surface_dict["hb_face_obj"])  # take the hb face from the dict
    return hb_surface_list


def context_building_to_surface_kept(pre_processed_building_surfaces_dict_to_test, building_to_keep,
                                     building_not_to_keep=[]):
    """ """
    # Initialization
    surface_dict_list = []
    # If we want all the surfaces
    if building_to_keep == "all":
        for id in list(pre_processed_building_surfaces_dict_to_test.keys()):
            if id not in building_not_to_keep:
                surface_list = pre_processed_building_surfaces_dict_to_test[id]["envelope_faces"]
                for surface in surface_list:
                    surface_dict_list.append(surface)
    # keep only the surfaces in the kept building
    else:
        for id in building_to_keep:
            surface_list = pre_processed_building_surfaces_dict_to_test[id]["envelope_faces"]
            for surface in surface_list:
                surface_dict_list.append(surface)

    return surface_dict_list

def context_building_to_bb_kept(pre_processed_building_surfaces_dict_to_test,building_not_to_keep=[]):
    """ """
    # Initialization
    surface_dict_list = []
    # If we want all the surfaces
    for id in list(pre_processed_building_surfaces_dict_to_test.keys()):
        if id not in building_not_to_keep:
            surface_list = pre_processed_building_surfaces_dict_to_test[id]["bounding_box_faces"]
            for surface in surface_list:
                surface_dict_list.append(surface)
    return surface_dict_list


def is_obstructed(emitter, receiver, context):
    """
        Check if the surfaces
    """
    # Initialization
    obstructed = True
    ## preprocess the vectors to check
    ray_list = ray_list_from_emitter_to_receiver(emitter, receiver, exclude_surface_from_ray=True, number_of_rays=3)
    ## loop over the context
    for ray in ray_list:
        # WARNING : the ray tracing work only if the surfaces are oriented

        # test
        # print(ray)
        # ray_3D=pv.PolyData(np.array([ray[0],ray[1],[ray[1][0],ray[1][1],ray[1][2]+1.],[ray[0][0],ray[0][1],ray[0][2]+1.]]),[4,0,1,2,3])
        # pv_emitter = hb_face_to_pv_polydata(emitter["hb_face_obj"])
        # context_2=context.copy()
        # context_2=context_2+ray_3D+pv_emitter

        points, ind = context.ray_trace(origin=ray[0], end_point=ray[1], first_point=False, plot=False)

        # test
        # print(ind)
        # context_2.plot(show_edges=True)

        if ind.size == 0:  # no obstruction
            obstructed = False
            # print("not obstructed")
            break
    # print("out of loop")
    return obstructed


def pre_processed_surface_list_to_hb_face_list(pre_processed_surface_list):
    """ Convert the preprocessed surface list into hb face list """
    return ([face["hb_face_obj"] for face in pre_processed_surface_list])


def hb_face_to_pv_polydata(hb_face):
    """ Convert the context hb face to a polydata Pyvista mesh  """

    # vertices
    vertices = []  # initialize the list of vertices
    lb_vertex_list = hb_face.vertices  # extract LB geometry vertices
    # face [number of vertices, index vertex 1, index vertex 2 ...] <=> [n, 0,1,2...]
    face = [len(lb_vertex_list)]
    # extraction
    for index, vertex in enumerate(lb_vertex_list):
        vertices.append([vertex.x, vertex.y, vertex.z])  # add the coordinates of the vertices
        face.append(index)
    vertices = np.array(vertices)  # convert into numpy array ( makes it faster to process for later

    return pv.PolyData(vertices, face)


def hb_face_list_to_pv_polydata(hb_face_list):
    """ Convert the context hb face to a polydata Pyvista mesh  """

    # Initialize mesh
    if hb_face_list != []:
        mesh = hb_face_to_pv_polydata(hb_face_list[0])
        for hb_face in hb_face_list[1:]:
            mesh = mesh + hb_face_to_pv_polydata(hb_face)

        # mesh = sum(mesh_list)  # merge all the sub_meshes/hb faces/facades of all the context building

        return mesh
    else:
        return []


def are_hb_faces_facing(hb_face_1, centroid_1, hb_face_2, centroid_2):
    """ Check with the normals if the surfaces are facing each other (and thus they can shade on each other) """

    # normal vectors
    normal_1 = hb_face_1.normal
    normal_2 = hb_face_2.normal
    # vectors from centroid_2 to centroid_1
    vector_21 = centroid_1 - centroid_2  # operation possible with LB Point3D
    # dot product
    dot_product_sup = normal_2.dot(vector_21)
    dot_product_inf = normal_1.dot(vector_21)
    # vivibility/facing criteria  (same as PyviewFactor)
    if dot_product_sup > 0 and dot_product_inf < 0:
        return True
    else:
        return False


def ray_list_from_emitter_to_receiver(emitter, receiver, exclude_surface_from_ray=True, number_of_rays=3):
    """
        Args:
            emitter [dict]: dictionary with the following properties of the emitter surface {"hb_face_obj", "area",
                "centroid":(Point3D), "lower_corner_point3d":{"left","right"},"height"}
            receiver [dict]: dictionary with the following properties of the receiver surface {"hb_face_obj", "area",
                "centroid":(Point3D), "lower_corner_point3d":{"left","right"},"height"}
            exclude_surface_from_ray [boolean]: True the rays are slightly shorten not to intersect
                with the emitter and receiver surfaces

        Output:
            ray list, with ray tuple (start, stop)
    """
    # z coordinate of the start and end of the rays
    z_receiver = receiver["elevation"] + receiver["height"]
    z_emitter = min([emitter["elevation"] + emitter["height"], z_receiver])
    # start vertices
    start_c = emitter["lower_corner_points"]["center"]
    start_l = emitter["lower_corner_points"]["left"]
    start_r = emitter["lower_corner_points"]["right"]
    start_c[2], start_l[2], start_r[2] = z_emitter, z_emitter, z_emitter  # correct the z coordinate
    # end vertices
    end_c = receiver["lower_corner_points"]["center"]
    end_l = receiver["lower_corner_points"]["left"]
    end_r = receiver["lower_corner_points"]["right"]
    end_c[2], end_l[2], end_r[2] = z_receiver, z_receiver, z_receiver  # correct the z coordinate

    # ray list
    ray_list = [
        (start_c, end_c),
        (start_c, end_l),
        (start_c, end_r),
        (start_l, end_l),
        (start_r, end_r),
        (start_l, end_c),
        (start_r, end_c),
        (start_l, end_r),
        (start_r, end_l),
    ]
    if exclude_surface_from_ray:
        for i in range(number_of_rays):
            ray_list[i] = excluding_surfaces_from_ray(start=ray_list[i][0], end=ray_list[i][1])
    return ray_list[:number_of_rays]


def excluding_surfaces_from_ray(start, end):
    """
        Return the start and end point of a ray reducing slightly the distance between the vertices to prevent
        considering the sender and receiver in the raytracing obstruction detection
    """
    ray_vector = end - start
    unit_vector = ray_vector / np.linalg.norm(ray_vector)  # normalize the vector with it's norm
    # Move the ray boundaries
    new_start = start + unit_vector * 0.05  # move the start vertex by 10cm on the toward the end vertex
    new_end = end - unit_vector * 0.05  # move the end vertex by 10cm on the toward the start vertex

    return new_start, new_end


def adjust_lower_corners(pt_left, pt_right):
    """
        move slightly the vertices to launch the rays from so that surfaces on corner will be detected as well
        pt_1 [Point3D]: point left
        pt_2 [Point3D]: point right
    """
    vector = pt_left - pt_right
    unit_vector = vector / np.linalg.norm(vector)
    new_point_left = pt_left - unit_vector * 0.1
    new_point_right = pt_right + unit_vector * 0.1
    return ([new_point_left, new_point_right])


def point3d_to_numpy_array(pt_3d):
    """ Convert LB Point3D to numpy array """

    return (np.array([pt_3d.x, pt_3d.y, pt_3d.z]))
