from aiogram.types import InlineKeyboardMarkup

from bot.shared import get_user_by_id
from utils.menu_keyboards import get_captain_main_menu_keyboard, get_main_menu_keyboard


def get_main_menu_reply_markup(chat_id: int, user_id: int) -> InlineKeyboardMarkup:
    user_role = int(get_user_by_id(chat_id, user_id)['user_role'])
    reply_markup: InlineKeyboardMarkup
    match user_role:
        case 1:
            return get_captain_main_menu_keyboard()
        case _:
            return get_main_menu_keyboard()
