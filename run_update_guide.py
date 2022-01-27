from guide_creator.manage_guide import UpdateGuide
from guide_creator.configs import config
from globals import initialize_sqlserver, initialize_logger


RAW_FILE_PATH = config.RAW_FILE_PATH
AUDIO_PATH = config.AUDIO_PATH
IMAGE_PATH = config.IMAGE_PATH
PLAYLIST_PATH = config.PLAYLIST_PATH
ROOT_PATH = config.ROOT_PATH
LOGGER = initialize_logger('bird_guide')


guide = UpdateGuide(file_path=RAW_FILE_PATH, logger=LOGGER,
                    sql_server_connection=initialize_sqlserver(),
                    guide_name='Cebu PH', image_path=IMAGE_PATH, audio_path=AUDIO_PATH, playlist_root=PLAYLIST_PATH,
                    test=1, root=ROOT_PATH)
guide.run_update()
