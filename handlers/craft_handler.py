from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from bot.messages import send_message
from bot.shared import can_proceed, get_user_by_id
from utils.keyboards import get_craft_keyboard

router = Router()


# Команда для создания предметов
@router.message(Command("создание", "крафт"))
async def craft(message: Message):
    if not await can_proceed(message):
        return
    chat_id = message.chat.id
    role = int(get_user_by_id(chat_id, message.from_user.id)['user_role'])
    if role != 2 and role != 1:
        await send_message(chat_id, "⚠️ Только инженер или капитан может создавать предметы")
        return
    await message.answer("Выберите предмет для создания 🛠",
                         reply_markup=get_craft_keyboard())
