# Функция для получения текста сообщения компьютера
from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest, TelegramRetryAfter
from aiogram.types import CallbackQuery

from bot.bot_data import bot
from bot.shared import is_chat_active, exist_user_by_id
from bot.text import get_computer_text
from utils.keyboards import get_computer_inline_keyboard

router = Router()


@router.callback_query(F.data == "update_computer_text")
async def update_computer_text(callback: CallbackQuery):
    print("Обновляем текст компьютера")
    chat_id = callback.message.chat.id
    if not is_chat_active(chat_id):
        await callback.answer()
        return
    if not exist_user_by_id(chat_id, callback.from_user.id):
        await callback.answer("Вы не член экипажа")
        return
    new_text = get_computer_text(chat_id)
    if callback.message.text != new_text:
        try:
            await callback.answer()
            await bot.edit_message_text(chat_id=chat_id,
                                        message_id=callback.message.message_id,
                                        text=new_text,
                                        reply_markup=get_computer_inline_keyboard())
            print(f"Текст компьютера в чате {chat_id} успешно обновлен")
        except TelegramBadRequest:
            print("Ошибка при изменении сообщения компьютера: TelegramBadRequest")
        except TelegramRetryAfter:
            print("Ошибка при изменении сообщения компьютера: TelegramRetryAfter")
    else:
        print(f"Текст компьютера в чате {chat_id} совпадает с прошлым")
        await callback.answer("Уже обновлено.")
