from aiogram import Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from bot.bot_data import bot
from bot.messages import send_message
from bot.shared import is_chat_active, all_ships, exist_user_by_id
from utils.crew import get_default_crew
from utils.roles import get_normal_role, get_role_name_by_num

router = Router()


# Функция, которая позволяет добавить пользователя в список разрешенных пользователей
def add_user_to_white_list(user_id: int, chat_id: int, user_name: str, user_role: int) -> bool:
    if len(all_ships[chat_id]['crew']) > 1:
        # Возвращаем False, если капитан пытается добавить самого себя
        if user_id == all_ships[chat_id]['crew'][0]['user_id']:
            return False
    if not exist_user_by_id(chat_id, user_id):
        user = get_default_crew()
        user["user_name"] = user_name
        user["user_role"] = user_role
        user["user_id"] = user_id
        all_ships[chat_id]['crew'].append(user)
        return True
    return False


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
        await send_message(chat_id,
                           "Не удалось получить информацию о корабле:\nНет соединения. ⚠️\nПопробуйте ввести команду /играть")
        return
    # Только капитан может сделать это
    if message.from_user.id != all_ships[chat_id]['crew'][0]['user_id']:
        await send_message(chat_id, "Только капитан может добавить участников на борт ⚠️")
        return
    # Если аргументов нет, то мы не можем добавить участников
    if command.args is None:
        await send_message(chat_id, "Не получилось отправить команду\nВы не указали ID участника⚠️")
        return
    try:
        args = command.args.split()
        user_id = int(args[0])
        role = 0
        if len(args) > 1:
            role = get_normal_role(args[1])

        user = await bot.get_chat_member(chat_id, user_id)

        if add_user_to_white_list(user_id, chat_id, user.user.first_name, role):
            role_name = get_role_name_by_num(role)
            await send_message(chat_id, f"Успешно! {user.user.first_name} теперь {role_name} корабля. ✅")
        else:
            await send_message(chat_id, "Не получилось добавить нового игрока ⚠️")
    except ValueError:
        await send_message(chat_id, "Не получилось добавить нового игрока ⚠️")
    except TelegramBadRequest:
        await send_message(chat_id, "Компьютер не нашёл этого участника ⚠️")


@router.message(Command("удалить"))
async def del_user(message: Message, command: CommandObject):
    chat_id = message.chat.id
    if not is_chat_active(chat_id):
        await send_message(chat_id,
                           "Не удалось получить информацию о корабле:\nНет соединения. ⚠️\nПопробуйте ввести команду /играть")
        return
    # Только капитан может сделать это
    if message.from_user.id != all_ships[chat_id]['crew'][0]['user_id']:
        await send_message(chat_id, "Только капитан может удалить участников ⚠️")
        return
    # Если аргументов нет, то мы не можем удалить участников
    if command.args is None:
        await send_message(chat_id, "Не получилось отправить команду\nВы не указали ID участника ⚠️")
        return
    if exist_user_by_id(chat_id, int(command.args)):
        try:
            if del_user_from_white_list(int(command.args), chat_id):
                await send_message(chat_id, "Успешно! Член экипажа выброшен в открытый космос. ✅")
            else:
                await send_message(chat_id, "Капитан не может удалить самого себя ⚠️")
        except ValueError:
            await send_message(chat_id, "Не удалось удалить члена экипажа ⚠️")

    else:
        await send_message(chat_id, "Не удалось удалить члена экипажа ⚠️\nПерепроверьте ID")
