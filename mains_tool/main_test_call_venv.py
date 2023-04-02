import sys
import os
import logging
# #sys.path.append('D://Elie//PhD//Programming//Elie_UBEM_tool')
#from urban_canopy.urban_canopy import UrbanCanopy
from datetime import datetime


# print ("zob")
# urban_canopy = UrbanCanopy()
#
def main():
    # os.system("notepad")
    currentDirectory = os.getcwd()
    Logspath = "/logs"
    isExist = os.path.exists(currentDirectory + Logspath)
    if not isExist:
       os.makedirs(currentDirectory + Logspath)

    LOG_FILENAME = datetime.now().strftime(currentDirectory + Logspath + '/logfile_%H_%M_%S_%d_%m_%Y.log')
    logging.basicConfig(filename=LOG_FILENAME, level=logging.INFO)

if __name__ == "__main__":
    main()