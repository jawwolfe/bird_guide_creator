from guide_creator.manage_guide import EbirdBarchartParseUtility, ExoticParseUtility, CreateImageAudioTodoList
from guide_creator.configs import config
from globals import initialize_sqlserver, initialize_logger

EBIRD_BARCHART_ROOT  = config.EBIRD_BARCHART_ROOT
EBIRD_ABUNDANCE_DIFFICULTY_MATRIX = config.EBIRD_ABUNDANCE_DIFFICULTY_MATRIX
EXOTIC_ROOT = config.EXOTIC_ROOT
TODO_PATH = config.TODO_PATH
AUDIO_GUIDE_PATH = config.AUDIO_PATH_GUIDE
LOGGER = initialize_logger('bird_guide')

update = EbirdBarchartParseUtility(logger=LOGGER, sql_server_connection=initialize_sqlserver(),
                                   ebird_base_url=EBIRD_BARCHART_ROOT,
                                   abundance_matrix=EBIRD_ABUNDANCE_DIFFICULTY_MATRIX)
update.parse_all_regions()


update = ExoticParseUtility(logger=LOGGER, sql_server_connection=initialize_sqlserver(),
                            exotic_base_url=EXOTIC_ROOT)
update.parse_all_guides()

update = CreateImageAudioTodoList(logger=LOGGER, sql_server_connection=initialize_sqlserver(),
                                  audio_guide_path=AUDIO_GUIDE_PATH, todo_path=TODO_PATH)
update.run()
