"""

"""

import numpy as np
import pyvista as pv

from current_development.mvfc_demonstration.utils_random_rectangle_generation import rectangle_normal


def plot_rectangle(rectangle_list, color_list):
    """
    Plot a rectangle using PyVista.
    :param rectangle_list: pv.Rectangle object representing the rectangle.
    :param color: Color of the rectangle (default is 'blue').
    """
    plotter = pv.Plotter()
    for rectangle, color in zip(rectangle_list, color_list):
        points = np.array(rectangle.points)
        poly = pv.PolyData(points)
        faces = np.array([[0, 1, 2]])
        poly.faces = faces
        plotter.add_mesh(poly, color=color, line_width=5)

    for rectangle, color in zip(rectangle_list, color_list):
        origin = np.array(rectangle.center)
        poly = pv.PolyData(origin)
        plotter.add_mesh(poly, color=color, point_size=10)


    plotter.show()



def plot_vertices(vertices, color='red'):
    """
    Plot vertices using PyVista.
    :param vertices: List of vertex coordinates.
    :param color: Color of the vertices (default is 'red').
    """
    points = np.array(vertices)
    poly = pv.PolyData(points)
    plotter = pv.Plotter()
    plotter.add_mesh(poly, color=color, point_size=10)
    plotter.show()


def plot_vector(origin, vector, color='green'):
    """
    Plot a vector using PyVista.
    :param origin: Starting point of the vector.
    :param vector: Direction and magnitude of the vector.
    :param color: Color of the vector (default is 'green').
    """
    points = np.array([origin, origin + vector])
    lines = np.array([[0, 1]])
    poly = pv.PolyData(points)
    poly.lines = lines
    plotter = pv.Plotter()
    plotter.add_mesh(poly, color=color, line_width=5)
    plotter.show()


def plot_segment(point1, point2, color='blue'):
    """
    Plot a line segment between two points using PyVista.
    :param point1: Starting point of the segment.
    :param point2: Ending point of the segment.
    :param color: Color of the segment (default is 'blue').
    """
    points = np.array([point1, point2])
    lines = np.array([[0, 1]])
    poly = pv.PolyData(points)
    poly.lines = lines
    plotter = pv.Plotter()
    plotter.add_mesh(poly, color=color, line_width=5)
    plotter.show()
