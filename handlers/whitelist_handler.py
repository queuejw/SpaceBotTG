from aiogram import Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from bot.bot_data import bot
from bot.shared import is_chat_active, all_ships, exist_user_by_id
from utils.crew import get_default_crew

router = Router()


# Функция, которая позволяет добавить пользователя в список разрешенных пользователей
def add_user_to_white_list(user_id: int, chat_id: int, user_name: str, user_role: int) -> bool:
    if len(all_ships[chat_id]['crew']) > 1:
        # Возвращаем False, если капитан пытается добавить самого себя
        if user_id == all_ships[chat_id]['crew'][0]['user_id']:
            return False
    captain = get_default_crew()
    captain["user_name"] = user_name
    captain["user_role"] = user_role
    captain["user_id"] = user_id
    all_ships[chat_id]['crew'].append(captain)
    return True


# Функция, которая позволяет удалить пользователя из списка разрешенных пользователей
def del_user_from_white_list(user_id: int, chat_id: int) -> bool:
    if len(all_ships[chat_id]['crew']) > 1:
        # Возвращаем False, если капитан пытается удалить самого себя
        if user_id == all_ships[chat_id]['crew'][0]['user_id']:
            return False
        for i in all_ships[chat_id]['crew']:
            if i['user_id'] == user_id:
                all_ships[chat_id]['crew'].remove(i)
                return True
    return False


@router.message(Command("добавить"))
async def add_user(message: Message, command: CommandObject):
    chat_id = message.chat.id
    if not is_chat_active(chat_id):
        await message.answer(
            "Не удалось получить информацию о корабле:\nНет соединения. ⚠️\nПопробуйте ввести команду /играть")
        return
    # Только капитан может сделать это
    if message.from_user.id != all_ships[chat_id]['crew'][0]['user_id']:
        await message.answer("Только капитан может добавить участников на борт ⚠️")
        return
    # Если аргументов нет, то мы не можем добавить участников
    if command.args is None:
        await message.answer("Не получилось отправить команду\nВы не указали ID участника⚠️")
        return
    try:
        user = await bot.get_chat_member(chat_id, int(command.args))
        if add_user_to_white_list(int(command.args), chat_id, user.user.first_name, 0):
            await message.answer(f"Успешно! {user.user.first_name} теперь член экипажа корабля. ✅")
        else:
            await message.answer("Не получилось добавить нового игрока ⚠️")
    except ValueError:
        await message.answer("Не получилось добавить нового игрока ⚠️")
    except TelegramBadRequest:
        await message.answer("Компьютер не нашёл этого участника ⚠️")


@router.message(Command("удалить"))
async def del_user(message: Message, command: CommandObject):
    chat_id = message.chat.id
    if not is_chat_active(chat_id):
        await message.answer(
            "Не удалось получить информацию о корабле:\nНет соединения. ⚠️\nПопробуйте ввести команду /играть")
        return
    # Только капитан может сделать это
    if message.from_user.id != all_ships[chat_id]['crew'][0]['user_id']:
        await message.answer("Только капитан может удалить участников ⚠️")
        return
    # Если аргументов нет, то мы не можем удалить участников
    if command.args is None:
        await message.answer("Не получилось отправить команду\nВы не указали ID участника ⚠️")
        return
    if exist_user_by_id(chat_id, int(command.args)):
        try:
            if del_user_from_white_list(int(command.args), chat_id):
                await message.answer("Успешно! Член экипажа выброшен в открытый космос. ✅")
            else:
                await message.answer("Капитан не может удалить самого себя ⚠️")
        except ValueError:
            await message.answer("Не удалось удалить члена экипажа ⚠️")

    else:
        await message.answer("Не удалось удалить члена экипажа ⚠️\nПерепроверьте ID")
