# Создает кнопки для меню создания предметов
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_main_menu_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="Выход", callback_data="main_menu_exit"),
        InlineKeyboardButton(text="Компьютер", callback_data="main_menu_computer"),
        InlineKeyboardButton(text="Экипаж", callback_data="main_menu_crew"),
    )
    return builder.as_markup()


def get_computer_menu_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="Назад", callback_data="menu_computer_back"),
        InlineKeyboardButton(text="Обновить", callback_data="menu_computer_update"),
    )
    return builder.as_markup()


def get_crew_menu_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="Назад", callback_data="menu_crew_back"),
        InlineKeyboardButton(text="Обновить", callback_data="menu_crew_update"),
    )
    return builder.as_markup()
