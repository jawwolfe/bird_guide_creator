from guide_creator.manage_guide import EbirdBarchartParseUtility
from guide_creator.configs import config
from globals import initialize_sqlserver, initialize_logger

EBIRD_BARCHART_ROOT  = config.EBIRD_BARCHART_ROOT
EBIRD_ABUNDANCE_DIFFICULTY_MATRIX = config.EBIRD_ABUNDANCE_DIFFICULTY_MATRIX
LOGGER = initialize_logger('bird_guide')

update = EbirdBarchartParseUtility(logger=LOGGER, sql_server_connection=initialize_sqlserver(),
                                   ebird_base_url=EBIRD_BARCHART_ROOT,
                                   abundance_matrix=EBIRD_ABUNDANCE_DIFFICULTY_MATRIX)
update.parse_all_regions()


