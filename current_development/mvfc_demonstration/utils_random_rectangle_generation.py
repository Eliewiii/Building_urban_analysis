"""

"""
import sys

import random

import numpy as np
import pyvista as pv
import pyviewfactor as pvf

from math import sqrt, atan, log, pi


def generate_random_rectangles(min_size: float = 0.0001, max_size: float = 100.):
    """

    """

    max_distance = 100 * max_size

    def generate_ref_rectangle_in_xy_plane():
        """ Generate a rectangle in the (x, y) plane. """
        width = random.uniform(min_size, max_size)
        pointa = [1, 0, 0]
        pointb = [1, width, 0]
        pointc = [0, width, 0]
        pointd = [0, 0, 0]
        return pv.Rectangle([pointa, pointb, pointc])

    def generate_random_rectangle(ref_rectangle):
        """ Generate a random rectangle that faces the reference rectangle. """
        # Select a random vertex for the centroid of the new rectangle
        ref_rectangle_centroid = np.array(ref_rectangle.center)
        rectangle_centroid = random_point_with_maximum_distance_from_point(point=ref_rectangle_centroid,
                                                                           max_distance=max_distance,
                                                                           ensure_z_posive=True)
        # Select a random normal unit vector for the new rectangle

        random_normal_unit_vector = random_nonzero_vector(ensure_z_negative=True)
        random_normal_unit_vector = normalize_vector(random_normal_unit_vector)
        # Select a random distance from the reference rectangle
        random_distance = random.uniform(0, max_distance)

        # Compute the centroid of the reference rectangle
        centroid = np.array(ref_rectangle.center)
        # Compute the centroid of the random rectangle
        random_centroid = [centroid[0] + random_distance * (-random_normal_unit_vector[0]),
                           centroid[1] + random_distance * (-random_normal_unit_vector[1]),
                           centroid[2] + random_distance * (-random_normal_unit_vector[2])]
        # Unit vectors of the plane that contains the reference rectangle and are orthogonal to the random_normal_unit_vector
        random_orthogonal_vectors(normal_vec=random_normal_unit_vector)
        # rotate the unit vector by a random angle around the normal vector
        random_angle = random.uniform(0, 2 * pi)
        rotation_matrix_according_to_normal_vector =

        random_unit_vector_1 = [
            random_unit_vector_1[0] * cos(random_angle) + random_unit_vector_2[0] * sin(random_angle),
            random_unit_vector_1[1] * cos(random_angle) + random_unit_vector_2[1] * sin(random_angle),
            random_unit_vector_1[2] * cos(random_angle) + random_unit_vector_2[2] * sin(random_angle)]
        random_unit_vector_2 = [
            random_unit_vector_2[0] * cos(random_angle) - random_unit_vector_1[0] * sin(random_angle),
            random_unit_vector_2[1] * cos(random_angle) - random_unit_vector_1[1] * sin(random_angle),
            random_unit_vector_2[2] * cos(random_angle) - random_unit_vector_1[2] * sin(random_angle)]
        # normalize the unit vectors
        random_unit_vector_1 = normalize_vector(random_unit_vector_1)
        random_unit_vector_2 = normalize_vector(random_unit_vector_2)

        # Compute the random rectangle
        random_width = random.uniform(min_size, max_size)
        random_length = random.uniform(min_size, max_size)

def random_face_normal_vector_facing_face(vertex_ref:np.ndarray,normal_ref:np.ndarray,vertex_new:np.ndarray,normalize:bool=False):
    """
    Generate a random face normal vector facing a reference face.
    :param vertex_ref: The reference face vertex.
    :param normal_ref: The reference face normal vector.
    :param vertex_new: The new face vertex.
    :param normalize: Normalize the random face normal vector.
    :return: The random face normal vector.
    """
    random_normal_unit_vector = random_nonzero_vector(normalize=normalize)
    # Check if the faces are facing each other
    if not are_faces_facing(vertex_ref, normal_ref, vertex_new, random_normal_unit_vector):
        random_normal_unit_vector = - random_normal_unit_vector
        if not are_faces_facing(vertex_ref, normal_ref, vertex_new, random_normal_unit_vector):
            raise ValueError("Could not generate a random face normal vector facing the reference face")

    return random_normal_unit_vector


def random_point_with_maximum_distance_from_point(point: np.ndarray, max_distance: float,
                                                  ensure_z_posive: bool = True) -> np.ndarray:
    """
    Generate a random point with a maximum distance from a given point.
    :param point: The given point.
    :param max_distance: The maximum distance.
    :return: The random point.
    """
    # make a random vector
    random_unit_vector = random_nonzero_vector(ensure_z_posive=ensure_z_posive, normalize=True)
    # normalize the random vector
    random_distance = max_distance * random.uniform(sys.float_info.epsilon, 1)
    return point + random_distance * random_unit_vector


def random_orthogonal_vectors(normal_vec: np.ndarray,normalize:bool=False) -> tuple[np.ndarray, np.ndarray]:
    """
    Generate two random orthogonal vectors to a given normal vector.
    :param normal_vec: The normal vector.
    :param normalize: Normalize the orthogonal vectors.
    :return: Two orthogonal vectors.
    """
    # Generate a random vector
    rand_vec = non_parallel_random_nonzero_vector()
    # Project rand_vec onto normal_vec to get a component parallel to normal_vec
    parallel_component = np.dot(rand_vec, normal_vec) * normal_vec
    # Subtract the parallel component from rand_vec to get a vector perpendicular to normal_vec
    perpendicular_vec = rand_vec - parallel_component
    # Normalize the perpendicular vector to get the first orthogonal vector
    ortho_vec1 = perpendicular_vec / np.linalg.norm(perpendicular_vec)
    # Calculate the second orthogonal vector using the cross product with normal_vec
    ortho_vec2 = np.cross(normal_vec, ortho_vec1)
    # Normalize the second orthogonal vector
    ortho_vec2 /= np.linalg.norm(ortho_vec2)

    if normalize:
        ortho_vec1 = normalize_vector(ortho_vec1)
        ortho_vec2 = normalize_vector(ortho_vec2)

    return ortho_vec1, ortho_vec2


def are_faces_facing(centroid_1: np.ndarray, normal_1: np.ndarray, centroid_2: np.ndarray,
                                  normal_2: np.ndarray):
    """
    Visibility check between 2 faces
    :param centroid_1: centroid of the first face
    :param normal_1: normal vector of the first face
    :param centroid_2: centroid of the second face
    :param normal_2: normal vector of the second face
    :return: True if the faces are facing each other, False otherwise
    """
    # vectors from centroid_2 to centroid_1
    vector_21 = centroid_1 - centroid_2
    # dot product
    dot_product_sup = normal_2.dot(vector_21)
    dot_product_inf = normal_1.dot(vector_21)
    # visibility/facing criteria  (same as PyviewFactor)
    if dot_product_sup > 0 > dot_product_inf:
        return True
    else:
        return False

def normalize_vector(vector: np.ndarray) -> np.ndarray:
    """
    Normalize a vector
    :param vector: vector to normalize
    :return: normalized vector
    """
    # Ensure the norm is not zero
    if np.linalg.norm(vector) < 1e-6:
        raise ValueError("Cannot normalize a vector with zero norm")
    return vector / np.linalg.norm(vector)


def non_parallel_random_nonzero_vector(normal_vec: np.ndarray) -> np.ndarray:
    """ Generate a random nonzero 3D vector that is not parallel to a given normal vector. """
    for i in range(100):
        rand_vec = random_nonzero_vector()
        # Check if the cross product is not close to zero
        if np.linalg.norm(np.cross(rand_vec, normal_vec)) > 1e-6:
            return rand_vec
    raise ValueError(
        "Could not generate a nonzero vector that is not parallel to the given vector after 100 attempts")


def random_nonzero_vector(ensure_z_posive: bool = False, ensure_z_negative=False,
                          normalize: bool = False) -> np.ndarray:
    """Generate a random nonzero 3D vector."""
    for i in range(100):
        rand_vec = [random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1, 1)]
        if ensure_z_posive:
            rand_vec[2] = abs(rand_vec[2])
        if ensure_z_negative:
            rand_vec[2] = -abs(rand_vec[2])
        if np.linalg.norm(rand_vec) > 1e-6:  # Check if norm is not too close to zero
            if normalize:
                return normalize_vector(rand_vec)
            return rand_vec
    raise ValueError("Could not generate a nonzero vector after 100 attempts")



