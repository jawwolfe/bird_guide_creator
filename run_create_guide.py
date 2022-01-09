from guide_creater.manage_guide import CreateGuide, UpdateGuide
from guide_creater.configs import config
from globals import initialize_logger, initialize_sqlserver

RAW_FILE_PATH = config.RAW_FILE_PATH
AUDIO_PATH = config.AUDIO_PATH
IMAGE_PATH = config.IMAGE_PATH
PLAYLIST_PATH = config.PLAYLIST_PATH
LOGGER = initialize_logger('bird_guide')


guide = CreateGuide(guide_name='Khao Yai National Park', exotic_name='KYNP', file_path=RAW_FILE_PATH, logger=LOGGER,
                    sql_server_connection=initialize_sqlserver(), image_path=IMAGE_PATH, audio_path=AUDIO_PATH,
                    playlist_root=PLAYLIST_PATH, test=1)
guide.run_create()
