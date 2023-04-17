import os
import sys

local_appdata = os.environ['LOCALAPPDATA']
path_tool = os.path.join(local_appdata, "Building_urban_analysis")

sys.path.append(os.path.join(path_tool, "Scripts"))