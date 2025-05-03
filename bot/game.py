# Код игры, который выполняется всё время, пока активна игра или действует какое-то событие
import asyncio
import random
from types import NoneType

from bot.bot_data import bot
from bot.check_crew import check_all_crew
from bot.config import PLANETS
from bot.game_functions import fire_func, destroy_engine, destroy_fuel_tank, destroy_cannon, stop_game
from bot.messages import send_message
from bot.save_game import check_and_save_data, check_data
from bot.shared import is_chat_active, all_ships, damage_all_crew, is_crew_alive
from utils.util import clamp


# Изменение планет и сброс расстояния каждые 60 секунд
async def game_loop_planet_change(chat_id: int):
    while is_chat_active(chat_id):
        if not all_ships[chat_id]['on_planet']:
            all_ships[chat_id]['previous_planet_name'] = all_ships[chat_id]['next_planet_name']
            all_ships[chat_id]['next_planet_name'] = random.choice(PLANETS)
            all_ships[chat_id]["distance"] = 0
        # Сохраняем игру каждые 60 секунд
        check_and_save_data(all_ships[chat_id], chat_id)
        await asyncio.sleep(60)


# Атака пришельцев
async def alien_attack(chat_id: int):
    if all_ships[chat_id]['alien_attack']:
        return
    all_ships[chat_id]['alien_attack'] = True
    await send_message(chat_id, "⚠️ Нас атакуют пришельцы! 👽🛸\nОтбейте атаку при помощи команды:\n/выстрел")
    if all_ships[chat_id]['connected_chat'] != 'null':
        c_chat_id = int(all_ships[chat_id]['connected_chat'])
        if is_chat_active(c_chat_id):
            chat = await bot.get_chat(chat_id)
            if type(chat.title) != NoneType:
                await send_message(c_chat_id,
                                   f"Корабль {all_ships[chat_id]['ship_name']} чата {chat.title} атакуют пришельцы!")
            else:
                await send_message(c_chat_id,
                                   f"Корабль {all_ships[chat_id]['ship_name']} атакуют пришельцы!")
    while is_chat_active(chat_id) and all_ships[chat_id]['alien_attack']:
        if not all_ships[chat_id]['alien_attack']:
            return
        if int(all_ships[chat_id]['ship_health']) < 1:
            all_ships[chat_id]['alien_attack'] = False
            await send_message(chat_id, "Пришельцы улетели! 👽")
            break
        if random.random() < 0.2:
            all_ships[chat_id]['ship_health'] = clamp(all_ships[chat_id]['ship_health'] - random.randint(1, 10), 0, 100)
            await send_message(chat_id,
                               f"Пришельцы попали в нас 👽!\nПрочность корабля: {all_ships[chat_id]['ship_health']}%")
            if random.random() < 0.25 and not all_ships[chat_id]["fire"]:
                # Пожар от выстрела противника
                all_ships[chat_id]["fire"] = True
                await fire_func(chat_id)

            await destroy_engine(chat_id, 0.1)
            await destroy_fuel_tank(chat_id, 0.1)
            await destroy_cannon(chat_id, 0.1)

        await asyncio.sleep(5)


async def meteorite(chat_id: int):
    all_ships[chat_id]['meteorite_fall'] = True
    time = random.randint(15, 45)
    await send_message(chat_id,
                       f"☄️⚠️ Угроза падения метеорита. Срочно покиньте эту планету.\nДо столкновения осталось: {time} секунд.")
    meteorite_fall_active = True
    for i in range(time):
        if not all_ships[chat_id]['meteorite_fall']:
            await send_message(chat_id,
                               f"☄️✅ Вы избежали столкновения.")
            meteorite_fall_active = False
            break
        await asyncio.sleep(1)
    if not meteorite_fall_active:
        return
    await send_message(chat_id, f"☄️❌ Столкновение с метеоритом! 💥")
    await destroy_engine(chat_id, 0.75)
    await destroy_fuel_tank(chat_id, 0.75)
    await destroy_cannon(chat_id, 0.75)
    damage_all_crew(chat_id, 10, 30)
    all_ships[chat_id]["ship_health"] -= random.randint(10, 30)
    check_data(all_ships[chat_id], chat_id)
    await asyncio.sleep(1)
    if random.random() < 0.5:
        all_ships[chat_id]["fire"] = True
        await fire_func(chat_id)


# Создание случайных событий на планете или в космосе.
async def game_loop_events(chat_id: int):
    # Небольшая задержка в начале игры
    await asyncio.sleep(5)
    while is_chat_active(chat_id):
        if all_ships[chat_id]["on_planet"]:
            # события на планетах
            if random.random() < 0.15:
                # Ресурсы на планете
                value = random.randint(50, 150)
                all_ships[chat_id]["resources"] += value
                await send_message(chat_id, f"Мы нашли полезные ресурсы!\nПолучено {value} ресурсов")
            if random.random() < 0.08:
                # Буря
                text = "Буря на планете!\n"
                if all_ships[chat_id]['connected_chat'] != 'null':
                    all_ships[chat_id]['connected_chat'] = 'null'
                    text = text + "Связь потеряна.\n"

                value = random.randint(1, 5)
                all_ships[chat_id]["ship_health"] = clamp(all_ships[chat_id]["ship_health"] - value, 0, 100)
                text = text + f"Прочность корабля: {all_ships[chat_id]["ship_health"]}%"
                await send_message(chat_id, text)

            if random.random() < 0.06:
                # Аномалия на планете
                if not int(all_ships[chat_id]["ship_health"]) == 0:
                    value = random.randint(1, 5)
                    all_ships[chat_id]["ship_health"] = clamp(all_ships[chat_id]["ship_health"] - value, 0, 100)
                    await send_message(chat_id,
                                       f"✨⚡️ Аномалия на планете! Корабль поврежден!\nПрочность корабля: {all_ships[chat_id]["ship_health"]}%")
                    await destroy_engine(chat_id, 0.2)
            if random.random() < 0.04:
                # Падение метеорита
                if not int(all_ships[chat_id]["ship_health"]) == 0 and not all_ships[chat_id]['meteorite_fall']:
                    asyncio.create_task(meteorite(chat_id))
        else:
            # события в космосе
            if random.random() < 0.02:
                # Космический мусор
                if not int(all_ships[chat_id]["ship_health"]) == 0:
                    value = random.randint(1, 3)
                    all_ships[chat_id]["ship_health"] = clamp(all_ships[chat_id]["ship_health"] - value, 0, 100)
                    await send_message(chat_id,
                                       f"Мы столкнулись с космическим мусором!\nПрочность корабля: {all_ships[chat_id]["ship_health"]}%")
                    await destroy_engine(chat_id, 0.2)
            if random.random() < 0.02:
                # Космическая аномалия
                all_ships[chat_id]["distance"] = 0
                all_ships[chat_id]["next_planet_name"] = random.choice(PLANETS)
                await send_message(chat_id, f"Космическая аномалия!\nМы сбились с курса")
            if random.random() < 0.001:
                # Столкновение с астероидом
                value = random.randint(1, 20)
                all_ships[chat_id]["ship_health"] = clamp(all_ships[chat_id]["ship_health"] - value, 0, 100)
                damage_all_crew(chat_id, 10, 30)
                await send_message(chat_id,
                                   f"💥 Столкновение с астероидом! 💥\nЭкипаж получил ранения, прочность корабля: {all_ships[chat_id]["ship_health"]}%")
        # Здесь могут быть универсальные события
        if random.random() < 0.01 and not all_ships[chat_id]["alien_attack"]:
            # Атака пришельцев
            if not int(all_ships[chat_id]["ship_health"]) == 0:
                await alien_attack(chat_id)

        if random.random() < 0.01 and not all_ships[chat_id]["fire"]:
            # пожар
            all_ships[chat_id]["fire"] = True
            await fire_func(chat_id)

        await asyncio.sleep(30)


# Основной цикл игры
async def game_loop(chat_id: int):
    warned_of_air_leak = False
    warned_of_empty_air = False
    warned_of_empty_fuel = False
    while is_chat_active(chat_id):
        if all_ships[chat_id]["ship_fuel"] < 1:
            if not warned_of_empty_fuel:
                await send_message(chat_id, "⚠️ Закончилось топливо.")
                warned_of_empty_fuel = True
            all_ships[chat_id]["ship_speed"] = random.randint(0, 900)
            all_ships[chat_id]["distance"] += round(all_ships[chat_id]["ship_speed"] / 60)
        else:
            # Если бак поврежден, убавляем топливо
            if all_ships[chat_id]['fuel_tank_damaged'] and random.random() < 0.15:
                all_ships[chat_id]["ship_fuel"] -= 1

            # Изменяем скорость корабля и пройденный путь
            all_ships[chat_id]["ship_speed"] = random.randint(28000, 64000) if not all_ships[chat_id][
                'engine_damaged'] else random.randint(10000, 24000)
            all_ships[chat_id]["distance"] += round(all_ships[chat_id]["ship_speed"] / 60)

            if warned_of_empty_fuel:
                warned_of_empty_fuel = False

            if random.random() < 0.05 and not all_ships[chat_id]["on_planet"]:
                # Уменьшаем количество топлива
                all_ships[chat_id]["ship_fuel"] -= 1

        # уменьшаем воздух если здоровье корабля меньше 1 (0)
        if all_ships[chat_id]["ship_health"] < 1:
            if not warned_of_air_leak:
                await send_message(chat_id, "⚠️ Корпус разрушен, утечка воздуха. Требуется ремонт.")
                warned_of_air_leak = True

            damage_all_crew(chat_id, 1, 3)
        else:
            if warned_of_air_leak:
                warned_of_air_leak = False

        # уменьшаем здоровье если нет воздуха
        if all_ships[chat_id]["oxygen"] < 1:
            if not warned_of_empty_air:
                await send_message(chat_id, "⚠️ Закончился воздух. Требуется ремонт.")
                warned_of_empty_air = True

            damage_all_crew(chat_id, 1, 5)
        else:
            if warned_of_empty_air:
                warned_of_empty_air = False

        await check_all_crew(chat_id)
        # завершаем игру если здоровье экипажа на нуле
        if not is_crew_alive(chat_id):
            await send_message(chat_id, "Игра завершена!\nЭкипаж выведен из строя. ⚠️")
            stop_game(chat_id)
            break
        # Проверка данных во избежание проблем
        check_data(all_ships[chat_id], chat_id)
        # Ожидаем 5 секунд перед началом следующей итерации
        await asyncio.sleep(5)


# Особый цикл для орудий
async def cannon_loop(chat_id: int):
    while is_chat_active(chat_id):

        # Убираем перегрев орудия
        if all_ships[chat_id]['cannon_overheated']:
            all_ships[chat_id]['cannon_overheated'] = False

        await asyncio.sleep(10)
