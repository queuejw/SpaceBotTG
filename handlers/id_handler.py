# Выводит id пользователя
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router()


@router.message(Command("id"))
async def send_user_id(message: Message):
    await message.reply(f"Ваш ID: {message.from_user.id}")
