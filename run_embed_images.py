from guide_creater.embed_tags import EmbedTags
from guide_creater.configs import config
from globals import initialize_logger, initialize_sqlserver

SQLSERVER_NAME = config.SQLSERVER_NAME
SQLSERVER_DATABASE = config.SQLSERVER_DATABASE
AUDIO_PATH_FINAL = config.AUDIO_PATH_GUIDE
IMAGE_PATH_FINAL = config.IMAGE_PATH_GUIDE
PLAYLIST_ROOT = config.PLAYLIST_PATH
LOGGER = initialize_logger('bird_guide')


embed = EmbedTags(logger=LOGGER, sql_server_connection=initialize_sqlserver(), image_path=IMAGE_PATH_FINAL,
                  audio_path=AUDIO_PATH_FINAL, playlist_root=PLAYLIST_ROOT)
embed.run_embed()
