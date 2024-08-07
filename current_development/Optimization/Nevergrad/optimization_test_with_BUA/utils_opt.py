"""

"""

import shutil
import os


def duplicate_folder(src_folder, dest_folder, overwrite=False):
    """
    Duplicate a folder from src_folder to dest_folder, with an option to overwrite the destination folder if it already exists.

    :param src_folder: Path to the source folder.
    :param dest_folder: Path to the destination folder.
    :param overwrite: If True, the destination folder will be deleted if it exists. Default is False.
    """
    if not os.path.exists(src_folder):
        raise FileNotFoundError(f"The source folder '{src_folder}' does not exist.")

    # Check if the destination folder already exists
    if os.path.exists(dest_folder):
        if overwrite:
            # Remove the existing destination folder and its contents
            shutil.rmtree(dest_folder)
            print(f"Existing folder '{dest_folder}' has been deleted.")
        else:
            raise FileExistsError(
                f"The destination folder '{dest_folder}' already exists and overwrite is set to False.")

    # Copy the entire folder
    shutil.copytree(src_folder, dest_folder)

