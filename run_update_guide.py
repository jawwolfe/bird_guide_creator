from guide_creater.manage_guide import UpdateGuide
from guide_creater.configs import config
from globals import initialize_sqlserver, initialize_logger


RAW_FILE_PATH = config.RAW_FILE_PATH
AUDIO_PATH = config.AUDIO_PATH
IMAGE_PATH = config.IMAGE_PATH
PLAYLIST_PATH = config.PLAYLIST_PATH
LOGGER = initialize_logger('bird_guide')


guide = UpdateGuide(ebird_files={'Cebu_ebird_12-15-21.xlsx'}, file_path=RAW_FILE_PATH, logger=LOGGER,
                    sql_server_connection=initialize_sqlserver(),
                    guide_name='Cebu PH', image_path=IMAGE_PATH, audio_path=AUDIO_PATH, playlist_root=PLAYLIST_PATH,
                    test=1)
guide.run_update()
