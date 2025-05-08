from aiogram.exceptions import TelegramBadRequest, TelegramRetryAfter
from aiogram.types import InlineKeyboardMarkup

from bot.bot_data import bot


async def edit_text(chat_id: int, message_id: int, new_text: str, old_text: str,
                    reply_markup: InlineKeyboardMarkup | None) -> bool:
    if new_text == old_text:
        return False
    try:
        await bot.edit_message_text(chat_id=chat_id,
                                    message_id=message_id,
                                    text=new_text,
                                    reply_markup=reply_markup)
        return True
    except TelegramBadRequest:
        print("Ошибка при изменении сообщения: TelegramBadRequest")
        return False
    except TelegramRetryAfter:
        print("Ошибка при изменении сообщения: TelegramRetryAfter")
        return False
