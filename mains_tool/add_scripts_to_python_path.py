"""
Add to the python path the path of the scripts of the tool.
Meant to be run before the main script when the called from Grasshopper.
It should be run before the main in the batch file.
"""

import sys
import os

# from mains_tool.utils_general import path_scripts_tool
# as the scripts are not added to the path yet, we need to get the path of the scripts manually,
# it cannot be imported from another script, or its path should be added to the path before importing it
# or it can be an argrument of the script given inside the batch file

# Get Appdata\local folder
local_appdata = os.environ['LOCALAPPDATA']
path_tool = os.path.join(local_appdata, "Building_urban_analysis")
# Path of the different folders in the tool
path_scripts_tool = os.path.join(path_tool, "Scripts")

# Add the path of the scripts to the python path
sys.path.append(path_scripts_tool)
print(path_scripts_tool)
