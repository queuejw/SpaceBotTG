from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from bot.shared import is_chat_active, all_ships
from utils.keyboards import get_self_destruction_inline_keyboard

router = Router()


# Команда самоуничтожения
@router.message(Command("самоуничтожение", "ликвидация"))
async def self_destruction_command(message: Message):
    chat_id = message.chat.id
    if not is_chat_active(chat_id):
        await message.answer("Не получилось отправить команду самоуничтожение\nНет соединения. ⚠️")
        return
    if message.from_user.id != all_ships[chat_id]['crew'][0]['user_id']:
        await message.answer("Только капитан может сделать это ⚠️")
        return
    await message.answer("ВЫ УВЕРЕНЫ В ТОМ, ЧТО ХОТИТЕ СДЕЛАТЬ ЭТО ?:",
                         reply_markup=get_self_destruction_inline_keyboard())
