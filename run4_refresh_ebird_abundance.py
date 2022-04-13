from guide_creator.utilites import ParseGuideAbundance
from guide_creator.configs import config
from globals import initialize_sqlserver, initialize_logger

EBIRD_BARCHART_ROOT  = config.EBIRD_BARCHART_ROOT
EBIRD_ABUNDANCE_DIFFICULTY_MATRIX = config.EBIRD_ABUNDANCE_DIFFICULTY_MATRIX
EXOTIC_ROOT = config.EXOTIC_ROOT
LOGGER = initialize_logger('bird_guide')

update = ParseGuideAbundance(logger=LOGGER, sql_server_connection=initialize_sqlserver(),
                             ebird_matrix=EBIRD_ABUNDANCE_DIFFICULTY_MATRIX)
data = update.update_abundance_calc()
