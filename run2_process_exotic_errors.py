from guide_creator.manage_guide import ExoticParseUtility
from guide_creator.configs import config
from globals import initialize_sqlserver, initialize_logger

EBIRD_BARCHART_ROOT  = config.EBIRD_BARCHART_ROOT
EXOTIC_ROOT = config.EXOTIC_ROOT
LOGGER = initialize_logger('bird_guide')

# Note: you must first manually set the BirdID in the error tables for all values where Entered is 0:
# BirdsRegionsAbundance_Errs and ExoticChecklists_Errs
# These are due to taxonomy changes not reflected in Exotic data


update = ExoticParseUtility(logger=LOGGER, sql_server_connection=initialize_sqlserver(),
                            exotic_base_url=EXOTIC_ROOT)
update.parse_all_errors()

