from types import NoneType

from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from bot.bot_utils import save_config
from bot.config import ADMINS, CONFIG, BLOCKED_CHATS
from bot.game_functions import fire_func, stop_game
from bot.shared import all_ships, is_chat_active

router = Router()


def is_it_admin(user_id: int) -> bool:
    return user_id in ADMINS


# Команда администратора. Блокирует чат
@router.message(Command("adm:заблокировать"))
async def adm_block(message: Message, command: CommandObject):
    if not is_it_admin(message.from_user.id):
        return
    if type(command.args) == NoneType:
        await message.answer("Вы не указали ID.")
        return
    try:
        chat = int(command.args)
        BLOCKED_CHATS.append(chat)
        CONFIG['blacklist'] = BLOCKED_CHATS
        stop_game(chat)
        save_config(CONFIG)
        await message.answer(f"Чат {chat} заблокирован ✅")
    except ValueError as e:
        print(f"Не удалось заблокировать чат: {e} ")
        await message.answer(f"Не получилось заблокировать чат 🚫\n{e}")


# Команда администратора. Разблокирует чат
@router.message(Command("adm:разблокировать"))
async def adm_unlock(message: Message, command: CommandObject):
    if not is_it_admin(message.from_user.id):
        return
    if type(command.args) == NoneType:
        await message.answer("Вы не указали ID.")
        return
    try:
        chat = int(command.args)
        BLOCKED_CHATS.remove(chat)
        CONFIG['blacklist'] = BLOCKED_CHATS
        save_config(CONFIG)
        await message.answer(f"Чат {chat} разблокирован ✅")
    except ValueError as e:
        print(f"Не удалось разблокировать чат: {e} ")
        await message.answer(f"Не получилось разблокировать чат 🚫\n{e}")


@router.message(Command("adm:пожар"))
async def adm_fire(message: Message, command: CommandObject):
    if not is_it_admin(message.from_user.id):
        return
    if type(command.args) == NoneType:
        await message.answer("Вы не указали ID.")
        return
    try:
        chat = int(command.args)
        all_ships[chat]["fire"] = True
        await message.answer(f"Корабль в чате {chat} горит ✅")
        await fire_func(chat)
    except ValueError as e:
        print(f"Не получилось сжечь корабль : {e} ")
        await message.answer(f"Не получилось сжечь корабль 🚫\n{e}")


# Команда администратора. Останавливает игру в чате
@router.message(Command("adm:стоп"))
async def adm_stop(message: Message, command: CommandObject):
    if not is_it_admin(message.from_user.id):
        return
    if type(command.args) == NoneType:
        await message.answer("Вы не указали ID.")
        return
    try:
        chat = int(command.args)
        if is_chat_active(chat):
            stop_game(chat)
            await message.answer(f"Игра в чате {chat} остановлена ✅")
        else:
            await message.answer(f"Не получилось остановить игру в чате {chat} 🚫\nПроверьте ID.")
    except ValueError as e:
        await message.answer(f"Не получилось остановить игру в чате. 🚫\n{e}")
