from mains_tool.utils import *  # todo @Sharon: change with the new utils file

def main():

    currentDirectory = os.getcwd()
    Logspath = "/logs"
    isExist = os.path.exists(currentDirectory + Logspath)
    if not isExist:
       os.makedirs(currentDirectory + Logspath)

    LOG_FILENAME = datetime.now().strftime(currentDirectory + Logspath + '/logfile_%H_%M_%S_%d_%m_%Y.log')
    logging.basicConfig(filename=LOG_FILENAME, level=logging.INFO)



if __name__ == "__main__":
    main()