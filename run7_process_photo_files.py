from guide_creator.files_process import OptimizeImages, VerifyFileNames
from guide_creator.configs import config
from globals import initialize_sqlserver, initialize_logger

OPTIMIZE_PATH = config.OPTIMIZE_PATH
SOURCE_PATH = config.IMAGE_PATH
LOGGER = initialize_logger('bird_guide')

verify = VerifyFileNames(logger=LOGGER, sql_server_connection=initialize_sqlserver(), source_path=SOURCE_PATH,
                         is_image=1)
verify.run_verification()

optum = OptimizeImages(logger=LOGGER, source_path=SOURCE_PATH, optimize_path=OPTIMIZE_PATH)
optum.run_optimization()

