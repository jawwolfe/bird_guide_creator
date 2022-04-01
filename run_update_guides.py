from guide_creator.manage_guide import UpdateGuides
from globals import initialize_sqlserver, initialize_logger

LOGGER = initialize_logger('bird_guide')

update = UpdateGuides(logger=LOGGER, sql_server_connection=initialize_sqlserver())
update.run()


