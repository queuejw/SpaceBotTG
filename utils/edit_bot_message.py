from aiogram.exceptions import TelegramBadRequest, TelegramRetryAfter
from aiogram.types import InlineKeyboardMarkup

from bot.bot_data import bot


async def edit_text(chat_id: int, message_id: int, new_text: str, old_text: str,
                    reply_markup: InlineKeyboardMarkup) -> bool:
    if new_text == old_text:
        print("Текст не изменился")
        return False
    try:
        await bot.edit_message_text(chat_id=chat_id,
                                    message_id=message_id,
                                    text=new_text,
                                    reply_markup=reply_markup)
        print(f"Текст в чате {chat_id} успешно обновлен")
        return True
    except TelegramBadRequest:
        print("Ошибка при изменении сообщения склада: TelegramBadRequest")
        return False
    except TelegramRetryAfter:
        print("Ошибка при изменении сообщения склада: TelegramRetryAfter")
        return False
