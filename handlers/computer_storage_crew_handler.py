from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from bot.messages import send_message
from bot.shared import get_crew_text, exist_user_by_name, can_proceed, exist_user_by_id
from bot.text import get_specific_crew_text, get_computer_text, get_storage_text
from utils.keyboards import get_computer_inline_keyboard, get_storage_inline_keyboard
from utils.util import is_it_int

router = Router()


# Выводит информацию о корабле чата
@router.message(Command("компьютер", "к"))
async def computer(message: Message):
    chat_id = message.chat.id
    if not await can_proceed(message):
        return
    text = get_computer_text(chat_id)
    await message.answer(text, reply_markup=get_computer_inline_keyboard())


# Выводит информацию о предметах на складе
@router.message(Command("склад"))
async def storage(message: Message):
    chat_id = message.chat.id
    if not await can_proceed(message):
        return

    await message.answer(get_storage_text(chat_id), reply_markup=get_storage_inline_keyboard())


# Выводит список игроков либо информацию о конкретном игроке
@router.message(Command("экипаж", "э"))
async def crew(message: Message, command: CommandObject):
    chat_id = message.chat.id
    if not await can_proceed(message):
        return
    # Если ник не был указан, то отправляем список участников
    if command.args is None:
        text = get_crew_text(chat_id)
        await send_message(chat_id, text)
    else:
        # Проверяем, что данный пользователь существует и отправляем сообщение
        value: bool
        if not is_it_int(command.args):
            value = exist_user_by_name(chat_id, command.args)
        else:
            value = exist_user_by_id(chat_id, int(command.args))

        text = get_specific_crew_text(chat_id, command.args) if not is_it_int(command.args) else get_specific_crew_text(
            chat_id, int(command.args))
        if value:
            await send_message(chat_id, text)
        else:
            await send_message(chat_id, text + "Возможно, вы ошиблись с вводом имени или id члена экипажа.")


# Выводит информацию об игроке, который ввел эту команду
@router.message(Command("я"))
async def about_me(message: Message):
    chat_id = message.chat.id
    if not await can_proceed(message):
        return
    text = get_specific_crew_text(chat_id, message.from_user.id)
    await send_message(chat_id, text)
