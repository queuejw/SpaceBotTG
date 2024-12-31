# открытый космос бот игра от @queuejw
# библиотеки необходимые для работы бота
import asyncio
import json
import logging
import os
import sys
import random

# aiogram
from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import CommandStart, Command, CommandObject
from aiogram.methods import DeleteWebhook
from aiogram.types import Message, ChatMemberUpdated, InlineKeyboardButton, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Функция для получения токена бота из файла token.txt
def get_token() -> str:
    token_file = "token.txt"
    if os.path.exists(token_file):
        with open(token_file, "r") as f:
            result = f.read()
            f.close()
            return result
    # Если не получится, то вернёт пустой текст
    return ""

# Функция для получения списка планет
def get_planets():
    with open('planets.txt', 'r', encoding='utf-8') as file:
        planets_from_file = [line.strip() for line in file.readlines()]
        file.close()
        return planets_from_file

# Планеты
PLANETS = get_planets()

# Эмодзи
REPAIR_EMOJI = ["🔨", "⚒️", "🛠", "⛏️", "🪚", "⚙️", "🔧", "🪛"]
# Токен, бот
TOKEN = get_token()
dp = Dispatcher()
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

#Корабли всех чатов будут здесь
all_ships = {}
# Директория для хранения кораблей
DATA_DIR = "ships"
# создать если нет
os.makedirs(DATA_DIR, exist_ok=True)

# Стандартные параметры корабля

#TODO: Нужно реализовать систему пожара и утечки воздуха. Также нужно сделать одноразовое оповещение игроков о том, что произошла утечка воздуха, прочность корабля на 0 и так далее.
def get_default_ship() -> dict:
    return {
        'active': False, # Активна ли игра?
        'blocked': False, # Заблокированы ли действия игроков?
        'on_planet': False, # Находится ли корабль на планете?
        'air_leaking': False,  # Утечка воздуха
        'fire': False,  # Пожар на корабле
        'planet_name': "Земля", # Название текущей планеты
        'next_planet_name': "Луна", # Название следующей планеты
        'previous_planet_name': "Земля", # Название предыдущей планеты
        'ship_name': "Марс-06",  # Название корабля
        'distance' : 0, # Расстояние от планеты
        'ship_fuel': 100, # Уровень топлива (от 0 до 100)
        'ship_health': 100, # Уровень прочности (от 0 до 100)
        'ship_speed': 0, # Скорость (от 28 000 до 108 000)
        'crew_health': 100, # Здоровье экипажа (от 0 до 100)
        'crew_oxygen': 100, # Уровень воздуха (от 0 до 100)
        'resources': 500 # Количество ресурсов
    }

# Создает кнопки обновить для сообщения компьютера
def get_computer_inline_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Обновить", callback_data="update_computer_text"))
    return builder.as_markup()

# Создает кнопки да и отмена для сообщения самоуничтожения
def get_self_destruction_inline_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="Отмена", callback_data="self_destruction_cancel"),
        InlineKeyboardButton(text="Отмена", callback_data="self_destruction_cancel"),
        InlineKeyboardButton(text="Да", callback_data="self_destruction_continue")
    )
    return builder.as_markup()

# Создает кнопки потушить для сообщения пожара на корабле
def get_fire_inline_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Потушить", callback_data="fire_callback"))
    return builder.as_markup()


# Функция для получения пути к файлу корабля
def get_chat_folder(chat_id: int) -> str:
    print(f"Получаю папку для чата {chat_id}")
    return os.path.join(DATA_DIR, str(chat_id))

def get_chat_state_file(chat_id: int) -> str:
    print(f"Получаю файл корабля чата {chat_id}")
    return os.path.join(get_chat_folder(chat_id), "ship.json")

#Функция для удаления корабля
def delete_chat_state(chat_id: int):
    print(f"Пытаюсь удалить корабль чата {chat_id}")
    all_ships.pop(chat_id)
    state_file = get_chat_state_file(chat_id)
    if os.path.exists(state_file):
        os.remove(state_file)
        print(f"Корабль чата {chat_id} удален")

# Функция для загрузки корабля
def load_chat_state(chat_id: int) -> dict:
    print(f"Получаю корабль чата {chat_id}")
    state_file = get_chat_state_file(chat_id)
    print(state_file)

    if os.path.exists(state_file):
        with open(state_file, "r") as f:
            print("Загружаю данные из файла")
            return json.load(f)

    # Если файл не существует, инициализируем новое состояние
    print(f"Не получилось получить корабль, возвращаем стандартный.")
    return get_default_ship()

# Функция для сохранения корабля
def save_chat_state(chat_id: int, state: dict):
    print(f"Сохраняю данные корабля чата {chat_id}")
    chat_folder = get_chat_folder(chat_id)
    os.makedirs(chat_folder, exist_ok=True)

    state_file = get_chat_state_file(chat_id)
    with open(state_file, "w", encoding="utf-8") as f:
        f.write(json.dumps(state))
        print("Записаны новые данные")

#Вернет True, если корабль чата есть в словаре.
def is_chat_active(chat_id: int):
    return chat_id in all_ships

#Вернет True, если выполнение действий в данных момент запрещено
def is_actions_blocked(chat_id: int):
    return load_chat_state(chat_id)['blocked']

# Функция для создания нового корабля в чате
def create_new_ship(chat_id: int):
    print(f"Создаю корабль для чата {chat_id}")
    all_ships[chat_id] = load_chat_state(chat_id)
    save_chat_state(chat_id, all_ships[chat_id])

# Функция, которая вызывается командой /start
@dp.message(CommandStart())
async def command_start_handler(message: Message):
    text = (
        "Привет! Добро пожаловать на борт!👽\n"
        "Этот бот поможет вам весело провести время в открытом космосе вместе с друзьями!👨‍👨‍👦\n"
        "\n"
        "Путешествуйте по планетам, ищите друзей из других чатов, собирайте ресурсы и попробуйте выжить как можно дольше!💼\n"
        "\n"
        "Введи /играть , чтобы начать путешествие в мир космоса!🚀\n"
        "/инфо для информации о боте."
    )
    await message.answer(text)

# Функция, которая вызывается командой /инфо
@dp.message(Command("инфо"))
async def info(message: Message):
    text = (
        "открытый космос - игровой бот для вашего чата.👽\n"
        "находится в разработке, не все функции работают правильно.\n"
        "последнее обновление: 31.12.24\n"
        "сделал @queuejw"
    )
    await message.answer(text)

# Функция для получения текста сообщения компьютера
def get_computer_text(chat_id: int) -> str:
    state = load_chat_state(chat_id)
    if not state["on_planet"]:
        #В космосе
        text = (
        "📺БОРТОВОЙ КОМПЬЮТЕР📺\n"
        "=============\n"
        f"🚀Корабль {state['ship_name']}\n"
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
        #На планете
        text = (
            "📺БОРТОВОЙ КОМПЬЮТЕР📺\n"
            "=============\n"
            f"🚀Корабль {state['ship_name']}\n"
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
@dp.message(Command("компьютер"))
async def computer(message: Message):
    chat_id = message.chat.id
    if not is_chat_active(chat_id):
        await message.answer("Не удалось получить информацию о корабле:\nНет соединения. ⚠️")
        return
    text = get_computer_text(chat_id)
    await message.answer(text, reply_markup=get_computer_inline_keyboard())

# Функция, которая вызывается командой /помощь. Выводит текст со всеми возможными командами и их описанием.
@dp.message(Command('помощь'))
async def commands(message: Message):
    text = (
        "Команды бортового компьютера:\n"
        "\n"
        "/компьютер - информация о корабле\n"
        "/лететь [планета] - лететь на указанную планету. Если не указать, то будет выбрана следующая планета\n"
        "/покинуть - покинуть планету\n"
        "/ремонт - немного лечит экипаж и немного увеличивает прочность корабля, а также исправляет утечки воздуха. Требуется 50 ресурсов.\n"
        "/самоуничтожение - закончить игру (потребуется подтвердить своё решение)\n"
        "/название [название] - изменить название корабля (не более 18 символов)\n"
        "\n"
        "Путешествуйте по планетам, чтобы собирать ресурсы. С помощью ресурсов вы сможете ремонтировать корабль, тушить пожары и выполнять многие действия."
    )
    await message.answer(text)

@dp.message(Command("играть"))
async def play(message: Message):
    chat_id = message.chat.id
    if is_chat_active(chat_id):
        await message.answer("Не удалось запустить корабль в космос:\nИгра активна. ⚠️")
        return
    #Создаем корабль для этого чата
    create_new_ship(chat_id)
    asyncio.create_task(game_loop(chat_id))
    asyncio.create_task(game_loop_planet_change(chat_id))
    asyncio.create_task(game_loop_events(chat_id))
    text = (
        "🚀Игра началась!\n"
        "Введите команду /помощь , чтобы узнать все команды бота."
    )
    await bot.send_message(chat_id, text)

@dp.message(Command("пробитие"))
async def probitie(message: Message):
    chat_id = message.chat.id
    if not is_chat_active(chat_id):
        await message.answer("⚠️")
        return
    state = load_chat_state(chat_id)
    state["ship_health"] -= 25
    check_and_save_data(state, chat_id)
    await message.answer("Есть пробитие")

@dp.message(Command("очко"))
async def ochko(message: Message):
    chat_id = message.chat.id
    if not is_chat_active(chat_id):
        await message.answer("⚠️")
        return
    state = load_chat_state(chat_id)
    state["crew_health"] -= 25
    check_and_save_data(state, chat_id)
    await message.answer("Есть пробитие")

# Команда для переименования корабля
@dp.message(Command("название"))
async def change_ship_name(message: Message, command: CommandObject):
    chat_id = message.chat.id
    if not is_chat_active(chat_id):
        await message.answer("Не получилось отправить команду\nНет соединения с кораблем. ⚠️")
        return
    if is_actions_blocked(chat_id):
        await message.answer("Подождите, пока не будет выполнена другая задача. ⚠️")
        return
    # Если аргументов нет, то мы не можем переименовать корабль
    if command.args is None:
        await message.answer("Не получилось отправить команду\nВы не указали новое название корабля⚠️")
        return
    #Пробуем переименовать
    try:
        name = command.args
        if len(name) > 18:
            await message.answer("Не удалось изменить название\nНазвание слишком длинное⚠️")
            return
        state = load_chat_state(chat_id)
        state["ship_name"] = name
        save_chat_state(chat_id, state)
        await message.answer(f"Название корабля изменено на: {name} ")
    except ValueError:
        await message.answer("Не удалось изменить название\nПри передаче данных связь была потеряна⚠️")
        return

# Функция для имитирования полета
async def fly(chat_id: int, planet_name: str):
    state = load_chat_state(chat_id)
    if state["on_planet"]:
        await bot.send_message(chat_id, "Чтобы улететь на другую планету, нужно покинуть текущую.\nПопробуйте ввести команду /покинуть")
        return
    if state["ship_fuel"] < 1:
        await bot.send_message(chat_id,"Недостаточно топлива!️⚠️")
        return
    # случайное время для ожидания
    time = random.randint(5, 10)
    # блокируем действия на время полета и обновляем данные
    state["blocked"] = True
    save_chat_state(chat_id, state)
    # уведомляем игроков
    await bot.send_message(chat_id, f"Посадка на планету {planet_name} через {time} секунд")
    await asyncio.sleep(time)
    # обновляем данные и отменяем блокировку действий
    state["on_planet"] = True
    state["blocked"] = False
    state["planet_name"] = planet_name
    state["previous_planet_name"] = planet_name
    save_chat_state(chat_id, state)
    await bot.send_message(chat_id, f"Успешная посадка на планету {planet_name} ")

# Команда для посадки, полета на планету
@dp.message(Command("лететь"))
async def fly_command(message: Message, command: CommandObject):
    chat_id = message.chat.id
    if not is_chat_active(chat_id):
        await message.answer("Не получилось отправить команду\nНет соединения с кораблем. ⚠️")
        return
    if is_actions_blocked(chat_id):
        await message.answer("Подождите, пока не будет выполнена другая задача. ⚠️")
        return
    # Если аргументов нет, то летим на ближайшую (следующую) планету
    name = command.args
    if name is None:
        await fly(chat_id, load_chat_state(chat_id)['next_planet_name'])
    else:
        if len(name) > 18:
            await message.answer("Название планеты слишком длинное⚠️")
            return

        await fly(chat_id, name)

async def leave_planet(chat_id: int):
    state = load_chat_state(chat_id)
    if not state["on_planet"]:
        await bot.send_message(chat_id, "Невозможно покинуть планету\nВы не на планете")
        return
    if state["ship_fuel"] < 1:
        await bot.send_message(chat_id,"Недостаточно топлива!️⚠️")
        return
    # случайное время для ожидания
    time = random.randint(5, 10)
    # блокируем действия на время полета и обновляем данные
    state["blocked"] = True
    save_chat_state(chat_id, state)
    # уведомляем игроков
    await bot.send_message(chat_id, f"Покидаем планету {state["planet_name"]} через {time} секунд")
    await asyncio.sleep(time)
    # обновляем данные и отменяем блокировку действий
    state["on_planet"] = False
    state["blocked"] = False
    state["previous_planet_name"] = state["planet_name"]
    state["next_planet_name"] = random.choice(PLANETS)
    save_chat_state(chat_id, state)
    await bot.send_message(chat_id, f"Мы покинули планету {state["previous_planet_name"]}")

# Команда, чтобы покинуть планету
@dp.message(Command("покинуть"))
async def leave_planet_command(message: Message):
    chat_id = message.chat.id
    if not is_chat_active(chat_id):
        await message.answer("Не получилось отправить команду\nНет соединения с кораблем. ⚠️")
        return
    if is_actions_blocked(chat_id):
        await message.answer("Подождите, пока не будет выполнена другая задача. ⚠️")
        return
    await leave_planet(chat_id)

#Ремонт корабля
async def repair(chat_id: int):
    state = load_chat_state(chat_id)
    # блокируем действия на время ремонта и обновляем данные
    state["blocked"] = True
    save_chat_state(chat_id, state)
    # уведомляем игроков
    await bot.send_message(chat_id, "Ремонтируем корабль ...")
    for _ in range(5):
        if (state["resources"] - 25) < 1:
            break
        if state["ship_health"] > 99:
            break
        state["resources"] -= 25
        state["ship_health"] += random.randint(5, 10)
        state["crew_oxygen"] += random.randint(2, 5)
        state["crew_health"] += random.randint(2, 5)
        await bot.send_message(chat_id, random.choice(REPAIR_EMOJI))
        await asyncio.sleep(1)
    # обновляем данные и отменяем блокировку действий
    state["blocked"] = False
    save_chat_state(chat_id, state)
    await bot.send_message(chat_id, "Ремонт завершён")

# Ремонт корабля
@dp.message(Command("ремонт"))
async def repair_ship(message: Message):
    chat_id = message.chat.id
    if not is_chat_active(chat_id):
        await message.answer("Не получилось отправить команду\nНет соединения с кораблем. ⚠️")
        return
    if is_actions_blocked(chat_id):
        await message.answer("Подождите, пока не будет выполнена другая задача. ⚠️")
        return
    await repair(chat_id)

@dp.chat_member()
async def handle_chat_rocket_message(chat_member: ChatMemberUpdated):
    if chat_member.new_chat_member.user.id == bot.id:
        await bot.send_message(chat_member.chat.id, "🚀")
    elif chat_member.new_chat_member.user.id == bot.id and chat_member.new_chat_member.status in ["kicked", "left"]:
        print(f"Бота удалили из чата {chat_member.chat.id}, завершаю игру, если активна.")
        delete_chat_state(chat_member.chat.id)

@dp.message(Command("самоуничтожение"))
async def self_destruction_command(message: Message):
    chat_id = message.chat.id
    if not is_chat_active(chat_id):
        await message.answer("Не получилось отправить команду самоуничтожение\nНет соединения. ⚠️")
        return
    await message.answer("ВЫ УВЕРЕНЫ В ТОМ, ЧТО ХОТИТЕ СДЕЛАТЬ ЭТО ?:",
                        reply_markup=get_self_destruction_inline_keyboard())

@dp.message(Command("выстрел"))
async def shot_command(message: Message):
    chat_id = message.chat.id
    if not is_chat_active(chat_id):
        await message.answer("Не получилось отправить команду\nНет соединения. ⚠️")
        return
    await message.answer("не")

@dp.message(Command("сгори"))
async def fireplease(message: Message):
    chat_id = message.chat.id
    if not is_chat_active(chat_id):
        await message.answer("Не получилось отправить команду\nНет соединения. ⚠️")
        return
    await message.answer("сгори в огне мудила")
    state = load_chat_state(chat_id)
    state["fire"] = True
    check_and_save_data(state, chat_id)
    await fire_func(chat_id)

async def self_destruction_func(chat_id):
    await bot.send_message(chat_id, "💥")
    text = (
        "💥💥💥💥💥\n"
        "Игра завершена! Корабль самоуничтожился."
    )
    delete_chat_state(chat_id)
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
            print("Ошибка при изменении сообщения компьютера")
    else:
        print(f"Текст компьютера в чате {chat_id} совпадает с прошлым")
        await callback.answer("Уже обновлено.")

# Механика пожаров
async def fire_func(chat_id: int):
    await bot.send_message(chat_id, "🔥")
    await bot.send_message(chat_id, "🔥Корабль горит!🔥", reply_markup=get_fire_inline_keyboard())
    while True:
        state = load_chat_state(chat_id)
        if not state["fire"]:
            break

        if random.random() > 0.2:
            state["ship_fuel"] -= random.randint(5, 12)
        if random.random() > 0.25:
            state["resources"] -= random.randint(5, 12)
        if random.random() > 0.25:
            state["ship_health"] -= random.randint(5, 10)
        if random.random() > 0.25:
            state["crew_health"] -= random.randint(2, 8)
        if random.random() > 0.25:
            state["crew_oxygen"] -= random.randint(2, 8)

        check_and_save_data(state, chat_id)

        if random.random() < 0.1:
            await bot.send_message(chat_id, "🔥")
        await asyncio.sleep(3)


# Механика тушения пожаров
@dp.callback_query(F.data == "fire_callback")
async def fire_callback(callback: CallbackQuery):
    print("Обработка тушения пожара")
    chat_id = callback.message.chat.id
    if not is_chat_active(chat_id):
        await callback.answer()
        return
    state = load_chat_state(chat_id)
    if not state["fire"]:
        await callback.answer("Корабль не горит.")
        return
    if state["blocked"]:
        await callback.answer("Мы уже тушим корабль!")
        return
    await callback.answer("Тушим корабль ...")
    state["blocked"] = True
    check_and_save_data(state, chat_id)
    await bot.send_message(chat_id, "Тушим корабль ... 🧯")
    for _ in range(5):
        await asyncio.sleep(1)
    await bot.send_message(chat_id, "Пожар потушен!🧯✅")
    state["blocked"] = False
    state["fire"] = False
    check_and_save_data(state, chat_id)

@dp.callback_query(F.data.startswith("self_destruction_"))
async def self_destruction_callback(callback: CallbackQuery):
    print("Обработка самоуничтожения")
    chat_id = callback.message.chat.id
    if not is_chat_active(chat_id):
        await callback.answer()
        return
    if callback.data == "self_destruction_cancel":
        print("Отмена самоуничтожения")
        await bot.answer_callback_query(callback.id, text="Отмена самоуничтожения")
        await bot.delete_message(callback.message.chat.id, callback.message.message_id)
    elif callback.data == "self_destruction_continue":
        print(f"Начинаем самоуничтожение в чате {chat_id}")
        await bot.answer_callback_query(callback.id, text="САМОУНИЧТОЖЕНИЕ")
        await bot.delete_message(callback.message.chat.id, callback.message.message_id)
        await self_destruction_func(callback.message.chat.id)
    await callback.answer()

#Костыль для перепроверки данных и их обновления
def check_and_save_data(state: dict, chat_id: int):
    if state["ship_fuel"] < 1:
        state["ship_fuel"] = 0
    if state["ship_health"] < 1:
        state["ship_health"] = 0
    if state["crew_health"] < 1:
        state["crew_health"] = 0
    if state["crew_oxygen"] < 1:
        state["crew_oxygen"] = 0

    if state["ship_fuel"] > 100:
        state["ship_fuel"] = 100
    if state["ship_health"] > 100:
        state["ship_health"] = 100
    if state["crew_health"] > 100:
        state["crew_health"] = 100
    if state["crew_oxygen"] > 100:
        state["crew_oxygen"] = 100

    save_chat_state(chat_id, state)

# Изменение планет и сброс расстояния каждые 60 секунд
async def game_loop_planet_change(chat_id: int):
    while is_chat_active(chat_id):
        state = load_chat_state(chat_id)
        if not state['on_planet']:
            state['previous_planet_name'] = state['next_planet_name']
            state['next_planet_name'] = random.choice(PLANETS)
            state["distance"] = 0
            save_chat_state(chat_id, state)
        await asyncio.sleep(60)

# Создание случайных событий на планете или в космосе.
async def game_loop_events(chat_id: int):
    #Небольшая задержка в начале игры
    await asyncio.sleep(5)
    while is_chat_active(chat_id):
        state = load_chat_state(chat_id)
        if state["on_planet"]:
            # события на планетах
            if random.random() < 0.12:
                # Ресурсы на планете
                value = random.randint(50, 125)
                state["resources"] += value
                await bot.send_message(chat_id, f"Мы нашли полезные ресурсы!\nПолучено {value} ресурсов")
            if random.random() < 0.1:
                # Аномалия на планете
                value = random.randint(1, 3)
                state["ship_health"] -= value
                await bot.send_message(chat_id,f"Аномалия на планете. Корабль поврежден!\nПрочность корабля: {state["ship_health"]}%")
        else:
            # события в космосе
            if random.random() < 0.15:
                # Космический мусор
                value = random.randint(1, 8)
                state["ship_health"] -= value
                await bot.send_message(chat_id, f"Мы столкнулись с космическим мусором!\nПрочность корабля: {state["ship_health"]}%")
            if random.random() < 0.2:
                # Космическая аномалия
                state["next_planet_name"] = random.choice(PLANETS)
                await bot.send_message(chat_id, f"Космическая аномалия!\nМы сбились с курса")
        # Здесь могут быть универсальные события
        if random.random() < 0.04 and not state["fire"]:
            # пожар
            state["fire"] = True
            check_and_save_data(state, chat_id)
            await fire_func(chat_id)

        check_and_save_data(state, chat_id)
        await asyncio.sleep(30)

async def game_loop(chat_id: int):
    while is_chat_active(chat_id):
        # Получаю данные корабля
        state = load_chat_state(chat_id)
        if state["ship_fuel"] < 1:
            state["ship_speed"] = random.randint(0, 700)
            state["distance"] += round(state["ship_speed"] / 60)
        else:
            # Изменяем скорость корабля и пройденный путь
            state["ship_speed"] = random.randint(28000, 64000)
            state["distance"] += round(state["ship_speed"] / 60)
            if random.random() < 0.05 and not state["on_planet"]:
                # Уменьшаем количество топлива
                state["ship_fuel"] -= 1

        # уменьшаем воздух если здоровье корабля меньше 1 (0)
        if state["ship_health"] < 1:
            state["crew_oxygen"] -= random.randint(1, 10)

        # уменьшаем здоровье если нет воздуха
        if state["crew_oxygen"] < 1:
            state["crew_health"] -= random.randint(1, 10)

        # завершаем игру если здоровье экипажа меньше 1 (0)
        if state["crew_health"] < 1:
            await bot.send_message(chat_id, "Игра завершена!\nЭкипаж мёртв. ⚠️")
            delete_chat_state(chat_id)
            break
        # Сохраняем все изменения
        check_and_save_data(state, chat_id)
        # Ожидаем 5 секунд перед началом следующей итерации
        await asyncio.sleep(5)

# Функция, которая вызывается при запуске бота
async def init():
    await bot(DeleteWebhook(drop_pending_updates=True))
    await dp.start_polling(bot)

# Запуск бота
if __name__ == "__main__":
    print("Открытый космос бот запущен")
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(init())