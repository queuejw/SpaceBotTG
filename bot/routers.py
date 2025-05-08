from callbacks import fire_callback, selfdestruction_callback, craft_callback, \
    menu_callback
from handlers import play_handler, start_help_info_handler, chat_handler, adm_handler, user_handler, id_handler, \
    rename_handler, connection_handler, fly_handler, shot_handler, repair_handler, role_handler, menu_handler

router_list = [
    play_handler.router,
    start_help_info_handler.router,
    chat_handler.router,
    adm_handler.router,
    fire_callback.router,
    selfdestruction_callback.router,
    craft_callback.router,
    user_handler.router,
    id_handler.router,
    rename_handler.router,
    connection_handler.router,
    fly_handler.router,
    shot_handler.router,
    repair_handler.router,
    role_handler.router,
    menu_handler.router,
    menu_callback.router
]
