from guide_creator.utilites import ParseEbirdRegions
from guide_creator.configs import config
from globals import initialize_sqlserver, initialize_logger

EBIRD_REGIONS_ROOT = config.EBIRD_REGIONS_ROOT
LOGGER = initialize_logger('bird_guide')

regions = ParseEbirdRegions(logger=LOGGER, sql_server_connection=initialize_sqlserver(),
                            ebird_base_url=EBIRD_REGIONS_ROOT, country='US', counties=1)
regions.run()
