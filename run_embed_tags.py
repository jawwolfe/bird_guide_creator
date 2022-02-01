from guide_creator.embed_tags import EmbedTags
from guide_creator.configs import config
from globals import initialize_logger, initialize_sqlserver

SQLSERVER_NAME = config.SQLSERVER_NAME
SQLSERVER_DATABASE = config.SQLSERVER_DATABASE
AUDIO_PATH_FINAL = config.AUDIO_PATH_GUIDE
IMAGE_PATH_FINAL = config.IMAGE_PATH_GUIDE
PLAYLIST_ROOT = config.PLAYLIST_PATH
LOGGER = initialize_logger('bird_guide')
GOOGLE_API_SCOPES = config.GOOGLE_API_SCOPES
GOOGLE_CRED_PATH = config.GOOGLE_CRED_PATH
SUPER_GUIDE_PERMISSIONS = config.SUPER_GUIDE_PERMISSIONS


# todo add drive_root parameter "Playlist Directories"
embed = EmbedTags(logger=LOGGER, sql_server_connection=initialize_sqlserver(), image_path=IMAGE_PATH_FINAL,
                  audio_path=AUDIO_PATH_FINAL, playlist_root=PLAYLIST_ROOT, google_api_scopes=GOOGLE_API_SCOPES,
                  google_cred_path=GOOGLE_CRED_PATH, super_guide_perm=SUPER_GUIDE_PERMISSIONS)
embed.run_embed()
