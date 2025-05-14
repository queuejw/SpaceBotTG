from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from bot.messages import send_message
from bot.shared import can_proceed
from utils.menu_reply_markup import get_main_menu_reply_markup

router = Router()


@router.message(Command("menu", "меню"))
async def send_menu(message: Message):
    if not await can_proceed(message):
        return
    await send_message(message.chat.id, "Меню бортового компьютера 🖥",
                       reply_markup=get_main_menu_reply_markup(message.chat.id, message.from_user.id))
