from guide_creator.manage_guide import EbirdBarchartParseUtility, ExoticParseUtility
from guide_creator.utilites import ParseGuideAbundance
from guide_creator.configs import config
from globals import initialize_sqlserver, initialize_logger
import sys

EBIRD_BARCHART_ROOT  = config.EBIRD_BARCHART_ROOT
EBIRD_ABUNDANCE_DIFFICULTY_MATRIX = config.EBIRD_ABUNDANCE_DIFFICULTY_MATRIX
EXOTIC_ROOT = config.EXOTIC_ROOT
LOGGER = initialize_logger('bird_guide')


update = ExoticParseUtility(logger=LOGGER, sql_server_connection=initialize_sqlserver(),
                            exotic_base_url=EXOTIC_ROOT)
update.parse_exotic_errors()

'''
update = EbirdBarchartParseUtility(logger=LOGGER, sql_server_connection=initialize_sqlserver(),
                                   ebird_base_url=EBIRD_BARCHART_ROOT,
                                   abundance_matrix=EBIRD_ABUNDANCE_DIFFICULTY_MATRIX)
update.parse_all_regions()

update = ExoticParseUtility(logger=LOGGER, sql_server_connection=initialize_sqlserver(),
                            exotic_base_url=EXOTIC_ROOT)
update.parse_all_guides()


update = ParseGuideAbundance(logger=LOGGER, sql_server_connection=initialize_sqlserver(),
                             ebird_matrix=EBIRD_ABUNDANCE_DIFFICULTY_MATRIX)
data = update.update_abundance_calc()
'''
