import asyncio
import random

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from bot.messages import send_message
from bot.save_game import check_data
from bot.shared import all_ships, can_proceed, get_user_by_id
from utils.check_role import check_role

router = Router()


# Ремонт корабля
async def repair(chat_id: int, sec: int):
    # блокируем действия на время ремонта и обновляем данные
    all_ships[chat_id]["blocked"] = True
    is_it_captain = sec > 7
    # уведомляем игроков
    await send_message(chat_id, "Ремонтируем корабль ...")
    for _ in range(sec):
        if (all_ships[chat_id]["resources"] - 25) < 1:
            break
        if all_ships[chat_id]["ship_health"] > 99:
            break
        all_ships[chat_id]["resources"] -= 25
        if not is_it_captain:
            all_ships[chat_id]["ship_health"] += random.randint(5, 10)
            all_ships[chat_id]["oxygen"] += random.randint(2, 5)
        else:
            all_ships[chat_id]["ship_health"] += random.randint(2, 5)
            all_ships[chat_id]["oxygen"] += random.randint(1, 3)
        await asyncio.sleep(1)
    # Отменяем блокировку действий
    all_ships[chat_id]["blocked"] = False
    # Ремонтируем корабль и проверяем данные
    all_ships[chat_id]['engine_damaged'] = False
    all_ships[chat_id]['fuel_tank_damaged'] = False
    all_ships[chat_id]['cannon_damaged'] = False
    all_ships[chat_id]['air_leaking'] = False
    check_data(all_ships[chat_id], chat_id)
    await send_message(chat_id, "Ремонт завершён")


# Функция для проверки корабля на наличие повреждений
def is_ship_damaged(ship: dict) -> bool:
    return ship['air_leaking'] or ship['engine_damaged'] or ship['fuel_tank_damaged'] or ship['cannon_damaged']


# Ремонт корабля
@router.message(Command("ремонт", "чинить"))
async def repair_ship(message: Message):
    chat_id = message.chat.id
    if not await can_proceed(message):
        return
    user_role = int(get_user_by_id(chat_id, message.from_user.id)['user_role'])
    if check_role(2, chat_id, message.from_user.id):
        await send_message(chat_id, "⚠️ Только инженер или капитан может ремонтировать корабль")
        return
    if all_ships[chat_id]['ship_health'] > 99 and not is_ship_damaged(all_ships[chat_id]):
        await message.answer("Ремонт не требуется.")
        return
    time = random.randint(5, 7) if user_role != 1 else random.randint(8, 15)
    await repair(chat_id, time)
