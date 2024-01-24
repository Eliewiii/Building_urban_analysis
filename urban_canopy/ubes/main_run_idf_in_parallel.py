"""
Run in parallel the idf files send as inputs in this file
"""
import os
import subprocess

# todo: import the function to run idf from path to idf, epw etc





if __name__ == '__main__':

    import argparse
    # Get the inputs from the command line
    parser = argparse.ArgumentParser()
    # todo: add the other parameters
    parser.add_argument("path_to_folder", type=str, help="path to the folder containing the idf files")

    # make a list of the idf files

    # run the idf files in parallel



