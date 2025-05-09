# Все, что связано с игрой

import asyncio
import random
from types import NoneType

from bot import chat_utils
from bot.bot_data import bot
from bot.messages import send_message
from bot.save_game import check_data
from bot.shared import all_ships, is_chat_active, damage_all_crew, remove_chat_from_all_ships
from utils.keyboards import get_fire_inline_keyboard


# Механика пожаров
async def fire_func(chat_id: int):
    await bot.send_message(chat_id, "🔥Корабль горит!🔥", reply_markup=get_fire_inline_keyboard())
    if all_ships[chat_id]['connected_chat'] != 'null':
        # Уведомляем соединенный чат о пожаре на корабле
        c_chat_id = int(all_ships[chat_id]['connected_chat'])
        if is_chat_active(c_chat_id):
            chat = await bot.get_chat(chat_id)
            if type(chat.title) != NoneType:
                await send_message(c_chat_id,
                                   f"Корабль {all_ships[chat_id]['ship_name']} чата {chat.title} горит!")
            else:
                await send_message(c_chat_id,
                                   f"Корабль {all_ships[chat_id]['ship_name']} горит!")

    while True:
        if not is_chat_active(chat_id):
            break
        if not all_ships[chat_id]["fire"]:
            break
        # Если прочность корабля на нуле завершаем пожар
        if int(all_ships[chat_id]["ship_health"]) < 1:
            break

        if random.random() > 0.15:
            all_ships[chat_id]["ship_fuel"] -= random.randint(5, 10)
        if random.random() > 0.25:
            all_ships[chat_id]["resources"] -= random.randint(5, 10)
        if random.random() > 0.25:
            all_ships[chat_id]["ship_health"] -= random.randint(5, 10)
        if random.random() > 0.25:
            damage_all_crew(chat_id, 1, 5)
        if random.random() > 0.25:
            all_ships[chat_id]["oxygen"] -= random.randint(2, 5)

        await destroy_engine(chat_id, 0.05)
        await destroy_fuel_tank(chat_id, 0.05)
        await destroy_radio(chat_id, 0.05)

        check_data(all_ships[chat_id], chat_id)

        await asyncio.sleep(3)


# Функция для повреждения двигателя
async def destroy_engine(chat_id: int, chance: float) -> bool:
    # Если повезет, то ломаем двигатель
    if random.random() < chance and not all_ships[chat_id]["engine_damaged"]:
        all_ships[chat_id]["engine_damaged"] = True
        await send_message(chat_id, "Двигатель поврежден, максимальная скорость снижена! ⚠️")
        return True
    return False


# Функция для повреждения топливного бака
async def destroy_fuel_tank(chat_id: int, chance: float) -> bool:
    # Если повезет, то ломаем бак
    if random.random() < chance and not all_ships[chat_id]["fuel_tank_damaged"]:
        all_ships[chat_id]["fuel_tank_damaged"] = True
        await send_message(chat_id, "Пробит топливный бак! ⚠️")
        return True
    return False


# Функция для повреждения орудия
async def destroy_cannon(chat_id: int, chance: float) -> bool:
    # Если повезет, то ломаем орудие
    if random.random() < chance and not all_ships[chat_id]["cannon_damaged"]:
        all_ships[chat_id]["cannon_damaged"] = True
        await send_message(chat_id, "Орудие повреждено, точность стрельбы снижена! ⚠️")
        return True
    return False


# Функция для повреждения радио (связи)
async def destroy_radio(chat_id: int, chance: float) -> bool:
    # Если повезет, то ломаем орудие
    if random.random() < chance and not all_ships[chat_id]["radio_damaged"]:
        all_ships[chat_id]["radio_damaged"] = True
        await send_message(chat_id, "Радиостанция повреждена, качество связи снижено! ⚠️")
        return True
    return False


# Останавливает игру и удаляет файл сохранения
def stop_game(chat_id: int):
    remove_chat_from_all_ships(chat_id)
    chat_utils.delete_chat_state(chat_id)
