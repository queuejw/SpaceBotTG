import asyncio
import random
from types import NoneType

from aiogram import Router
from aiogram.exceptions import TelegramRetryAfter
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from bot.bot_data import bot
from bot.messages import send_message
from bot.shared import all_ships, is_chat_active, can_proceed, is_chat_banned
from utils.check_role import check_role

router = Router()


# Функция для получения случайного chat id
def get_random_chat_id(my_chat_id: int):
    items = list(all_ships.items())
    if len(items) < 2:
        return my_chat_id
    r_ship = random.choice(items)
    r_chat_id = r_ship[0]
    if my_chat_id == r_chat_id:
        get_random_chat_id(my_chat_id)
        return None
    else:
        return int(r_chat_id)


# Соединение с кораблем
async def connection(random_chat_id: int, chat_id: int, my_chat_title, args, user_id: int):
    if random_chat_id == chat_id:
        await send_message(chat_id, f"Не удалось найти ближайший корабль. Попробуйте позже.")
        return
    if not is_chat_active(random_chat_id):
        print("чат не активен, попытка соединиться ещё раз")
        await connect(chat_id, my_chat_title, args, user_id)
        return
    if all_ships[random_chat_id]['connected_chat'] != 'null':
        await send_message(chat_id,
                           f"Не удалось подключиться к выбранному кораблю. Попробуйте установить связь ещё раз.")
        return

    all_ships[chat_id]['connected_chat'] = f'{random_chat_id}'
    all_ships[random_chat_id]['connected_chat'] = f'{chat_id}'

    print(f"выбран чат {random_chat_id} , отправляю сообщения")
    random_chat = await bot.get_chat(random_chat_id)

    if type(random_chat.title) != NoneType:
        r_chat_name = random_chat.title
        await send_message(chat_id,
                           f"Установлена связь с кораблём {all_ships[random_chat_id]['ship_name']} чата {r_chat_name}\nЧтобы отключиться, введите /!связь")
    else:
        await send_message(chat_id,
                           f"Установлена связь с кораблём {all_ships[random_chat_id]['ship_name']}\nЧтобы отключиться, введите /!связь")

    if type(my_chat_title) != NoneType:
        chat_name = my_chat_title
        await send_message(random_chat_id,
                           f"Мы поймали связь с кораблём {all_ships[chat_id]['ship_name']} чата {chat_name}\nЧтобы отключиться, введите /!связь")
    else:
        await send_message(random_chat_id,
                           f"Мы поймали связь с кораблём {all_ships[chat_id]['ship_name']}\nЧтобы отключиться, введите /!связь")


# Сбрасывает параметры соединения с другим кораблем
def reset_connection(chat_id: int):
    all_ships[chat_id]['connected_chat'] = 'null'
    all_ships[chat_id]['blocked'] = False


# Подготовка к соединению с кораблем, либо отправка сообщения
async def connect(chat_id: int, title, args, user_id: int):
    try:
        if type(args) == NoneType:
            # Связываемся со случайным кораблем
            if all_ships[chat_id]['connected_chat'] == 'null':
                if check_role(5, chat_id, user_id):
                    await send_message(chat_id, "⚠️ Только связист или капитан может установить соединение.")
                    return
                random_chat_id = get_random_chat_id(chat_id)
                if type(random_chat_id) == NoneType:
                    print("Не удалось подключиться, пробую ещё раз")
                    await connect(chat_id, title, args, user_id)
                    return
                await connection(random_chat_id, chat_id, title, args, user_id)

            else:
                await send_message(chat_id,
                                   f"Уже установлена связь с каким-то кораблём.\nЧтобы отключиться, введите /!связь")
        else:
            if all_ships[chat_id]['connected_chat'] == 'null':
                if check_role(5, chat_id, user_id):
                    await send_message(chat_id, "⚠️ Только связист или капитан может установить соединение.")
                    return
                ships_f = 0
                ships_f_id = -1
                ships = list(all_ships.items())
                for ship in ships:
                    if ship[1]['ship_name'] == args:
                        ships_f += 1
                        ships_f_id = int(ship[0])
                if ships_f != 1:
                    await send_message(chat_id,
                                       "Не получилось подключиться к выбранному кораблю ⚠️")
                else:
                    await connection(ships_f_id, chat_id, title, args, user_id)


            # или передаем сообщения
            else:
                all_ships[chat_id]['blocked'] = True
                connected_chat_id = int(all_ships[chat_id]['connected_chat'])
                if connected_chat_id == chat_id:
                    reset_connection(chat_id)
                    await send_message(connected_chat_id, f"Не удалось найти ближайший корабль. Попробуйте позже.")
                    return
                if is_chat_banned(connected_chat_id):
                    reset_connection(chat_id)
                    await send_message(chat_id,
                                       f"Не удалось соединиться с кораблём. Выбранный корабль был заблокирован.")
                    return
                if not is_chat_active(connected_chat_id):
                    reset_connection(chat_id)
                    await send_message(chat_id, f"Не удалось соединиться с кораблём. Соединение прервано")
                    return
                if all_ships[connected_chat_id]['connected_chat'] != f'{chat_id}':
                    reset_connection(chat_id)
                    await send_message(chat_id,
                                       f"Не удалось подключиться к выбранному кораблю. Попробуйте установить связь ещё раз.")
                    return
                try:
                    await send_message(connected_chat_id, f"Получено сообщение: {args}")
                    await send_message(chat_id, f"Отправлено сообщение: {args}")
                except TelegramRetryAfter:
                    print("Наверное Too Many Requests. ")
                    all_ships[chat_id]['blocked'] = False

                await asyncio.sleep(2)
                all_ships[chat_id]['blocked'] = False

    except ValueError:
        await send_message(chat_id, "Не удалось связаться с кораблём.\nПри передаче данных связь была потеряна⚠️")


# Команда для связи с другими кораблями
@router.message(Command("связь", "с"))
async def connect_to_other_ship(message: Message, command: CommandObject):
    chat_id = message.chat.id
    if not await can_proceed(message):
        return
    await connect(chat_id, message.chat.title, command.args, message.from_user.id)


@router.message(Command("!связь", "!с"))
async def disconnect_from_other_ship(message: Message):
    chat_id = message.chat.id
    if not await can_proceed(message):
        return
    if all_ships[chat_id]['connected_chat'] != 'null':
        connected_chat_id = int(all_ships[chat_id]['connected_chat'])
        if not is_chat_active(connected_chat_id):
            all_ships[chat_id]['connected_chat'] = 'null'
            await send_message(chat_id, f"Мы успешно отключились от другого корабля.")
            return
        connected_chat = await bot.get_chat(connected_chat_id)
        all_ships[chat_id]['connected_chat'] = 'null'
        chat_name = connected_chat.title
        if type(chat_name) != NoneType:
            await send_message(chat_id,
                               f"Мы отключились от корабля {all_ships[connected_chat_id]['ship_name']} чата {chat_name}")
        else:
            await send_message(chat_id,
                               f"Мы отключились от корабля {all_ships[connected_chat_id]['ship_name']}")

        if all_ships[connected_chat_id]["connected_chat"] == f'{chat_id}':
            all_ships[connected_chat_id]['connected_chat'] = 'null'
            if type(message.chat.title) != NoneType:
                chat_name = message.chat.title
                await send_message(connected_chat_id,
                                   f"Корабль {all_ships[chat_id]["ship_name"]} чата {chat_name} отключился от нас.")
            else:
                await send_message(connected_chat_id,
                                   f"Корабль {all_ships[chat_id]["ship_name"]} отключился от нас.")
    else:
        await send_message(chat_id, "Мы уже отключились от другого корабля ⚠️")
