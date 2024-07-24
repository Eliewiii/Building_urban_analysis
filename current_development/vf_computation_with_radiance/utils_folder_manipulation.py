"""
Utility functions for folder manipulation.
"""

import os


def check_file_exist(file_path: str):
    """
    Check if a file exists and raise an error if not.
    :param file_path: str, the path of the file.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")


def check_parent_folder_exist(file_path: str):
    """
    Check if the parent folder of a file path exists and raise an error if not.
    :param file_path: str, the path of the file.
    """
    parent_folder = os.path.dirname(file_path)
    if not os.path.exists(parent_folder):
        raise FileNotFoundError(f"Folder not found: {parent_folder}")
