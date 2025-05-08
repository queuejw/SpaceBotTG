# Создает кнопки для меню создания предметов
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_main_menu_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="Компьютер", callback_data="main_menu_computer"),
        InlineKeyboardButton(text="Экипаж", callback_data="main_menu_crew"),
        InlineKeyboardButton(text="Склад", callback_data="main_menu_storage")
    )
    builder.row(
        InlineKeyboardButton(text="Выход", callback_data="main_menu_exit")
    )
    return builder.as_markup()


def get_captain_main_menu_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="Компьютер", callback_data="main_menu_computer"),
        InlineKeyboardButton(text="Экипаж", callback_data="main_menu_crew"),
        InlineKeyboardButton(text="Роли", callback_data="main_menu_roles")
    )
    builder.row(
        InlineKeyboardButton(text="Склад", callback_data="main_menu_storage"),
        InlineKeyboardButton(text="Создание", callback_data="main_menu_craft"),
        InlineKeyboardButton(text="Ремонт", callback_data="main_menu_repair")
    )
    builder.row(
        InlineKeyboardButton(text="Пауза", callback_data="main_menu_pause"),
        InlineKeyboardButton(text="Самоуничтожение", callback_data="main_menu_selfdestruction")
    )
    builder.row(
        InlineKeyboardButton(text="Выход", callback_data="main_menu_exit")
    )
    return builder.as_markup()


def get_computer_menu_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="Назад", callback_data="main_menu_back"),
        InlineKeyboardButton(text="Обновить", callback_data="menu_computer_update")
    )
    return builder.as_markup()


def get_crew_menu_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="Назад", callback_data="main_menu_back"),
        InlineKeyboardButton(text="Обновить", callback_data="menu_crew_update")
    )
    return builder.as_markup()


def get_storage_menu_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="Назад", callback_data="main_menu_back"),
        InlineKeyboardButton(text="Обновить", callback_data="menu_storage_update")
    )
    return builder.as_markup()


def get_craft_menu_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🧯  (100📦)", callback_data="craft_extinguisher"),
        InlineKeyboardButton(text="🔫  (50📦)", callback_data="craft_bullet"),
        InlineKeyboardButton(text="⛽️ 10%  (75📦)", callback_data="craft_fuel")
    )
    builder.row(
        InlineKeyboardButton(text="Назад", callback_data="main_menu_back")
    )
    return builder.as_markup()


# Создает кнопки да и отмена для сообщения самоуничтожения
def get_self_destruction_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="Отмена", callback_data="main_menu_back"),
        InlineKeyboardButton(text="Отмена", callback_data="main_menu_back"),
        InlineKeyboardButton(text="Да", callback_data="self_destruction_continue")
    )
    return builder.as_markup()
