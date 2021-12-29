from guide_creater.utilities_guide import Compare, Rename, RecreateImageList, RecreateAudioFiles
from guide_creater.configs import config
from globals import initialize_logger, initialize_sqlserver

SQLSERVER_NAME = config.SQLSERVER_NAME
SQLSERVER_DATABASE = config.SQLSERVER_DATABASE
AUDIO_PATH = config.AUDIO_PATH_GUIDE
IMAGE_PATH = config.IMAGE_PATH_GUIDE
LOGGER = initialize_logger('bird_guide')


#compare = Compare(logger=LOGGER, path_one='', path_two='')
#compare.run_compare()

#image_list = RecreateAudioFiles(logger=LOGGER, sql_server_connection=initialize_sqlserver())
#image_list.run_recreate_audio_files()

#rename = Rename(logger=LOGGER, sql_server_connection=initialize_sqlserver(), path_audio='', path_images='')
#rename.run_rename()

rename = Rename(LOGGER, initialize_sqlserver(), path_audio='C:\\temp\\Utilities\\', path_images=None)
rename.run_rename()
