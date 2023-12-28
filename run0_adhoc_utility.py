from guide_creator.utilities_guide import  Compare
from guide_creator.configs import config
from globals import initialize_sqlserver, initialize_logger


IMAGE_PATH_GUIDE =  config.IMAGE_PATH_GUIDE
LOGGER = initialize_logger('bird_guide')

update = Compare(logger=LOGGER, path_one=IMAGE_PATH_GUIDE, sql_server_connection=initialize_sqlserver())
update.run_compare_db_directory()