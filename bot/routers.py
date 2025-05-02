from callbacks import computer_callback, fire_callback, storage_callback, selfdestruction_callback, craft_callback
from handlers import play_handler, start_help_info_handler, chat_handler, adm_handler, whitelist_handler, id_handler, \
    rename_handler, connection_handler, fly_handler, craft_handler, pause_handler, selfdestruction_handler, \
    computer_storage_crew_handler, shot_handler, repair_handler

router_list = [
    play_handler.router,
    start_help_info_handler.router,
    chat_handler.router,
    adm_handler.router,
    computer_callback.router,
    fire_callback.router,
    storage_callback.router,
    selfdestruction_callback.router,
    craft_callback.router,
    whitelist_handler.router,
    id_handler.router,
    rename_handler.router,
    craft_handler.router,
    connection_handler.router,
    fly_handler.router,
    pause_handler.router,
    selfdestruction_handler.router,
    computer_storage_crew_handler.router,
    shot_handler.router,
    repair_handler.router
]
