from guide_creator.manage_guide import UpdateGuides
from globals import initialize_sqlserver, initialize_logger
from guide_creator.configs import config

LOGGER = initialize_logger('bird_guide')
EBIRD_MATRIX = config.EBIRD_ABUNDANCE_DIFFICULTY_MATRIX

update = UpdateGuides(logger=LOGGER, ebird_matrix=EBIRD_MATRIX, sql_server_connection=initialize_sqlserver())
update.run()


