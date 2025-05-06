from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from bot.messages import send_message
from bot.shared import can_proceed
from utils.check_role import check_role
from utils.keyboards import get_craft_keyboard

router = Router()


# Команда для создания предметов
@router.message(Command("создание", "крафт"))
async def craft(message: Message):
    if not await can_proceed(message):
        return
    chat_id = message.chat.id
    if check_role(2, chat_id, message.from_user.id):
        await send_message(chat_id, "⚠️ Только инженер или капитан может создавать предметы")
        return
    await message.answer("Выберите предмет для создания 🛠",
                         reply_markup=get_craft_keyboard())
