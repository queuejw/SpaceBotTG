from aiogram.exceptions import TelegramBadRequest, TelegramRetryAfter

from bot.bot_data import bot


async def delete_message(chat_id: int, message_id: int):
    try:
        await bot.delete_message(chat_id, message_id)
    except TelegramBadRequest as e:
        print(f"Не получилось удалить сообщение. Это всё, что нам известно: {e}")


async def send_message(chat_id: int, message: str):
    try:
        await bot.send_message(chat_id, message)
    except TelegramRetryAfter as e:
        print(f"Сервера Telegram сгорели, не удалось отправить сообщение. Это всё, что нам известно: {e}")
