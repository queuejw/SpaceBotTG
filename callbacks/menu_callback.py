from aiogram import Router, F
from aiogram.types import CallbackQuery

from bot.messages import delete_message
from bot.shared import is_chat_active, exist_user_by_id, get_crew_text
from bot.text import get_computer_text
from utils.edit_bot_message import edit_text
from utils.game_keyboards import get_computer_menu_keyboard, get_main_menu_keyboard, get_crew_menu_keyboard

router = Router()


@router.callback_query(F.data.startswith("main_menu_"))
async def main_menu_callback(callback: CallbackQuery):
    chat_id = callback.message.chat.id
    if not is_chat_active(chat_id):
        await callback.answer("Игра не активна")
        return
    if not exist_user_by_id(chat_id, callback.from_user.id):
        await callback.answer("Вы не член экипажа")
        return
    if callback.data == "main_menu_exit":
        await delete_message(callback.message.chat.id, callback.message.message_id)
        await callback.answer("Выключение бортового компьютера ...")

    elif callback.data == "main_menu_computer":
        await edit_text(chat_id, callback.message.message_id, get_computer_text(chat_id), callback.message.text,
                        get_computer_menu_keyboard())
        await callback.answer("Бортовой компьютер")

    elif callback.data == "main_menu_crew":
        await edit_text(chat_id, callback.message.message_id, get_crew_text(chat_id), callback.message.text,
                        get_crew_menu_keyboard())
        await callback.answer("Экипаж")


@router.callback_query(F.data.startswith("menu_computer_"))
async def computer_menu_callback(callback: CallbackQuery):
    chat_id = callback.message.chat.id
    if not is_chat_active(chat_id):
        await callback.answer("Игра не активна")
        return
    if not exist_user_by_id(chat_id, callback.from_user.id):
        await callback.answer("Вы не член экипажа")
        return
    if callback.data == "menu_computer_back":
        await callback.answer("Назад")
        if await edit_text(chat_id, callback.message.message_id, "Меню бортового компьютера 🖥", callback.message.text,
                           get_main_menu_keyboard()):
            await callback.answer("Назад")
        else:
            await callback.answer("Сбой!")

    elif callback.data == "menu_computer_update":
        if await edit_text(chat_id, callback.message.message_id, get_computer_text(chat_id), callback.message.text,
                           get_computer_menu_keyboard()):
            await callback.answer("Обновлено")
        else:
            await callback.answer("Уже обновлено!")


@router.callback_query(F.data.startswith("menu_crew_"))
async def computer_menu_callback(callback: CallbackQuery):
    chat_id = callback.message.chat.id
    if not is_chat_active(chat_id):
        await callback.answer("Игра не активна")
        return
    if not exist_user_by_id(chat_id, callback.from_user.id):
        await callback.answer("Вы не член экипажа")
        return
    if callback.data == "menu_crew_back":
        await callback.answer("Назад")
        if await edit_text(chat_id, callback.message.message_id, "Меню бортового компьютера 🖥", callback.message.text,
                           get_main_menu_keyboard()):
            await callback.answer("Назад")
        else:
            await callback.answer("Сбой!")

    elif callback.data == "menu_crew_update":
        if await edit_text(chat_id, callback.message.message_id, get_crew_text(chat_id), callback.message.text,
                           get_crew_menu_keyboard()):
            await callback.answer("Обновлено")
        else:
            await callback.answer("Уже обновлено!")
