print("Добро пожаловать в открытый космос. Подождите секунду...")
# открытый космос бот игра от @queuejw
# библиотеки необходимые для работы бота
import asyncio
import logging
import random
import sys
from asyncio import CancelledError
from types import NoneType

# aiogram
from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest, TelegramRetryAfter
from aiogram.filters import Command, CommandObject
from aiogram.methods import DeleteWebhook
from aiogram.types import Message, CallbackQuery

import helpers.chat_utils
from handlers import start_help_info_handler
from helpers.keyboards import get_computer_inline_keyboard, get_self_destruction_inline_keyboard, \
    get_fire_inline_keyboard, get_craft_keyboard, get_storage_inline_keyboard

all_ships = {}


# Удаляет чат из all_ships
def remove_chat_from_all_ships(chat_id: int):
    all_ships.pop(chat_id)


REPAIR_EMOJI = ["🔨", "⚒️", "🛠", "⛏️", "🪚", "⚙️", "🔧", "🪛"]

TOKEN = helpers.chat_utils.get_token()
PLANETS = helpers.chat_utils.get_planets()
dp = Dispatcher()
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))


# Вернет True, если корабль чата есть в словаре.
def is_chat_active(chat_id: int) -> bool:
    return chat_id in all_ships


# Функция, которая позволяет добавить id пользователя в список разрешенных пользователей
def add_user_to_white_list(user_id: int, chat_id: int) -> bool:
    users: list = all_ships[chat_id]['crew']
    if len(users) > 1:
        # Возвращаем False, если капитан пытается добавить самого себя
        if user_id == users[0]:
            return False
    users.append(user_id)
    all_ships[chat_id]['crew'] = users
    return True


# Функция, которая позволяет удалить id пользователя из списка разрешенных пользователей
def del_user_from_white_list(user_id: int, chat_id: int) -> bool:
    users: list = all_ships[chat_id]['crew']
    if len(users) > 1:
        # Возвращаем False, если капитан пытается удалить самого себя
        if user_id == users[0]:
            return False
    users.remove(user_id)
    all_ships[chat_id]['crew'] = users
    return True


#  Вернет True, если id пользователя есть в списке разрешенных
def is_user_allowed(user_id: int, chat_id: int) -> bool:
    users: list = all_ships[chat_id]['crew']
    return user_id in users


# Вернет True, если выполнение действий в данных момент запрещено
def is_actions_blocked(chat_id: int) -> bool:
    return all_ships[chat_id]['blocked']


# Уведомляем пользователей о том, что было загружено сохранение
async def notify_players(chat_id: int, loaded_state: dict):
    # Уведомляем, что загружено сохранение.
    if not loaded_state['default']:
        await bot.send_message(chat_id, "Загружено последнее сохранение. ☀️")
    else:
        # Помечаем, что корабль не является дефолтным
        loaded_state['default'] = False


# Функция для создания нового корабля в чате
def create_new_ship(message: Message):
    chat_id = message.chat.id
    print(f"Создаю корабль для чата {chat_id}")
    loaded_state = helpers.chat_utils.load_chat_state(chat_id)
    asyncio.create_task(notify_players(chat_id, loaded_state))
    loaded_state['captain'] = message.from_user.first_name
    all_ships[chat_id] = loaded_state
    add_user_to_white_list(message.from_user.id, chat_id)
    helpers.chat_utils.save_chat_state(chat_id, all_ships[chat_id])


# Создание корабля для чата
@dp.message(Command("играть"))
async def play(message: Message):
    chat_id = message.chat.id
    if is_chat_active(chat_id):
        await message.answer("Не удалось запустить корабль в космос:\nИгра активна. ⚠️")
        return
    # Создаем корабль для этого чата
    create_new_ship(message)
    asyncio.create_task(game_loop(chat_id))
    asyncio.create_task(game_loop_planet_change(chat_id))
    asyncio.create_task(game_loop_events(chat_id))
    text = (
        "🚀Игра началась!\n"
        "Введите команду /помощь , чтобы узнать все команды бота.\n"
        "Добавить новых членов экипажа можно командой /добавить . Посмотрите список команд."
    )
    await message.answer(text)


# Ограничивает значение в пределах минимального и максимального.
def clamp(value, min_value, max_value):
    return max(min_value, min(max_value, value))


# Функция для получения текста сообщения компьютера
def get_computer_text(chat_id: int) -> str:
    state = all_ships[chat_id]
    if not state["on_planet"]:
        # В космосе
        text = (
            "📺БОРТОВОЙ КОМПЬЮТЕР📺\n"
            "=============\n"
            f"🚀Корабль {state['ship_name']}\n"
            f"👑 Капитан корабля: {state['captain']}\n"
            "=============\n"
            f"📏Расстояние: {state['distance']} км\n"
            f"🪐Следующий объект: {state['next_planet_name']}\n"
            f"🌎Предыдущий объект: {state['previous_planet_name']}\n"
            "=============\n"
            f"🛡️Прочность корабля: {state['ship_health']}%\n"
            f"⛽️Уровень топлива: {state['ship_fuel']}%\n"
            f"🚀Скорость корабля: {state['ship_speed']} км/ч\n"
            "=============\n"
            f"❤️Здоровье экипажа: {state['crew_health']}%\n"
            f"💨Уровень воздуха: {state['crew_oxygen']}%\n"
            f"📦Количество ресурсов: {state['resources']}\n"
        )
        return text
    else:
        # На планете
        text = (
            "📺БОРТОВОЙ КОМПЬЮТЕР📺\n"
            "=============\n"
            f"🚀Корабль {state['ship_name']}\n"
            f"👑 Капитан корабля: {state['captain']}\n"
            "=============\n"
            f"🌎Мы находимся на планете: {state['planet_name']}\n"
            "=============\n"
            f"🛡️Прочность корабля: {state['ship_health']}%\n"
            f"⛽️Уровень топлива: {state['ship_fuel']}%\n"
            "=============\n"
            f"❤️Здоровье экипажа: {state['crew_health']}%\n"
            f"💨Уровень воздуха: {state['crew_oxygen']}%\n"
            f"📦Количество ресурсов: {state['resources']}\n"
        )
    return text


# Выводит информацию о корабле чата
@dp.message(Command("компьютер", "к"))
async def computer(message: Message):
    chat_id = message.chat.id
    if not is_chat_active(chat_id):
        await message.answer(
            "Не удалось получить информацию о корабле:\nНет соединения. ⚠️\nПопробуйте ввести команду /играть")
        return
    if not is_user_allowed(message.from_user.id, chat_id):
        await message.answer(
            "Только экипаж корабля может использовать эту команду. ⚠️")
        return
    text = get_computer_text(chat_id)
    await message.answer(text, reply_markup=get_computer_inline_keyboard())


@dp.message(Command("добавить"))
async def add_user(message: Message, command: CommandObject):
    chat_id = message.chat.id
    if not is_chat_active(chat_id):
        await message.answer(
            "Не удалось получить информацию о корабле:\nНет соединения. ⚠️\nПопробуйте ввести команду /играть")
        return
    # Только капитан может сделать это
    if message.from_user.id != list(all_ships[chat_id]['crew'])[0]:
        await message.answer("Только капитан может добавить участников на борт ⚠️")
        return
    # Если аргументов нет, то мы не можем добавить участников
    if command.args is None:
        await message.answer("Не получилось отправить команду\nВы не указали ID участника⚠️")
        return
    try:
        if add_user_to_white_list(int(command.args), chat_id):
            await message.answer("Успешно! Новый член экипажа успешно добавлен. ✅")
        else:
            await message.answer("Не получилось добавить нового игрока ⚠️")
    except ValueError:
        await message.answer("Не получилось добавить нового игрока ⚠️")


@dp.message(Command("удалить"))
async def add_user(message: Message, command: CommandObject):
    chat_id = message.chat.id
    if not is_chat_active(chat_id):
        await message.answer(
            "Не удалось получить информацию о корабле:\nНет соединения. ⚠️\nПопробуйте ввести команду /играть")
        return
    # Только капитан может сделать это
    if message.from_user.id != list(all_ships[chat_id]['crew'])[0]:
        await message.answer("Только капитан может удалить участников ⚠️")
        return
    # Если аргументов нет, то мы не можем удалить участников
    if command.args is None:
        await message.answer("Не получилось отправить команду\nВы не указали ID участника ⚠️")
        return
    if is_user_allowed(int(command.args), chat_id):
        try:
            if del_user_from_white_list(int(command.args), chat_id):
                await message.answer("Успешно! Член экипажа выброшен в открытый космос. ✅")
            else:
                await message.answer("Капитан не может удалить самого себя ⚠️")
        except ValueError:
            await message.answer("Не удалось удалить члена экипажа ⚠️")

    else:
        await message.answer("Не удалось удалить члена экипажа ⚠️\nПерепроверьте ID")


# Функция для получения текста склада
def get_storage_text(state: dict) -> str:
    return (f"📦 Склад корабля {state['ship_name']} 📦\n"
            "=============\n"
            f"📦 Ресурсы: {state['resources']}\n"
            f"🧯 Огнетушители: {state['extinguishers']}\n"
            f"🔫 Снаряды: {state['bullets']}\n")


# Выводит информацию о предметах на складе
@dp.message(Command("склад"))
async def storage(message: Message):
    chat_id = message.chat.id
    if not is_chat_active(chat_id):
        await message.answer(
            "Не удалось получить информацию о корабле:\nНет соединения. ⚠️\nПопробуйте ввести команду /играть")
        return
    if not is_user_allowed(message.from_user.id, chat_id):
        await message.answer(
            "Только экипаж корабля может использовать эту команду. ⚠️")
        return

    await message.answer(get_storage_text(all_ships[chat_id]), reply_markup=get_storage_inline_keyboard())


# Выводит id пользователя
@dp.message(Command("id"))
async def send_user_id(message: Message):
    await message.answer(f"Ваш ID: {message.from_user.id}")


# Проверка доступности названия корабля
def check_name(new_name: str) -> bool:
    ships = list(all_ships.items())
    for ship in ships:
        if ship[1]['ship_name'] == new_name:
            return False
    return True


# Команда для переименования корабля
@dp.message(Command("название"))
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
    if message.from_user.id != list(all_ships[chat_id]['crew'])[0]:
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

        if len(name) > 18:
            await message.answer("Не удалось изменить название\nНазвание слишком длинное⚠️")
            return
        all_ships[chat_id]["ship_name"] = name
        await message.answer(f"Название корабля изменено на: {name} ")
    except ValueError:
        await message.answer("Не удалось изменить название\nПри передаче данных связь была потеряна⚠️")
        return


# Функция для имитирования полета
async def fly(chat_id: int, planet_name: str):
    if all_ships[chat_id]["on_planet"]:
        await bot.send_message(chat_id,
                               "Чтобы улететь на другую планету, нужно покинуть текущую.\nПопробуйте ввести команду /покинуть")
        return
    if all_ships[chat_id]["ship_fuel"] < 1:
        await bot.send_message(chat_id, "Недостаточно топлива!️⚠️")
        return
    # случайное время для ожидания
    time = random.randint(5, 10) if not all_ships[chat_id]['engine_damaged'] else random.randint(10, 25)
    # блокируем действия на время полета и обновляем данные
    all_ships[chat_id]["blocked"] = True
    # уведомляем игроков
    await bot.send_message(chat_id, f"Посадка на планету {planet_name} через {time} секунд")
    await asyncio.sleep(time)
    # обновляем данные и отменяем блокировку действий
    all_ships[chat_id]["on_planet"] = True
    all_ships[chat_id]["blocked"] = False
    all_ships[chat_id]["planet_name"] = planet_name
    all_ships[chat_id]["previous_planet_name"] = planet_name
    await bot.send_message(chat_id, f"Успешная посадка на планету {planet_name} ")
    if all_ships[chat_id]['connected_chat'] != 'null':
        # Уведомляем соединенный чат о полете на планету
        c_chat_id = int(all_ships[chat_id]['connected_chat'])
        if is_chat_active(c_chat_id):
            chat = await bot.get_chat(chat_id)
            if type(chat.title) != NoneType:
                await bot.send_message(c_chat_id,
                                       f"Корабль {all_ships[chat_id]['ship_name']} чата {chat.title} летит на планету {planet_name}!")
            else:
                await bot.send_message(c_chat_id,
                                       f"Корабль {all_ships[chat_id]['ship_name']} летит на планету {planet_name}!")


# Команда для посадки, полета на планету
@dp.message(Command("лететь"))
async def fly_command(message: Message, command: CommandObject):
    chat_id = message.chat.id
    if not is_chat_active(chat_id):
        await message.answer(
            "Не получилось отправить команду\nНет соединения с кораблем. ⚠️\nПопробуйте ввести команду /играть")
        return
    if is_actions_blocked(chat_id):
        await message.answer("Подождите, пока не будет выполнена другая задача. ⚠️")
        return
    if not is_user_allowed(message.from_user.id, chat_id):
        await message.answer(
            "Только экипаж корабля может использовать эту команду. ⚠️")
        return
    # Если аргументов нет, то летим на ближайшую (следующую) планету
    name = command.args
    if name is None:
        await fly(chat_id, all_ships[chat_id]['next_planet_name'])
    else:
        if len(name) > 18:
            await message.answer("Название планеты слишком длинное⚠️")
            return

        await fly(chat_id, name)


# Функция взлёта с планета
async def leave_planet(chat_id: int):
    if not all_ships[chat_id]["on_planet"]:
        await bot.send_message(chat_id, "Невозможно покинуть планету\nВы не на планете")
        return
    if all_ships[chat_id]["ship_fuel"] < 1:
        await bot.send_message(chat_id, "Недостаточно топлива!️⚠️")
        return
    # случайное время для ожидания
    time = random.randint(5, 10) if not all_ships[chat_id]['engine_damaged'] else random.randint(10, 25)
    # блокируем действия на время полета и обновляем данные
    all_ships[chat_id]["blocked"] = True
    # уведомляем игроков
    await bot.send_message(chat_id, f"Покидаем планету {all_ships[chat_id]["planet_name"]} через {time} секунд")
    await asyncio.sleep(time)
    # обновляем данные и отменяем блокировку действий
    all_ships[chat_id]["on_planet"] = False
    all_ships[chat_id]["blocked"] = False
    all_ships[chat_id]["previous_planet_name"] = all_ships[chat_id]["planet_name"]
    all_ships[chat_id]["next_planet_name"] = random.choice(PLANETS)
    await bot.send_message(chat_id, f"Мы покинули планету {all_ships[chat_id]["previous_planet_name"]}")
    if all_ships[chat_id]['connected_chat'] != 'null':
        # Уведомляем соединенный чат о полете на планету
        c_chat_id = int(all_ships[chat_id]['connected_chat'])
        if is_chat_active(c_chat_id):
            chat = await bot.get_chat(chat_id)
            if type(chat.title) != NoneType:
                await bot.send_message(c_chat_id,
                                       f"Корабль {all_ships[chat_id]['ship_name']} чата {chat.title} покинул планету {all_ships[chat_id]["previous_planet_name"]}!")
            else:
                await bot.send_message(c_chat_id,
                                       f"Корабль {all_ships[chat_id]['ship_name']} покинул планету {all_ships[chat_id]["previous_planet_name"]}!")


# Команда, чтобы покинуть планету
@dp.message(Command("покинуть"))
async def leave_planet_command(message: Message):
    chat_id = message.chat.id
    if not is_chat_active(chat_id):
        await message.answer(
            "Не получилось отправить команду\nНет соединения с кораблем. ⚠️\nПопробуйте ввести команду /играть")
        return
    if not is_user_allowed(message.from_user.id, chat_id):
        await message.answer(
            "Только экипаж корабля может использовать эту команду. ⚠️")
        return
    if is_actions_blocked(chat_id):
        await message.answer("Подождите, пока не будет выполнена другая задача. ⚠️")
        return
    await leave_planet(chat_id)


# Ремонт корабля
async def repair(chat_id: int):
    # блокируем действия на время ремонта и обновляем данные
    all_ships[chat_id]["blocked"] = True
    # уведомляем игроков
    await bot.send_message(chat_id, "Ремонтируем корабль ...")
    for _ in range(5):
        if (all_ships[chat_id]["resources"] - 25) < 1:
            break
        if all_ships[chat_id]["ship_health"] > 99:
            break
        all_ships[chat_id]["resources"] -= 25
        all_ships[chat_id]["ship_health"] += random.randint(5, 10)
        all_ships[chat_id]["crew_oxygen"] += random.randint(2, 5)
        all_ships[chat_id]["crew_health"] += random.randint(2, 5)
        await bot.send_message(chat_id, random.choice(REPAIR_EMOJI))
        await asyncio.sleep(1)
    # Отменяем блокировку действий
    all_ships[chat_id]["blocked"] = False
    # Ремонтируем корабль и проверяем данные
    all_ships[chat_id]['engine_damaged'] = False
    all_ships[chat_id]['fuel_tank_damaged'] = False
    all_ships[chat_id]['cannon_damaged'] = False
    all_ships[chat_id]['air_leaking'] = False
    check_data(all_ships[chat_id], chat_id)
    await bot.send_message(chat_id, "Ремонт завершён")

# Функция для проверки корабля на наличие повреждений
def is_ship_damaged(ship: dict) -> bool:
    return ship['air_leaking'] or ship['engine_damaged'] or ship['fuel_tank_damaged'] or ship['cannon_damaged']


# Ремонт корабля
@dp.message(Command("ремонт"))
async def repair_ship(message: Message):
    chat_id = message.chat.id
    if not is_chat_active(chat_id):
        await message.answer("Не получилось отправить команду\nНет соединения с кораблем. ⚠️")
        return
    if not is_user_allowed(message.from_user.id, chat_id):
        await message.answer(
            "Только экипаж корабля может использовать эту команду. ⚠️")
        return
    if is_actions_blocked(chat_id):
        await message.answer("Подождите, пока не будет выполнена другая задача. ⚠️")
        return
    if all_ships[chat_id]['ship_health'] > 99 and not is_ship_damaged(all_ships[chat_id]):
        await message.answer("Ремонт не требуется.")
        return

    await repair(chat_id)


# Команда самоуничтожения
@dp.message(Command("самоуничтожение"))
async def self_destruction_command(message: Message):
    chat_id = message.chat.id
    if not is_chat_active(chat_id):
        await message.answer("Не получилось отправить команду самоуничтожение\nНет соединения. ⚠️")
        return
    if message.from_user.id != list(all_ships[chat_id]['crew'])[0]:
        await message.answer("Только капитан может сделать это ⚠️")
        return
    await message.answer("ВЫ УВЕРЕНЫ В ТОМ, ЧТО ХОТИТЕ СДЕЛАТЬ ЭТО ?:",
                         reply_markup=get_self_destruction_inline_keyboard())


# Команда для создания предметов
@dp.message(Command("создание", "крафт"))
async def craft(message: Message):
    chat_id = message.chat.id
    if not is_chat_active(chat_id):
        await message.answer("Не получилось отправить команду самоуничтожение\nНет соединения. ⚠️")
        return
    if not is_user_allowed(message.from_user.id, chat_id):
        await message.answer(
            "Только экипаж корабля может использовать эту команду. ⚠️")
        return
    await message.answer("Выберите предмет для создания 🛠",
                         reply_markup=get_craft_keyboard())


# Случайный текст для неудачного выстрела
def random_bad_shot_text() -> str:
    variants = ["Мимо!", "Промах!", "Не попал!", "Рикошет!", "Не пробил!"]
    return random.choice(variants)


# Выстрел
@dp.message(Command("выстрел"))
async def shot_command(message: Message):
    chat_id = message.chat.id
    if not is_chat_active(chat_id):
        await message.answer(
            "Не получилось отправить команду\nНет соединения с кораблем. ⚠️\nПопробуйте ввести команду /играть")
        return
    if not is_user_allowed(message.from_user.id, chat_id):
        await message.answer(
            "Только экипаж корабля может использовать эту команду. ⚠️")
        return
    if not all_ships[chat_id]['alien_attack']:
        await message.answer("⚠️ Нельзя стрелять, когда нет опасностей")
        return
    if int(all_ships[chat_id]['bullets']) < 1:
        await message.answer("⚠️ У нас нет снарядов!\nСоздайте их в меню создания (/создание)")
        return
    # Симуляция выстрела
    value = 0.5 if not all_ships[chat_id]['cannon_damaged'] else 0.75
    if random.random() < value:
        await message.answer(f"{random_bad_shot_text()} ⚠️")
    else:
        all_ships[chat_id]['alien_attack'] = False
        await message.answer("Успешный выстрел! ✅\nПришельцы уничтожены.")


# Функция для получения случайного chat id
def get_random_chat_id(my_chat_id: int):
    items = list(all_ships.items())
    if len(items) < 2:
        return my_chat_id
    r_ship = random.choice(items)
    r_chat_id = r_ship[0]
    if my_chat_id == r_chat_id:
        get_random_chat_id(my_chat_id)
    else:
        return int(r_chat_id)


# Соединение с кораблем
async def connection(random_chat_id: int, chat_id: int, my_chat_title, args):
    if random_chat_id == chat_id:
        await bot.send_message(chat_id, f"Не удалось найти ближайший корабль. Попробуйте позже.")
        return
    if not is_chat_active(random_chat_id):
        print("чат не активен, попытка соединиться ещё раз")
        await connect(chat_id, my_chat_title, args)
        return
    if all_ships[random_chat_id]['connected_chat'] != 'null':
        await bot.send_message(chat_id,
                               f"Не удалось подключиться к выбранному кораблю. Попробуйте установить связь ещё раз.")
        return

    all_ships[chat_id]['connected_chat'] = f'{random_chat_id}'
    all_ships[random_chat_id]['connected_chat'] = f'{chat_id}'

    print(f"выбран чат {random_chat_id} , отправляю сообщения")
    random_chat = await bot.get_chat(random_chat_id)

    if type(random_chat.title) != NoneType:
        r_chat_name = random_chat.title
        await bot.send_message(chat_id,
                               f"Установлена связь с кораблём {all_ships[random_chat_id]['ship_name']} чата {r_chat_name}\nЧтобы отключиться, введите /!связь")
    else:
        await bot.send_message(chat_id,
                               f"Установлена связь с кораблём {all_ships[random_chat_id]['ship_name']}\nЧтобы отключиться, введите /!связь")

    if type(my_chat_title) != NoneType:
        chat_name = my_chat_title
        await bot.send_message(random_chat_id,
                               f"Мы поймали связь с кораблём {all_ships[chat_id]['ship_name']} чата {chat_name}\nЧтобы отключиться, введите /!связь")
    else:
        await bot.send_message(random_chat_id,
                               f"Мы поймали связь с кораблём {all_ships[chat_id]['ship_name']}\nЧтобы отключиться, введите /!связь")


# Подготовка к соединению с кораблем, либо отправка сообщения
async def connect(chat_id: int, title, args):
    try:
        if type(args) == NoneType:
            # Связываемся со случайным кораблем
            if all_ships[chat_id]['connected_chat'] == 'null':
                random_chat_id = get_random_chat_id(chat_id)
                await connection(random_chat_id, chat_id, title, args)

            else:
                await bot.send_message(chat_id,
                                       f"Уже установлена связь с каким-то кораблём.\nЧтобы отключиться, введите /!связь")
        else:
            if all_ships[chat_id]['connected_chat'] == 'null':
                ships_f = 0
                ships_f_id = -1
                ships = list(all_ships.items())
                for ship in ships:
                    if ship[1]['ship_name'] == args:
                        ships_f += 1
                        ships_f_id = int(ship[0])
                if ships_f != 1:
                    await bot.send_message(chat_id,
                                           "Не получилось подключиться к выбранному кораблю ⚠️")
                else:
                    await connection(ships_f_id, chat_id, title, args)


            # или передаем сообщения
            else:
                connected_chat_id = int(all_ships[chat_id]['connected_chat'])
                if connected_chat_id == chat_id:
                    await bot.send_message(connected_chat_id, f"Не удалось найти ближайший корабль. Попробуйте позже.")
                    return
                if not is_chat_active(connected_chat_id):
                    all_ships[chat_id]['connected_chat'] = 'null'
                    await bot.send_message(chat_id, f"Не удалось соединиться с кораблём. Соединение прервано")
                    return
                if all_ships[connected_chat_id]['connected_chat'] != f'{chat_id}':
                    all_ships[chat_id]['connected_chat'] = 'null'
                    await bot.send_message(chat_id,
                                           f"Не удалось подключиться к выбранному кораблю. Попробуйте установить связь ещё раз.")
                    return
                await bot.send_message(connected_chat_id, f"Получено сообщение: {args}")
                await bot.send_message(chat_id, f"Отправлено сообщение: {args}")

    except ValueError:
        await bot.send_message(chat_id, "Не удалось связаться с кораблём.\nПри передаче данных связь была потеряна⚠️")


# Команда для связи с другими кораблями
@dp.message(Command("связь", "с"))
async def connect_to_other_ship(message: Message, command: CommandObject):
    chat_id = message.chat.id
    if not is_chat_active(chat_id):
        await message.answer(
            "Не получилось отправить команду\nНет соединения с кораблем. ⚠️\nПопробуйте ввести команду /играть")
        return
    if not is_user_allowed(message.from_user.id, chat_id):
        await message.answer(
            "Только экипаж корабля может использовать эту команду. ⚠️")
        return
    if is_actions_blocked(chat_id):
        await message.answer("Подождите, пока не будет выполнена другая задача. ⚠️")
        return
    await connect(chat_id, message.chat.title, command.args)


@dp.message(Command("!связь", "!с"))
async def disconnect_from_other_ship(message: Message):
    chat_id = message.chat.id
    if not is_chat_active(chat_id):
        await message.answer(
            "Не получилось отправить команду\nНет соединения с кораблем. ⚠️\nПопробуйте ввести команду /играть")
        return
    if not is_user_allowed(message.from_user.id, chat_id):
        await message.answer(
            "Только экипаж корабля может использовать эту команду. ⚠️")
        return
    if is_actions_blocked(chat_id):
        await message.answer("Подождите, пока не будет выполнена другая задача. ⚠️")
        return
    if all_ships[chat_id]['connected_chat'] != 'null':
        connected_chat_id = int(all_ships[chat_id]['connected_chat'])
        if not is_chat_active(connected_chat_id):
            all_ships[chat_id]['connected_chat'] = 'null'
            await bot.send_message(chat_id, f"Мы успешно отключились от другого корабля.")
            return
        connected_chat = await bot.get_chat(connected_chat_id)
        all_ships[chat_id]['connected_chat'] = 'null'
        chat_name = connected_chat.title
        if type(chat_name) != NoneType:
            await bot.send_message(chat_id,
                                   f"Мы отключились от корабля {all_ships[connected_chat_id]['ship_name']} чата {chat_name}")
        else:
            await bot.send_message(chat_id,
                                   f"Мы отключились от корабля {all_ships[connected_chat_id]['ship_name']}")

        if all_ships[connected_chat_id]["connected_chat"] == f'{chat_id}':
            all_ships[connected_chat_id]['connected_chat'] = 'null'
            if type(message.chat.title) != NoneType:
                chat_name = message.chat.title
                await bot.send_message(connected_chat_id,
                                       f"Корабль {all_ships[chat_id]["ship_name"]} чата {chat_name} отключился от нас.")
            else:
                await bot.send_message(connected_chat_id,
                                       f"Корабль {all_ships[chat_id]["ship_name"]} отключился от нас.")
    else:
        await bot.send_message(chat_id, "Мы уже отключились от другого корабля ⚠️")


async def self_destruction_func(chat_id):
    await bot.send_message(chat_id, "💥")
    text = (
        "💥💥💥💥💥\n"
        "Игра завершена! Корабль самоуничтожился."
    )
    remove_chat_from_all_ships(chat_id)
    helpers.chat_utils.delete_chat_state(chat_id)
    await bot.send_message(chat_id, text)


@dp.callback_query(F.data == "update_computer_text")
async def update_computer_text(callback: CallbackQuery):
    print("Обновляем текст компьютера")
    chat_id = callback.message.chat.id
    if not is_chat_active(chat_id):
        await callback.answer()
        return
    new_text = get_computer_text(chat_id)
    if callback.message.text != new_text:
        try:
            await callback.answer()
            await bot.edit_message_text(chat_id=chat_id,
                                        message_id=callback.message.message_id,
                                        text=new_text,
                                        reply_markup=get_computer_inline_keyboard())
            print(f"Текст компьютера в чате {chat_id} успешно обновлен")
        except TelegramBadRequest:
            print("Ошибка при изменении сообщения компьютера: TelegramBadRequest")
        except TelegramRetryAfter:
            print("Ошибка при изменении сообщения компьютера: TelegramRetryAfter")
    else:
        print(f"Текст компьютера в чате {chat_id} совпадает с прошлым")
        await callback.answer("Уже обновлено.")


@dp.callback_query(F.data == "update_storage_text")
async def update_storage_text(callback: CallbackQuery):
    print("Обновляем текст склада")
    chat_id = callback.message.chat.id
    if not is_chat_active(chat_id):
        await callback.answer()
        return
    new_text = get_storage_text(all_ships[chat_id])
    if callback.message.text != new_text:
        try:
            await callback.answer()
            await bot.edit_message_text(chat_id=chat_id,
                                        message_id=callback.message.message_id,
                                        text=new_text,
                                        reply_markup=get_storage_inline_keyboard())
            print(f"Текст склада в чате {chat_id} успешно обновлен")
        except TelegramBadRequest:
            print("Ошибка при изменении сообщения склада: TelegramBadRequest")
        except TelegramRetryAfter:
            print("Ошибка при изменении сообщения склада: TelegramRetryAfter")
    else:
        print(f"Текст склада в чате {chat_id} совпадает с прошлым")
        await callback.answer("Уже обновлено.")


# Механика пожаров
async def fire_func(chat_id: int):
    await bot.send_message(chat_id, "🔥")
    await bot.send_message(chat_id, "🔥Корабль горит!🔥", reply_markup=get_fire_inline_keyboard())
    if all_ships[chat_id]['connected_chat'] != 'null':
        # Уведомляем соединенный чат о пожаре на корабле
        c_chat_id = int(all_ships[chat_id]['connected_chat'])
        if is_chat_active(c_chat_id):
            chat = await bot.get_chat(chat_id)
            if type(chat.title) != NoneType:
                await bot.send_message(c_chat_id,
                                       f"Корабль {all_ships[chat_id]['ship_name']} чата {chat.title} горит!")
            else:
                await bot.send_message(c_chat_id,
                                       f"Корабль {all_ships[chat_id]['ship_name']} горит!")

    while True:
        if not is_chat_active(chat_id):
            break
        if not all_ships[chat_id]["fire"]:
            break

        if random.random() > 0.15:
            all_ships[chat_id]["ship_fuel"] -= random.randint(5, 10)
        if random.random() > 0.25:
            all_ships[chat_id]["resources"] -= random.randint(5, 10)
        if random.random() > 0.25:
            all_ships[chat_id]["ship_health"] -= random.randint(5, 10)
        if random.random() > 0.25:
            all_ships[chat_id]["crew_health"] -= random.randint(2, 5)
        if random.random() > 0.25:
            all_ships[chat_id]["crew_oxygen"] -= random.randint(2, 5)

        if random.random() < 0.05 and not all_ships[chat_id]["engine_damaged"]:
            all_ships[chat_id]["engine_damaged"] = True
            await bot.send_message(chat_id, "Двигатель поврежден, максимальная скорость снижена! ⚠️")

        if random.random() < 0.05 and not all_ships[chat_id]["fuel_tank_damaged"]:
            all_ships[chat_id]["fuel_tank_damaged"] = True
            await bot.send_message(chat_id, "Пробит топливный бак! ⚠️")

        if random.random() < 0.1:
            await bot.send_message(chat_id, "🔥")
        await asyncio.sleep(3)


# Механика тушения пожаров
@dp.callback_query(F.data == "fire_callback")
async def fire_callback(callback: CallbackQuery):
    print("Обработка тушения пожара")
    chat_id = callback.message.chat.id
    if not is_chat_active(chat_id):
        print("Игра не активна")
        await callback.answer()
        return
    if not all_ships[chat_id]["fire"]:
        print("Корабль не горит")
        await callback.answer("Корабль не горит.")
        return
    if int(all_ships[chat_id]['extinguishers']) < 1:
        await callback.answer("Закончились огнетушители! ⚠️")
        return
    if all_ships[chat_id]["blocked"]:
        await callback.answer("Мы уже тушим корабль!")
        return
    await callback.answer("Тушим корабль ...")
    all_ships[chat_id]["blocked"] = True
    await bot.send_message(chat_id, "Тушим корабль ... 🧯")
    for _ in range(random.randint(4, 7)):
        await asyncio.sleep(1)
    await bot.send_message(chat_id, "Пожар потушен!🧯✅")
    all_ships[chat_id]['extinguishers'] -= 1
    all_ships[chat_id]["blocked"] = False
    all_ships[chat_id]["fire"] = False


async def delete_message(chat_id: int, message_id: int):
    try:
        await bot.delete_message(chat_id, message_id)
    except TelegramBadRequest:
        print("Не получилось удалить сообщение.")


@dp.callback_query(F.data.startswith("self_destruction_"))
async def self_destruction_callback(callback: CallbackQuery):
    print("Обработка самоуничтожения")
    chat_id = callback.message.chat.id
    if not is_chat_active(chat_id):
        print("Игра не активна")
        await callback.answer()
        return
    if callback.data == "self_destruction_cancel":
        print("Отмена самоуничтожения")
        await bot.answer_callback_query(callback.id, text="Отмена самоуничтожения")
        await delete_message(callback.message.chat.id, callback.message.message_id)

    elif callback.data == "self_destruction_continue":
        print(f"Начинаем самоуничтожение в чате {chat_id}")
        await bot.answer_callback_query(callback.id, text="САМОУНИЧТОЖЕНИЕ")
        try:
            await delete_message(callback.message.chat.id, callback.message.message_id)
        except TelegramBadRequest:
            print("Не получилось удалить сообщение.")
        await self_destruction_func(callback.message.chat.id)
    await callback.answer()


@dp.callback_query(F.data.startswith("craft_"))
async def craft_callback(callback: CallbackQuery):
    print("Обработка создания предметов")
    chat_id = callback.message.chat.id
    if not is_chat_active(chat_id):
        print("Игра не активна")
        await callback.answer()
        return
    if callback.data == "craft_exit":
        print("Отмена создания предметов")
        await bot.answer_callback_query(callback.id, text="Отмена создания предметов")
        await delete_message(callback.message.chat.id, callback.message.message_id)

    elif callback.data == "craft_extinguisher":
        if int(all_ships[chat_id]['resources']) < 100:
            await bot.send_message(chat_id, "Недостаточно ресурсов ⚠️")
            return
        all_ships[chat_id]['resources'] -= 100
        all_ships[chat_id]['extinguishers'] += 1
        await bot.answer_callback_query(callback.id, text="Создан огнетушитель")
        await bot.send_message(chat_id, "Создан огнетушитель ✅\n+ 1 огнетушитель")
        await delete_message(callback.message.chat.id, callback.message.message_id)

    elif callback.data == "craft_bullet":
        if int(all_ships[chat_id]['resources']) < 50:
            await bot.send_message(chat_id, "Недостаточно ресурсов ⚠️")
            return
        all_ships[chat_id]['resources'] -= 50
        all_ships[chat_id]['bullets'] += 1
        await bot.answer_callback_query(callback.id, text="Создан снаряд")
        await bot.send_message(chat_id, "Создан снаряд ✅\n+ 1 снаряд")
        await delete_message(callback.message.chat.id, callback.message.message_id)

    elif callback.data == "craft_fuel":
        if int(all_ships[chat_id]['resources']) < 75:
            await bot.send_message(chat_id, "Недостаточно ресурсов ⚠️")
            return
        if int(all_ships[chat_id]['ship_fuel']) > 99:
            await bot.send_message(chat_id, "Корабль не нуждается в топливе ⚠️")
            return
        all_ships[chat_id]['resources'] -= 75
        all_ships[chat_id]['ship_fuel'] += 10
        check_data(all_ships[chat_id], chat_id)
        await bot.answer_callback_query(callback.id, text="Создано топливо.")
        await bot.send_message(chat_id, "Создано топливо ✅\n+ 10% топлива")
        await delete_message(callback.message.chat.id, callback.message.message_id)

    await callback.answer()


# Костыль для перепроверки данных
def check_data(state: dict, chat_id: int):
    state["ship_fuel"] = clamp(state["ship_fuel"], 0, 100)
    state["ship_health"] = clamp(state["ship_health"], 0, 100)
    state["crew_health"] = clamp(state["crew_health"], 0, 100)
    state["crew_oxygen"] = clamp(state["crew_oxygen"], 0, 100)
    state["extinguishers"] = clamp(state["extinguishers"], 0, 256)
    state["bullets"] = clamp(state["bullets"], 0, 128)
    all_ships[chat_id] = state


# Функция для сохранения данных
def check_and_save_data(state: dict, chat_id: int):
    check_data(state, chat_id)
    helpers.chat_utils.save_chat_state(chat_id, state)


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
    await bot.send_message(chat_id, "⚠️ Нас атакуют пришельцы! 👽🛸\nОтбейте атаку при помощи команды:\n/выстрел")
    if all_ships[chat_id]['connected_chat'] != 'null':
        c_chat_id = int(all_ships[chat_id]['connected_chat'])
        if is_chat_active(c_chat_id):
            chat = await bot.get_chat(chat_id)
            if type(chat.title) != NoneType:
                await bot.send_message(c_chat_id,
                                       f"Корабль {all_ships[chat_id]['ship_name']} чата {chat.title} атакуют пришельцы!")
            else:
                await bot.send_message(c_chat_id,
                                       f"Корабль {all_ships[chat_id]['ship_name']} атакуют пришельцы!")
    while is_chat_active(chat_id) and all_ships[chat_id]['alien_attack']:
        if random.random() < 0.05:
            all_ships[chat_id]['ship_health'] = clamp(all_ships[chat_id]['ship_health'] - random.randint(1, 10), 0, 100)
            await bot.send_message(chat_id,
                                   f"Пришельцы попали в нас 👽!\nПрочность корабля: {all_ships[chat_id]['ship_health']}%")
            if random.random() < 0.25 and not all_ships[chat_id]["fire"]:
                # Пожар от выстрела противника
                all_ships[chat_id]["fire"] = True
                await fire_func(chat_id)

            if random.random() < 0.1 and not all_ships[chat_id]["engine_damaged"]:
                all_ships[chat_id]["engine_damaged"] = True
                await bot.send_message(chat_id, "Двигатель поврежден, максимальная скорость снижена! ⚠️")

            if random.random() < 0.1 and not all_ships[chat_id]["fuel_tank_damaged"]:
                all_ships[chat_id]["fuel_tank_damaged"] = True
                await bot.send_message(chat_id, "Пробит топливный бак! ⚠️")

            if random.random() < 0.1 and not all_ships[chat_id]["cannon_damaged"]:
                all_ships[chat_id]["cannon_damaged"] = True
                await bot.send_message(chat_id, "Орудие повреждено, точность стрельбы снижена! ⚠️")


        await asyncio.sleep(5)


# Создание случайных событий на планете или в космосе.
async def game_loop_events(chat_id: int):
    # Небольшая задержка в начале игры
    await asyncio.sleep(5)
    while is_chat_active(chat_id):
        if all_ships[chat_id]["on_planet"]:
            # события на планетах
            if random.random() < 0.12:
                # Ресурсы на планете
                value = random.randint(50, 125)
                all_ships[chat_id]["resources"] += value
                await bot.send_message(chat_id, f"Мы нашли полезные ресурсы!\nПолучено {value} ресурсов")
            if random.random() < 0.08:
                # Аномалия на планете
                value = random.randint(1, 3)
                all_ships[chat_id]["ship_health"] -= value
                await bot.send_message(chat_id,
                                       f"Аномалия на планете. Корабль поврежден!\nПрочность корабля: {all_ships[chat_id]["ship_health"]}%")
        else:
            # события в космосе
            if random.random() < 0.03:
                # Космический мусор
                value = random.randint(1, 8)
                all_ships[chat_id]["ship_health"] -= value
                await bot.send_message(chat_id,
                                       f"Мы столкнулись с космическим мусором!\nПрочность корабля: {all_ships[chat_id]["ship_health"]}%")
            if random.random() < 0.02:
                # Космическая аномалия
                all_ships[chat_id]["next_planet_name"] = random.choice(PLANETS)
                await bot.send_message(chat_id, f"Космическая аномалия!\nМы сбились с курса")
        # Здесь могут быть универсальные события
        if random.random() < 0.01 and not all_ships[chat_id]["alien_attack"]:
            # Атака пришельцев
            await alien_attack(chat_id)

        if random.random() < 0.008 and not all_ships[chat_id]["fire"]:
            # пожар
            all_ships[chat_id]["fire"] = True
            await fire_func(chat_id)

        check_data(all_ships[chat_id], chat_id)
        await asyncio.sleep(30)


# Основной цикл игры
async def game_loop(chat_id: int):
    warned_of_air_leak = False
    warned_of_empty_air = False
    warned_of_empty_fuel = False
    while is_chat_active(chat_id):
        if all_ships[chat_id]["ship_fuel"] < 1:
            if not warned_of_empty_fuel:
                await bot.send_message(chat_id, "⚠️ Закончилось топливо.")
                warned_of_empty_fuel = True
            all_ships[chat_id]["ship_speed"] = random.randint(0, 900)
            all_ships[chat_id]["distance"] += round(all_ships[chat_id]["ship_speed"] / 60)
        else:
            # Если бак поврежден, убавляем топливо
            if all_ships[chat_id]['fuel_tank_damaged'] and random.random() < 0.15:
                 all_ships[chat_id]["ship_fuel"] -= 1

            # Изменяем скорость корабля и пройденный путь
            if not all_ships[chat_id]['engine_damaged']:
                all_ships[chat_id]["ship_speed"] = random.randint(28000, 64000)
            else:
                all_ships[chat_id]["ship_speed"] = random.randint(10000, 24000)

            all_ships[chat_id]["distance"] += round(all_ships[chat_id]["ship_speed"] / 60)

            if warned_of_empty_fuel:
                warned_of_empty_fuel = False

            if random.random() < 0.05 and not all_ships[chat_id]["on_planet"]:
                # Уменьшаем количество топлива
                all_ships[chat_id]["ship_fuel"] -= 1

        # уменьшаем воздух если здоровье корабля меньше 1 (0)
        if all_ships[chat_id]["ship_health"] < 1:
            if not warned_of_air_leak:
                await bot.send_message(chat_id, "⚠️ Корпус разрушен, утечка воздуха. Требуется ремонт.")
                warned_of_air_leak = True

            all_ships[chat_id]["crew_oxygen"] -= random.randint(1, 10)
        else:
            if warned_of_air_leak:
                warned_of_air_leak = False

        # уменьшаем здоровье если нет воздуха
        if all_ships[chat_id]["crew_oxygen"] < 1:
            if not warned_of_empty_air:
                await bot.send_message(chat_id, "⚠️ Закончился воздух. Требуется ремонт.")
                warned_of_empty_air = True

            all_ships[chat_id]["crew_health"] -= random.randint(1, 10)
        else:
            if warned_of_empty_air:
                warned_of_empty_air = False

        # завершаем игру если здоровье экипажа меньше 1 (0)
        if all_ships[chat_id]["crew_health"] < 1:
            await bot.send_message(chat_id, "Игра завершена!\nЭкипаж выведен из строя. ⚠️")
            remove_chat_from_all_ships(chat_id)
            helpers.chat_utils.delete_chat_state(chat_id)
            break
        # Проверка данных во избежание проблем
        check_data(all_ships[chat_id], chat_id)
        # Ожидаем 5 секунд перед началом следующей итерации
        await asyncio.sleep(5)
    await bot.send_message(chat_id, "Конец.")


# Функция, которая вызывается при запуске бота
async def init():
    try:
        dp.include_routers(start_help_info_handler.router)
        await bot(DeleteWebhook(drop_pending_updates=True))
        await dp.start_polling(bot)
    except CancelledError:
        print("Остановка.")


# Запуск бота
if __name__ == "__main__":
    print(f"Открытый космос бот запущен.")
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(init())
