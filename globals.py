from guide_creater.configs import config
import os, logging, datetime
from guide_creater.connection import SQLServerConnection

'''Get the name of the root directory for the log path and call it APP NAME'''
dir_path = os.getcwd()
APP_NAME = dir_path[dir_path.rindex('\\')+1:]
LOG_FILE_PATH = config.LOG_FILE_PATH
LOG_MESSAGE = '%(asctime)s -%(process)d - %(levelname)s - %(message)s'
LOG_TIME = '%d-%b-%y %H:%M:%S'
SQLSERVER_NAME = config.SQLSERVER_NAME
SQLSERVER_DATABASE = config.SQLSERVER_DATABASE


def initialize_logger(directory):
    full_path = LOG_FILE_PATH + '\\' + APP_NAME + '_' + directory + '\\' + \
                datetime.datetime.now().strftime("%Y-%m-%d") + '.log'
    global_format = logging.Formatter(LOG_MESSAGE, LOG_TIME)
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    file_logger = logging.FileHandler(full_path)
    file_logger.setLevel(logging.INFO)
    file_logger.setFormatter(global_format)
    logger.addHandler(file_logger)
    return logger


def initialize_sqlserver():
    sqlserver_connection = SQLServerConnection(name=SQLSERVER_NAME, database=SQLSERVER_DATABASE)
    return sqlserver_connection
