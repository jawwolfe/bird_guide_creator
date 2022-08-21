from guide_creator.utilites import PlaylistsSuperGuide, AbundanceChartSuperGuide, SQLUtilities
from guide_creator.configs import config
from globals import initialize_logger, initialize_sqlserver

SQLSERVER_NAME = config.SQLSERVER_NAME
SQLSERVER_DATABASE = config.SQLSERVER_DATABASE
PLAYLIST_ROOT = config.PLAYLIST_PATH
CHART_ROOT = config.CHART_ROOT
LOGGER = initialize_logger('bird_guide')
GOOGLE_API_SCOPES = config.GOOGLE_API_SCOPES
GOOGLE_CRED_PATH = config.GOOGLE_CRED_PATH
SUPER_GUIDE_PERMISSIONS = config.SUPER_GUIDE_PERMISSIONS


utilities = SQLUtilities(sp='sp_get_active_super_guides', logger=LOGGER, sql_server_connection=initialize_sqlserver())
super_guides = utilities.run_sql_return_no_params()

for super_guide in super_guides:
    playlists = PlaylistsSuperGuide(logger=LOGGER, sql_server_connection=initialize_sqlserver(),
                                    playlist_root=PLAYLIST_ROOT, google_api_scopes=GOOGLE_API_SCOPES,
                                    super_guide_id=super_guide[1], super_guide_name=super_guide[0],
                                    google_cred_path=GOOGLE_CRED_PATH, super_guide_perm=SUPER_GUIDE_PERMISSIONS,
                                    drive_root='Playlists Directories')
    playlists.refresh()
    playlists = AbundanceChartSuperGuide(logger=LOGGER, sql_server_connection=initialize_sqlserver(),
                                         chart_root=CHART_ROOT, google_api_scopes=GOOGLE_API_SCOPES,
                                         super_guide_id=super_guide[1], super_guide_name=super_guide[0],
                                         google_cred_path=GOOGLE_CRED_PATH, super_guide_perm=SUPER_GUIDE_PERMISSIONS,
                                         drive_root='Chart Directories')
    playlists.refresh()
