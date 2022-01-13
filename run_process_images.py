from guide_creator.images_process import Optimize, Verify
from guide_creator.configs import config
from globals import initialize_sqlserver, initialize_logger


RAW_FILE_PATH = config.RAW_FILE_PATH
OPTIMIZE_PATH = config.OPTIMIZE_PATH
SOURCE_PATH = config.IMAGE_PATH
PLAYLIST_PATH = config.PLAYLIST_PATH
LOGGER = initialize_logger('bird_guide')


verify = Verify(logger=LOGGER, sql_server_connection=initialize_sqlserver(), optimize_path=OPTIMIZE_PATH,
                source_path=SOURCE_PATH)
verify.run_verification()

optum = Optimize(logger=LOGGER, optimize_path=OPTIMIZE_PATH, source_path=SOURCE_PATH)
optum.run_optimization()