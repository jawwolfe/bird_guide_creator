from guide_creator.manage_guide import CreateGuide, UpdateGuide
from guide_creator.configs import config
from globals import initialize_logger, initialize_sqlserver

RAW_FILE_PATH = config.RAW_FILE_PATH
AUDIO_PATH = config.AUDIO_PATH
IMAGE_PATH = config.IMAGE_PATH
PLAYLIST_PATH = config.PLAYLIST_PATH
ROOT_PATH = config.ROOT_PATH
LOGGER = initialize_logger('bird_guide')


guide = CreateGuide(guide_name='Bangkok', exotic_name='', file_path=RAW_FILE_PATH, logger=LOGGER,
                    sql_server_connection=initialize_sqlserver(), image_path=IMAGE_PATH, audio_path=AUDIO_PATH,
                    playlist_root=PLAYLIST_PATH, test=1, root=ROOT_PATH, targets_only=1)
guide.run_create()
