from guide_creator.update_taxonomy import UpdateTaxonomy, UpdateBLIConservation
from guide_creator.configs import config
from globals import initialize_logger, initialize_sqlserver

SQLSERVER_NAME = config.SQLSERVER_NAME
SQLSERVER_DATABASE = config.SQLSERVER_DATABASE
LOGGER = initialize_logger('bird_guide')


update_cons = UpdateBLIConservation(logger=LOGGER, sql_server_connection=initialize_sqlserver())
update_cons.run()

'''
date = UpdateTaxonomy(logger=LOGGER, sql_server_connection=initialize_sqlserver())
update.run_taxonomy_update()
'''