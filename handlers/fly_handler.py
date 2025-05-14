import asyncio
import random

from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from bot.config import PLANETS
from bot.messages import send_message
from bot.shared import all_ships, is_chat_active, can_proceed
from utils.check_role import check_role
from utils.connection_utils import send_notification_to_connected_chat

router = Router()


# Функция для имитирования полета
async def fly(chat_id: int, planet_name: str):
    if not is_chat_active(chat_id):
        return
    if all_ships[chat_id]["on_planet"]:
        await send_message(chat_id,
                           "Чтобы улететь на другую планету, нужно покинуть текущую.\nПопробуйте ввести команду /покинуть")
        return
    if all_ships[chat_id]["ship_fuel"] < 1:
        await send_message(chat_id, "Недостаточно топлива!️⚠️")
        return
    # случайное время для ожидания
    time = random.randint(5, 10) if not all_ships[chat_id]['engine_damaged'] else random.randint(10, 25)
    # блокируем действия на время полета и обновляем данные
    all_ships[chat_id]["blocked"] = True
    # уведомляем игроков
    await send_message(chat_id, f"Посадка на планету {planet_name} через {time} секунд")
    await asyncio.sleep(time)
    if not is_chat_active(chat_id):
        return
    # обновляем данные и отменяем блокировку действий
    all_ships[chat_id]["on_planet"] = True
    all_ships[chat_id]["blocked"] = False
    all_ships[chat_id]["planet_name"] = planet_name
    all_ships[chat_id]["previous_planet_name"] = planet_name
    await send_message(chat_id, f"Успешная посадка на планету {planet_name} ")
    await send_notification_to_connected_chat(f"летит на планету {planet_name}", chat_id)


# Команда для посадки, полета на планету
@router.message(Command("лететь"))
async def fly_command(message: Message, command: CommandObject):
    chat_id = message.chat.id
    if not await can_proceed(message):
        return
    if check_role(4, chat_id, message.from_user.id):
        await send_message(chat_id, "⚠️ Только пилот или капитан может управлять кораблём")
        return
    # Если аргументов нет, то летим на ближайшую (следующую) планету
    name = command.args
    if name is None:
        await fly(chat_id, all_ships[chat_id]['next_planet_name'])
    else:
        if len(name) > 20:
            await message.answer("Название планеты слишком длинное⚠️")
            return

        await fly(chat_id, name)


# Функция взлёта с планета
async def leave_planet(chat_id: int):
    if not is_chat_active(chat_id):
        return
    if not all_ships[chat_id]["on_planet"]:
        await send_message(chat_id, "Невозможно покинуть планету\nВы не на планете")
        return
    if all_ships[chat_id]["ship_fuel"] < 1:
        await send_message(chat_id, "Недостаточно топлива!️⚠️")
        return
    # случайное время для ожидания
    time = random.randint(5, 10) if not all_ships[chat_id]['engine_damaged'] else random.randint(10, 25)
    # блокируем действия на время полета и обновляем данные
    all_ships[chat_id]["blocked"] = True
    # уведомляем игроков
    await send_message(chat_id, f"Покидаем планету {all_ships[chat_id]["planet_name"]} через {time} секунд")
    await asyncio.sleep(time)
    if not is_chat_active(chat_id):
        return
    # обновляем данные и отменяем блокировку действий
    all_ships[chat_id]["on_planet"] = False
    all_ships[chat_id]["blocked"] = False
    if all_ships[chat_id]['meteorite_fall']:
        all_ships[chat_id]['meteorite_fall'] = False
    all_ships[chat_id]["previous_planet_name"] = all_ships[chat_id]["planet_name"]
    all_ships[chat_id]["next_planet_name"] = random.choice(PLANETS)
    await send_message(chat_id, f"Мы покинули планету {all_ships[chat_id]["previous_planet_name"]}")
    await send_notification_to_connected_chat(f"покинул планету {all_ships[chat_id]["previous_planet_name"]}", chat_id)


# Команда, чтобы покинуть планету
@router.message(Command("покинуть"))
async def leave_planet_command(message: Message):
    chat_id = message.chat.id
    if not await can_proceed(message):
        return
    if check_role(4, chat_id, message.from_user.id):
        await send_message(chat_id, "⚠️ Только пилот или капитан может управлять кораблём")
        return
    await leave_planet(chat_id)
