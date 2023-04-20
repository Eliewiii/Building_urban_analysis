"""
Add to the python path the path of the scripts of the tool.
Meant to be run before the main script when the called from Grasshopper.
It should be run before the main in the batch file.
"""

import sys
from utils_general import path_scripts_tool

# Add the path of the scripts to the python path
sys.path.append(path_scripts_tool)
