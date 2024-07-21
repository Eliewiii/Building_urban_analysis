"""

"""
from pyvista import Rectangle

import pytest
import pyviewfactor as pvf

from current_development.mvfc_demonstration.utils_random_rectangle_generation import *
from current_development.mvfc_demonstration.test.plot_pyvista_obj import *


def test_generate_random_rectangles():
    ref_rectangle, random_rectangle = generate_random_rectangles(min_size=1, max_size=5,max_distance_factor=5)

    # plot_rectangle([ref_rectangle,random_rectangle],['blue',"red"])
    print(pvf.get_visibility(ref_rectangle, random_rectangle, strict=False, print_warning=True))
