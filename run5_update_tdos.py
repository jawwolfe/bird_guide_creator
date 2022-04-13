from guide_creator.manage_guide import CreateImageAudioTodoList
from guide_creator.configs import config
from globals import initialize_sqlserver, initialize_logger

TODO_PATH = config.TODO_PATH
AUDIO_GUIDE_PATH = config.AUDIO_PATH_GUIDE
LOGGER = initialize_logger('bird_guide')

update = CreateImageAudioTodoList(logger=LOGGER, sql_server_connection=initialize_sqlserver(),
                                  audio_guide_path=AUDIO_GUIDE_PATH, todo_path=TODO_PATH)
update.run()
