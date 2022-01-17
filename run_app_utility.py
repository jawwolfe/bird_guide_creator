from guide_creator.utilities_guide import Compare, Rename, RecreateImageList, RecreateAudioFiles
from guide_creator.utilites import PlaylistsSuperGuide
from guide_creator.configs import config
from globals import initialize_logger, initialize_sqlserver

SQLSERVER_NAME = config.SQLSERVER_NAME
SQLSERVER_DATABASE = config.SQLSERVER_DATABASE
AUDIO_PATH = config.AUDIO_PATH_GUIDE
IMAGE_PATH = config.IMAGE_PATH_GUIDE
PLAYLIST_ROOT = config.PLAYLIST_PATH
LOGGER = initialize_logger('bird_guide')
GOOGLE_API_SCOPES = config.GOOGLE_API_SCOPES
GOOGLE_CRED_PATH = config.GOOGLE_CRED_PATH

# refresh the playlists for this super guide
play = PlaylistsSuperGuide(logger=LOGGER, sql_server_connection=initialize_sqlserver(),
                           drive_root='Playlists Directories', playlist_root=PLAYLIST_ROOT,
                           google_api_scopes=GOOGLE_API_SCOPES,
                           google_cred_path=GOOGLE_CRED_PATH, super_guide_id=7,
                           super_guide_name='Birds of the World')
play.refresh()

#compare = Compare(logger=LOGGER, path_one='C:\\temp\\Bird Guide\\', path_two='C:\\temp\\Birds of the World\\',
 #                 sql_server_connection=initialize_sqlserver())
#compare.run_compare_dirs()

#image_list = RecreateAudioFiles(logger=LOGGER, sql_server_connection=initialize_sqlserver())
#image_list.run_recreate_audio_files()

#rename = Rename(logger=LOGGER, sql_server_connection=initialize_sqlserver(), path_audio='', path_images='')
#rename.run_rename()

#rename = Rename(LOGGER, initialize_sqlserver(), path_audio='C:\\temp\\Bird Guide\\', path_images=None)
#rename.run_rename()
