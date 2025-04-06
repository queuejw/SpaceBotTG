# Создает кнопки обновить для сообщения компьютера
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


# Кнопка обновить для компьютера
def get_computer_inline_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Обновить", callback_data="update_computer_text"))
    return builder.as_markup()


# Создает кнопки да и отмена для сообщения самоуничтожения
def get_self_destruction_inline_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="Отмена", callback_data="self_destruction_cancel"),
        InlineKeyboardButton(text="Отмена", callback_data="self_destruction_cancel"),
        InlineKeyboardButton(text="Да", callback_data="self_destruction_continue")
    )
    return builder.as_markup()


# Создает кнопки потушить для сообщения пожара на корабле
def get_fire_inline_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Потушить", callback_data="fire_callback"))
    return builder.as_markup()
