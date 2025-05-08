from aiogram import Router, F
from aiogram.types import CallbackQuery

from bot.messages import delete_message
from bot.save_game import check_and_save_data
from bot.shared import is_chat_active, exist_user_by_id, get_crew_text, all_ships, remove_chat_from_all_ships
from bot.text import get_computer_text, get_storage_text
from utils.check_role import check_role
from utils.edit_bot_message import edit_text
from utils.menu_keyboards import get_computer_menu_keyboard, get_crew_menu_keyboard, get_craft_menu_keyboard, \
    get_self_destruction_keyboard, get_storage_menu_keyboard
from utils.menu_reply_markup import get_main_menu_reply_markup

router = Router()


# Главное меню бота.
@router.callback_query(F.data.startswith("main_menu_"))
async def main_menu_callback(callback: CallbackQuery):
    chat_id = callback.message.chat.id
    if not is_chat_active(chat_id):
        await callback.answer("Игра не активна")
        return
    if not exist_user_by_id(chat_id, callback.from_user.id):
        await callback.answer("Вы не член экипажа")
        return

    user_id = callback.from_user.id
    captain = user_id == all_ships[chat_id]['crew'][0]['user_id']
    data = callback.data

    # Выход из меню
    if data == "main_menu_exit":
        await delete_message(callback.message.chat.id, callback.message.message_id)
        await callback.answer("Выключение бортового компьютера ...")

    # Кнопка назад на второстепенном меню (компьютер, экипаж)
    elif callback.data == "main_menu_back":
        await callback.answer("Назад")
        if await edit_text(chat_id, callback.message.message_id, "Меню бортового компьютера 🖥", callback.message.text,
                           get_main_menu_reply_markup(chat_id, callback.from_user.id)):
            await callback.answer("Назад")
        else:
            await callback.answer("Сбой!")

    # Компьютер
    elif data == "main_menu_computer":
        await edit_text(chat_id, callback.message.message_id, get_computer_text(chat_id), callback.message.text,
                        get_computer_menu_keyboard())
        await callback.answer("Бортовой компьютер")

    # Экипаж
    elif data == "main_menu_crew":
        await edit_text(chat_id, callback.message.message_id, get_crew_text(chat_id), callback.message.text,
                        get_crew_menu_keyboard())
        await callback.answer("Экипаж")

    # Склад
    elif data == "main_menu_storage":
        await edit_text(chat_id, callback.message.message_id, get_storage_text(chat_id), callback.message.text,
                        get_storage_menu_keyboard())
        await callback.answer("Склад")
    # Создание
    elif data == "main_menu_craft":
        if not check_role(2, chat_id, user_id):
            await edit_text(chat_id, callback.message.message_id, "Выберите предмет для создания 🛠",
                            callback.message.text,
                            get_craft_menu_keyboard())
        else:
            await callback.answer("⚠️ Только инженер или капитан может создавать предметы")
    # Самоуничтожение
    elif data == "main_menu_selfdestruction":
        if captain:
            await callback.answer("Вы уверены?")
            await edit_text(chat_id, callback.message.message_id, "ВЫ УВЕРЕНЫ В ТОМ, ЧТО ХОТИТЕ СДЕЛАТЬ ЭТО ?:",
                            callback.message.text,
                            get_self_destruction_keyboard())
        else:
            await callback.answer("Только капитан может сделать это ⚠️")

    # Пауза
    elif data == "main_menu_pause":
        if captain:
            check_and_save_data(all_ships[chat_id], chat_id)
            remove_chat_from_all_ships(chat_id)
            await edit_text(chat_id, callback.message.message_id,
                            "Игра остановлена! ✅\nℹ️ Продолжить игру можно командой /играть (загрузится последнее сохранение)",
                            callback.message.text, None)
        else:
            await callback.answer("ℹ️ Только капитан может остановить игру.")


# Кнопка обновить в меню компьютера
@router.callback_query(F.data == "menu_computer_update")
async def computer_menu_callback(callback: CallbackQuery):
    chat_id = callback.message.chat.id
    if not is_chat_active(chat_id):
        await callback.answer("Игра не активна")
        return
    if not exist_user_by_id(chat_id, callback.from_user.id):
        await callback.answer("Вы не член экипажа")
        return

    if await edit_text(chat_id, callback.message.message_id, get_computer_text(chat_id), callback.message.text,
                       get_computer_menu_keyboard()):
        await callback.answer("Обновлено")
    else:
        await callback.answer("Уже обновлено!")


# Кнопка обновить в меню экипажа
@router.callback_query(F.data == "menu_crew_update")
async def crew_menu_callback(callback: CallbackQuery):
    chat_id = callback.message.chat.id
    if not is_chat_active(chat_id):
        await callback.answer("Игра не активна")
        return
    if not exist_user_by_id(chat_id, callback.from_user.id):
        await callback.answer("Вы не член экипажа")
        return

    if await edit_text(chat_id, callback.message.message_id, get_crew_text(chat_id), callback.message.text,
                       get_crew_menu_keyboard()):
        await callback.answer("Обновлено")
    else:
        await callback.answer("Уже обновлено!")


# Кнопка обновить в меню склада
@router.callback_query(F.data == "menu_storage_update")
async def storage_menu_callback(callback: CallbackQuery):
    chat_id = callback.message.chat.id
    if not is_chat_active(chat_id):
        await callback.answer("Игра не активна")
        return
    if not exist_user_by_id(chat_id, callback.from_user.id):
        await callback.answer("Вы не член экипажа")
        return

    if await edit_text(chat_id, callback.message.message_id, get_storage_text(chat_id), callback.message.text,
                       get_storage_menu_keyboard()):
        await callback.answer("Обновлено")
    else:
        await callback.answer("Уже обновлено!")
