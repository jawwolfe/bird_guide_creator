from guide_creator.files_process import RenameAudioFiles, VerifyFileNames
from guide_creator.configs import config
from globals import initialize_sqlserver, initialize_logger

AUDIO_PATH = config.AUDIO_PATH_FINISHED
SOURCE_PATH = config.UTILITIES_PATH
LOGGER = initialize_logger('bird_guide')

rename = RenameAudioFiles(logger=LOGGER, source_path=SOURCE_PATH, destination_path=AUDIO_PATH)
rename.run_rename()

verify = VerifyFileNames(logger=LOGGER, sql_server_connection=initialize_sqlserver(), source_path=SOURCE_PATH,
                         is_image=0)
verify.run_verification()

rename.run_move()
