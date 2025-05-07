from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from bot.shared import can_proceed
from utils.game_keyboards import get_main_menu_keyboard

router = Router()


@router.message(Command("menu", "меню"))
async def send_menu(message: Message):
    if not await can_proceed(message):
        return
    await message.answer("Меню бортового компьютера 🖥",
                         reply_markup=get_main_menu_keyboard())
