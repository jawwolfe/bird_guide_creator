from guide_creater.manage_guide import CreateGuide, UpdateGuide
from guide_creater.configs import config
from globals import initialize_logger, initialize_sqlserver

RAW_FILE_PATH = config.RAW_FILE_PATH
AUDIO_PATH = config.AUDIO_PATH
IMAGE_PATH = config.IMAGE_PATH
PLAYLIST_PATH = config.PLAYLIST_PATH
LOGGER = initialize_logger('bird_guide')

#'Exotic_Thailand_KYNP_edited.xlsx'
#'Exotic_Thailand_KYNP_TARGETS.xlsx'
#Khao Yai National Park
guide = CreateGuide(ebird_files={'Nakhon_Nayok_Ebird_edited.xlsx'},
                    exotic_file='Exotic_Thailand_KYNP_edited.xlsx', targets_file='Exotic_Thailand_KYNP_TARGETS.xlsx', file_path=RAW_FILE_PATH, logger=LOGGER,
                    sql_server_connection=initialize_sqlserver(), guide_name='Khao Yai National Park', image_path=IMAGE_PATH,
                    audio_path=AUDIO_PATH, playlist_root=PLAYLIST_PATH)
guide.run_create()
