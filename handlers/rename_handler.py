from aiogram import Router
from aiogram.filters import CommandObject, Command
from aiogram.types import Message

from bot.shared import all_ships, is_chat_active, is_actions_blocked

router = Router()


# Проверка доступности названия корабля
def check_name(new_name: str) -> bool:
    ships = list(all_ships.items())
    for ship in ships:
        if ship[1]['ship_name'] == new_name:
            return False
    return True


# Команда для переименования корабля
@router.message(Command("название"))
async def change_ship_name(message: Message, command: CommandObject):
    chat_id = message.chat.id
    if not is_chat_active(chat_id):
        await message.answer(
            "Не получилось отправить команду\nНет соединения с кораблем. ⚠️\nПопробуйте ввести команду /играть")
        return
    if is_actions_blocked(chat_id):
        await message.answer("Подождите, пока не будет выполнена другая задача. ⚠️")
        return
    # Только капитан может сделать это
    if message.from_user.id != all_ships[chat_id]['crew'][0]['user_id']:
        await message.answer("Только капитан может изменить название корабля ⚠️")
        return
    # Если аргументов нет, то мы не можем переименовать корабль
    if command.args is None:
        await message.answer("Не получилось отправить команду\nВы не указали новое название корабля⚠️")
        return
    # Пробуем переименовать
    try:
        name = command.args
        if not check_name(name):
            # Название занято
            await message.answer("Это название уже занято ⚠️\nПопробуйте другое")
            return

        if len(name) > 20:
            await message.answer("Не удалось изменить название\nНазвание слишком длинное⚠️")
            return
        all_ships[chat_id]["ship_name"] = name
        await message.answer(f"Название корабля изменено на: {name} ")
    except ValueError:
        await message.answer("Не удалось изменить название\nПри передаче данных связь была потеряна⚠️")
        return
