from guide_creator.gdrive_bird_directories import GDriveBirdDirectories
from guide_creator.configs import config
from globals import initialize_logger, initialize_sqlserver

SQLSERVER_NAME = config.SQLSERVER_NAME
SQLSERVER_DATABASE = config.SQLSERVER_DATABASE
AUDIO_PATH_FINAL = config.AUDIO_PATH_GUIDE
LOGGER = initialize_logger('bird_guide')
GOOGLE_API_SCOPES = config.GOOGLE_API_SCOPES
GOOGLE_CRED_PATH = config.GOOGLE_CRED_PATH
ROOT_GUIDE_DIR = config.ROOT_GUIDE_DIR


google = GDriveBirdDirectories(logger=LOGGER, sql_server_connection=initialize_sqlserver(),
                               audio_path=AUDIO_PATH_FINAL,  google_api_scopes=GOOGLE_API_SCOPES,
                               google_cred_path=GOOGLE_CRED_PATH, root_guide_dir=ROOT_GUIDE_DIR)
google.refresh()
