from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from bot.messages import send_message
from bot.save_game import check_and_save_data
from bot.shared import can_proceed, all_ships, remove_chat_from_all_ships

router = Router()


@router.message(Command("пауза", "pause"))
async def pause_game(message: Message):
    chat_id = message.chat.id
    if not await can_proceed(message):
        return
    # Только капитан может сделать это
    if message.from_user.id != all_ships[chat_id]['crew'][0]['user_id']:
        await send_message(chat_id, "ℹ️ Только капитан может остановить игру.")
        return
    check_and_save_data(all_ships[chat_id], chat_id)
    remove_chat_from_all_ships(chat_id)
    await send_message(chat_id,
                       "Игра остановлена! ✅\nℹ️ Продолжить игру можно командой /играть (загрузится последнее сохранение)")
