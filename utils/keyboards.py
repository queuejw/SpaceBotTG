# Создает кнопки

from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


# Создает кнопки потушить для сообщения пожара на корабле
def get_fire_inline_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Потушить", callback_data="fire_callback"))
    return builder.as_markup()
