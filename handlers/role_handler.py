from types import NoneType

from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from bot.messages import send_message
from bot.shared import exist_user_by_name, exist_user_by_id, can_proceed, get_user_by_id, all_ships, get_user_by_name
from utils.roles import get_normal_role, get_role_name_by_num
from utils.util import is_it_int

router = Router()


@router.message(Command("роль"))
async def set_role(message: Message, command: CommandObject):
    chat_id = message.chat.id
    if not await can_proceed(message):
        return
    if message.from_user.id != all_ships[chat_id]['crew'][0]['user_id']:
        await send_message(chat_id, "Только капитан может изменять роли.")
        return
    if type(command.args) == NoneType:
        print("NoneType, невозможно изменить роль")
        await send_message(chat_id, "⚠️ Укажите ID или Имя игрока, а также его новую роль.")
        return
    args = command.args.split()
    if len(args) != 2:
        await send_message(chat_id, "⚠️ Вы ошиблись с вводом команды. Попробуйте ещё раз.")
        return

    user_id_name = args[0]

    is_user_exist: bool
    is_it_user_id: bool
    if not is_it_int(user_id_name):
        print("получено имя пользователя, сверяем")
        is_user_exist = exist_user_by_name(chat_id, user_id_name)
        is_it_user_id = False
    else:
        print("получен id пользователя, сверяем")
        is_user_exist = exist_user_by_id(chat_id, int(user_id_name))
        is_it_user_id = True

    if not is_user_exist:
        await send_message(chat_id, "⚠️ Выбранный игрок не существует. Убедитесь, что вы верно ввели его ID или Имя.")
        return

    print(args[1])
    new_role = get_normal_role(args[1])
    if new_role == -1:
        await send_message(chat_id, "⚠️ Указана неверная роль. Попробуйте ещё раз.")
        return

    player: dict = get_user_by_id(chat_id, int(user_id_name)) if is_it_user_id else get_user_by_name(chat_id,
                                                                                                     user_id_name)

    if player == all_ships[chat_id]['crew'][0]:
        print("Капитан хочет изменить себя. Сброс.")
        await send_message(chat_id,
                           "❌ Капитан не может изменить свою роль, но Вы можете передать роль Капитана другому участнику.")
        return

    data: list = all_ships[chat_id]['crew']

    old_role_name = get_role_name_by_num(int(player['user_role']))
    new_role_name = get_role_name_by_num(new_role)

    if new_role == 1:
        print("Обмен ролями")
        current_captain = data[0]
        player_index = data.index(player)
        current_captain['user_role'] = 0
        player['user_role'] = new_role
        data[0] = player
        data[player_index] = current_captain

        await send_message(chat_id,
                           f"Встречайте нового капитана - {player['user_name']} 👑.\n{current_captain['user_name']} больше не капитан корабля.")
    else:
        player_index = data.index(player)
        player['user_role'] = new_role
        data[player_index] = player
        await send_message(chat_id,
                           f"Роль игрока {player['user_name']} была изменена с {old_role_name} на {new_role_name} ✅")

    all_ships[chat_id]['crew'] = data
