"""
Utility functions for file and folder operations.
"""

import os
import shutil


def clean_directory(path):
    """

    """
    if os.path.exists(path):
        shutil.rmtree(path)
    os.mkdir(path)
