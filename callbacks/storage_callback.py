from aiogram import Router, F
from aiogram.types import CallbackQuery

from bot.shared import is_chat_active, exist_user_by_id
from bot.text import get_storage_text
from utils.edit_bot_message import edit_text
from utils.keyboards import get_storage_inline_keyboard

router = Router()


@router.callback_query(F.data == "update_storage_text")
async def update_storage_text(callback: CallbackQuery):
    print("Обновляем текст склада")
    chat_id = callback.message.chat.id
    if not is_chat_active(chat_id):
        await callback.answer("Игра не активна")
        return
    if not exist_user_by_id(chat_id, callback.from_user.id):
        await callback.answer("Вы не член экипажа")
        return
    if edit_text(chat_id, callback.message.message_id, get_storage_text(chat_id), callback.message.text,
                 get_storage_inline_keyboard()):
        await callback.answer("Обновлено")
    else:
        print(f"Текст склада в чате {chat_id} совпадает с прошлым")
        await callback.answer("Уже обновлено.")
