from guide_creater.manage_guide import CreateGuide, UpdateGuide
from guide_creater.configs import config
import os, logging, datetime
from guide_creater.connection import SQLServerConnection

'''Get the name of the root directory for the log path and call it APP NAME'''
dir_path = os.getcwd()
APP_NAME = dir_path[dir_path.rindex('\\')+1:]
SQLSERVER_NAME = config.SQLSERVER_NAME
SQLSERVER_DATABASE = config.SQLSERVER_DATABASE
LOG_FILE_PATH = config.LOG_FILE_PATH
BIRDS_FILE_PATH = config.BIRDS_FILE_PATH
AUIDO_PATH = config.AUDIO_PATH
IMAGE_PATH = config.IMAGE_PATH
LOG_MESSAGE = '%(asctime)s -%(process)d - %(levelname)s - %(message)s'
LOG_TIME = '%d-%b-%y %H:%M:%S'


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


LOGGER = initialize_logger('bird_guide')

# {'Ariana_ebird.xlsx', 'Ben_Arous_ebird.xlsx', 'Bizerte_ebird.xlsx', 'Nabeul_ebird.xlsx', 'Tunis_ebird.xlsx'}

'''
guide = CreateGuide(ebird_files={'Palawan_ebird_12-15-21.xlsx'}, exotic_file='Palawan_exotic_edited.xlsx',
                    targets_file='Palawan_targets.xlsx', file_path=BIRDS_FILE_PATH, logger=LOGGER,
                    sql_server_connection=initialize_sqlserver(), guide_name='Palawan PH', image_path=IMAGE_PATH,
                    audio_path=AUIDO_PATH)
guide.run_create()
'''

guide = UpdateGuide(ebird_files={'Cebu_ebird_12-15-21.xlsx'}, file_path=BIRDS_FILE_PATH, logger=LOGGER,
                    sql_server_connection=initialize_sqlserver(),
                    guide_name='Cebu PH', image_path=IMAGE_PATH, audio_path=AUIDO_PATH)
guide.run_update()


