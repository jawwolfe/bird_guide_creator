from guide_creater.manage_guide import CreateGuide, UpdateGuide
from guide_creater.configs import config
from globals import initialize_logger, initialize_sqlserver

SQLSERVER_NAME = config.SQLSERVER_NAME
SQLSERVER_DATABASE = config.SQLSERVER_DATABASE
AUDIO_PATH_FINAL = config.AUDIO_PATH_GUIDE
IMAGE_PATH_FINAL = config.IMAGE_PATH_GUIDE
LOGGER = initialize_logger('bird_guide')


guide = CreateGuide(ebird_files={'Ariana_ebird.xlsx', 'Ben_Arous_ebird.xlsx', 'Bizerte_ebird.xlsx', 'Nabeul_ebird.xlsx',
                                 'Tunis_ebird.xlsx'},
                    exotic_file=None, targets_file=None, file_path=RAW_FILE_PATH, logger=LOGGER,
                    sql_server_connection=initialize_sqlserver(), guide_name='North Tunisia', image_path=IMAGE_PATH,
                    audio_path=AUDIO_PATH, playlist_root=PLAYLIST_PATH)
guide.run_create()
