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
from aiogram.exceptions import TelegramBadRequest, TelegramRetryAfter, TelegramNetworkError
from aiogram.filters import Command, CommandObject, ChatMemberUpdatedFilter, IS_NOT_MEMBER, IS_MEMBER
from aiogram.methods import DeleteWebhook
from aiogram.types import Message, CallbackQuery, ChatMemberUpdated, Chat

from handlers import start_help_info_handler
from helpers import chat_utils
from helpers.bot_utils import load_config, save_config
from helpers.crew import get_default_crew
from helpers.keyboards import get_computer_inline_keyboard, get_self_destruction_inline_keyboard, \
    get_fire_inline_keyboard, get_craft_keyboard, get_storage_inline_keyboard
from helpers.utils import github_link

all_ships = {}


# Удаляет чат из all_ships
def remove_chat_from_all_ships(chat_id: int):
    if is_chat_active(chat_id):
        all_ships.pop(chat_id)


CONFIG = load_config()

BLOCKED_CHATS: list = CONFIG['blacklist']
ADMINS: list = CONFIG['administrators']

if len(CONFIG) == 0:
    print("Проверьте файл конфигурации.")
    exit(1)

TOKEN = CONFIG['token']

if TOKEN == "":
    print("Невозможно продолжить запуск. Проверьте токен в файле конфигурации")
    exit(1)

PLANETS = chat_utils.get_planets()
REPAIR_EMOJI = ["🔨", "⚒️", "🛠", "⛏️", "🪚", "⚙️", "🔧", "🪛"]

dp = Dispatcher()
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))


# Здоровье всего экипажа. Размер в зависимости от количества участников
def get_total_crew_health(chat_id: int) -> int:
    value = 0
    for i in all_ships[chat_id]['crew']:
        value += int(i['user_health'])
    return value


# Здоровье одного конкретного человека
def get_crew_health(chat_id: int, user_id: int) -> int:
    for i in all_ships[chat_id]['crew']:
        if int(i['user_id']) == user_id:
            return int(i['user_health'])
    return -1


# Здоровье одного конкретного человека
def get_crew_role(chat_id: int, user_id: int) -> int:
    for i in all_ships[chat_id]['crew']:
        if int(i['user_id']) == user_id:
            return int(i['user_id'])
    return -1


# Уменьшаем урон у всех на случайное количество в пределах min_value - max_value
def damage_all_crew(chat_id: int, min_value: int, max_value: int):
    for i in all_ships[chat_id]['crew']:
        i['user_health'] = clamp(i['user_health'] - random.randint(min_value, max_value), 0, 100)


# Уменьшаем урон у одного участника
def damage_crew(chat_id: int, user_id: int, value: int):
    for i in all_ships[chat_id]['crew']:
        if int(i['user_id']) == user_id:
            i['user_health'] = clamp(i['user_health'] - value, 0, 100)


# Проверяем здоровье у всех участников. Если на нуле - удаляем. Если погибает капитан, передаем роль случайному участнику
async def check_all_crew(chat_id: int):
    index = 0
    for i in all_ships[chat_id]['crew']:
        if i['user_health'] < 1:
            if i['user_role'] == 1:
                print("Передаем роль капитана случайному участнику")
                all_ships[chat_id]['crew'][0] = random.choice(all_ships[chat_id]['crew'])
                all_ships[chat_id]['crew'][0]['user_role'] = 1
                all_ships[chat_id]['crew'].pop(index)
                await bot.send_message(chat_id,
                                       f"Капитан {i['user_name']} погиб! Встречайте нового капитана: {all_ships[chat_id]['crew'][0]['user_name']} 👑")
            else:
                print("Какой-то игрок погиб")
                all_ships[chat_id]['crew'].remove(i)
                await bot.send_message(chat_id, f"{get_crew_role_by_num(int(i['user_role']))} {i['user_name']} погиб 😵")
        index += 1


# Если общее здоровье на нуле, то вернет False
def is_crew_alive(chat_id: int) -> bool:
    return get_total_crew_health(chat_id) != 0


# Вернет True, если корабль чата есть в словаре.
def is_chat_active(chat_id: int) -> bool:
    return chat_id in all_ships


# Функция, которая позволяет добавить пользователя в список разрешенных пользователей
def add_user_to_white_list(user_id: int, chat_id: int, user_name: str, user_role: int) -> bool:
    if len(all_ships[chat_id]['crew']) > 1:
        # Возвращаем False, если капитан пытается добавить самого себя
        if user_id == all_ships[chat_id]['crew'][0]['user_id']:
            return False
    captain = get_default_crew()
    captain["user_name"] = user_name
    captain["user_role"] = user_role
    captain["user_id"] = user_id
    all_ships[chat_id]['crew'].append(captain)
    return True


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


#  Вернет True, если id пользователя есть в списке
def exist_user_by_id(chat_id: int, user_id: int) -> bool:
    for i in all_ships[chat_id]['crew']:
        if i['user_id'] == user_id:
            return True
    return False


#  Вернет True, если имя пользователя есть в списке
def exist_user_by_name(chat_id: int, user_name: str) -> bool:
    for i in all_ships[chat_id]['crew']:
        if i['user_name'] == user_name:
            return True
    return False


# Вернет True, если выполнение действий в данных момент запрещено
def is_actions_blocked(chat_id: int) -> bool:
    return all_ships[chat_id]['blocked']


# Вернет True, если чат заблокирован
def is_chat_banned(chat_id) -> bool:
    if chat_id in BLOCKED_CHATS:
        print(f"{chat_id} Заблокирован, возвращаем False")
        return True
    else:
        return False


async def can_proceed(message: Message) -> bool:
    if is_chat_banned(message.chat.id):
        await message.answer(
            "🪐❌ Ваш чат был заблокирован. \nЕсли вы считаете, что это была ошибка, свяжитесь со мной: @queuejw")
        return False
    if not is_chat_active(message.chat.id):
        await message.answer(
            "Не удалось получить информацию о корабле:\nНет соединения. ⚠️\nПопробуйте ввести команду /играть")
        return False
    if not exist_user_by_id(message.chat.id, message.from_user.id):
        await message.answer(
            "Только экипаж корабля может использовать эту команду. ⚠️")
        return False
    if is_actions_blocked(message.chat.id):
        await message.answer("Подождите, пока не будет выполнена другая задача. ⚠️")
        return False
    return True


# Создает капитана
def create_captain_user_dict(user_name: str, user_id: int) -> dict:
    captain = get_default_crew()
    captain["user_name"] = user_name
    captain["user_role"] = 1
    captain["user_id"] = user_id
    return captain


# Функция для создания нового корабля в чате
def create_new_ship(message: Message):
    chat_id = message.chat.id
    print(f"Создаю корабль для чата {chat_id}")
    loaded_state = chat_utils.load_chat_state(chat_id)
    # Если на корабле никого нет, то создаем капитана
    if len(loaded_state['crew']) < 1:
        loaded_state['crew'].append(create_captain_user_dict(message.from_user.first_name, message.from_user.id))
    # Во избежание проблем сбрасываем пришельцев и пожары
    loaded_state['fire'] = False
    loaded_state['alien_attack'] = False
    all_ships[chat_id] = loaded_state
    chat_utils.save_chat_state(chat_id, all_ships[chat_id])


# Создание корабля для чата
@dp.message(Command("играть"))
async def play(message: Message):
    chat_id = message.chat.id
    if is_chat_banned(chat_id):
        await message.answer(
            "🪐❌ Ваш чат был заблокирован. \nЕсли вы считаете, что это была ошибка, свяжитесь со мной: @queuejw")
        return
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
        "Добавить новых членов экипажа можно командой /добавить . Посмотрите список команд.\n"
    )
    if not all_ships[chat_id]['default']:
        text = text + "ℹ️ Загружено последнее сохранение"
    else:
        all_ships[chat_id]['default'] = False

    await message.answer(text)


# Останавливает игру и удаляет файл сохранения
def stop_game(chat_id: int):
    remove_chat_from_all_ships(chat_id)
    chat_utils.delete_chat_state(chat_id)


# Ограничивает значение в пределах минимального и максимального.
def clamp(value, min_value, max_value):
    return max(min_value, min(max_value, value))


# Функция для получения текста сообщения компьютера
def get_computer_text(chat_id: int) -> str:
    state = all_ships[chat_id]
    captain = all_ships[chat_id]['crew'][0]['user_name']
    if not state["on_planet"]:
        # В космосе
        text = (
            "📺БОРТОВОЙ КОМПЬЮТЕР📺\n"
            "=============\n"
            f"🚀Корабль {state['ship_name']}\n"
            f"👑 Капитан корабля: {captain}\n"
            "=============\n"
            f"📏Расстояние: {state['distance']} км\n"
            f"🪐Следующий объект: {state['next_planet_name']}\n"
            f"🌎Предыдущий объект: {state['previous_planet_name']}\n"
            "=============\n"
            f"🛡️Прочность корабля: {state['ship_health']}%\n"
            f"⛽️Уровень топлива: {state['ship_fuel']}%\n"
            f"🚀Скорость корабля: {state['ship_speed']} км/ч\n"
            "=============\n"
            f"💨Уровень воздуха: {state['oxygen']}%\n"
            f"📦Количество ресурсов: {state['resources']}\n"
        )
        return text
    else:
        # На планете
        text = (
            "📺БОРТОВОЙ КОМПЬЮТЕР📺\n"
            "=============\n"
            f"🚀Корабль {state['ship_name']}\n"
            f"👑 Капитан корабля: {captain}\n"
            "=============\n"
            f"🌎Мы находимся на планете: {state['planet_name']}\n"
            "=============\n"
            f"🛡️Прочность корабля: {state['ship_health']}%\n"
            f"⛽️Уровень топлива: {state['ship_fuel']}%\n"
            "=============\n"
            f"💨Уровень воздуха: {state['oxygen']}%\n"
            f"📦Количество ресурсов: {state['resources']}\n"
        )
    return text


# Выводит информацию о корабле чата
@dp.message(Command("компьютер", "к"))
async def computer(message: Message):
    chat_id = message.chat.id
    if not await can_proceed(message):
        return
    text = get_computer_text(chat_id)
    await message.answer(text, reply_markup=get_computer_inline_keyboard())


def get_crew_role_by_num(value: int) -> str:
    match value:
        case 1:
            return "Капитан"
        case 2:
            return "не придумал"
        case _:
            return "Член экипажа"


# Функция для получения текста сообщения экипажа
def get_crew_text(chat_id) -> str:
    text = f"Экипаж корабля {all_ships[chat_id]['ship_name']}:\n\n"
    for i in all_ships[chat_id]['crew']:
        text = text + f"👤 {i['user_name']} : {get_crew_role_by_num(i['user_role'])}\n"
    return text


def get_crew_str(item: dict) -> str:
    return (
        f"👤 {item['user_name']}:\n"
        "=====\n"
        f"⭐ Роль: {get_crew_role_by_num(item['user_role'])}\n"
        f"❤️ Здоровье: {item['user_health']}%\n"
    )


# Выводит информацию об экипаже корабля чата
def get_specific_crew_text(chat_id: int, user_data) -> str:
    is_int = type(user_data) == type(0)
    for i in all_ships[chat_id]['crew']:
        if is_int:
            if i['user_id'] == int(user_data):
                return get_crew_str(i)
        else:
            if i['user_name'] == str(user_data):
                return get_crew_str(i)

    return "⚠️ Компьютер не нашёл этого члена экипажа.\n"


def is_it_int(value: str) -> bool:
    try:
        int(value)
        return True
    except ValueError:
        return False


# Выводит список игроков либо информацию о конкретном игроке
@dp.message(Command("экипаж", "э"))
async def crew(message: Message, command: CommandObject):
    chat_id = message.chat.id
    if not await can_proceed(message):
        return
    # Если ник не был указан, то отправляем список участников
    if command.args is None:
        text = get_crew_text(chat_id)
        await message.answer(text)
    else:
        # Проверяем, что данный пользователь существует и отправляем сообщение
        value: bool
        if not is_it_int(command.args):
            value = exist_user_by_name(chat_id, command.args)
        else:
            value = exist_user_by_id(chat_id, int(command.args))

        text = get_specific_crew_text(chat_id, command.args) if not is_it_int(command.args) else get_specific_crew_text(
            chat_id, int(command.args))
        if value:
            await message.answer(text)
        else:
            await message.answer(text + "Возможно, вы ошиблись с вводом имени или id члена экипажа.")


# Выводит информацию об игроке, который ввел эту команду
@dp.message(Command("я"))
async def about_me(message: Message):
    chat_id = message.chat.id
    if not await can_proceed(message):
        return
    text = get_specific_crew_text(chat_id, message.from_user.id)
    await message.answer(text)


@dp.message(Command("пауза"))
async def pause_game(message: Message):
    chat_id = message.chat.id
    if not await can_proceed(message):
        return
    # Только капитан может сделать это
    if message.from_user.id != all_ships[chat_id]['crew'][0]['user_id']:
        await message.answer("Только капитан может остановить игру.")
        return
    check_and_save_data(all_ships[chat_id], chat_id)
    remove_chat_from_all_ships(chat_id)
    await message.answer(
        "Игра остановлена! ✅\nℹ️ Продолжить игру можно командой /играть (загрузится последнее сохранение)")


@dp.message(Command("добавить"))
async def add_user(message: Message, command: CommandObject):
    chat_id = message.chat.id
    if not is_chat_active(chat_id):
        await message.answer(
            "Не удалось получить информацию о корабле:\nНет соединения. ⚠️\nПопробуйте ввести команду /играть")
        return
    # Только капитан может сделать это
    if message.from_user.id != all_ships[chat_id]['crew'][0]['user_id']:
        await message.answer("Только капитан может добавить участников на борт ⚠️")
        return
    # Если аргументов нет, то мы не можем добавить участников
    if command.args is None:
        await message.answer("Не получилось отправить команду\nВы не указали ID участника⚠️")
        return
    try:
        user = await bot.get_chat_member(chat_id, int(command.args))
        if add_user_to_white_list(int(command.args), chat_id, user.user.first_name, 0):
            await message.answer(f"Успешно! {user.user.first_name} теперь член экипажа корабля. ✅")
        else:
            await message.answer("Не получилось добавить нового игрока ⚠️")
    except ValueError:
        await message.answer("Не получилось добавить нового игрока ⚠️")
    except TelegramBadRequest:
        await message.answer("Компьютер не нашёл этого участника ⚠️")


@dp.message(Command("удалить"))
async def del_user(message: Message, command: CommandObject):
    chat_id = message.chat.id
    if not is_chat_active(chat_id):
        await message.answer(
            "Не удалось получить информацию о корабле:\nНет соединения. ⚠️\nПопробуйте ввести команду /играть")
        return
    # Только капитан может сделать это
    if message.from_user.id != all_ships[chat_id]['crew'][0]['user_id']:
        await message.answer("Только капитан может удалить участников ⚠️")
        return
    # Если аргументов нет, то мы не можем удалить участников
    if command.args is None:
        await message.answer("Не получилось отправить команду\nВы не указали ID участника ⚠️")
        return
    if exist_user_by_id(chat_id, int(command.args)):
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
    if not await can_proceed(message):
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
    if not is_chat_active(chat_id):
        return
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
    if not is_chat_active(chat_id):
        return
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
    if not await can_proceed(message):
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
    if not is_chat_active(chat_id):
        return
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
    if not is_chat_active(chat_id):
        return
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
    if not await can_proceed(message):
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
        all_ships[chat_id]["oxygen"] += random.randint(2, 5)
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
    if not await can_proceed(message):
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
    if message.from_user.id != all_ships[chat_id]['crew'][0]['user_id']:
        await message.answer("Только капитан может сделать это ⚠️")
        return
    await message.answer("ВЫ УВЕРЕНЫ В ТОМ, ЧТО ХОТИТЕ СДЕЛАТЬ ЭТО ?:",
                         reply_markup=get_self_destruction_inline_keyboard())


# Команда для создания предметов
@dp.message(Command("создание", "крафт"))
async def craft(message: Message):
    if not await can_proceed(message):
        return
    await message.answer("Выберите предмет для создания 🛠",
                         reply_markup=get_craft_keyboard())


# Случайный текст для неудачного выстрела
def random_bad_shot_text() -> str:
    variants = ["Мимо!", "Промах!", "Не попал!", "Рикошет!", "Не пробил!"]
    return random.choice(variants)


async def shot(chat_id: int, chat: Chat, connected_chat_id: int):
    if is_chat_banned(connected_chat_id):
        all_ships[chat_id]['connected_chat'] = 'null'
        all_ships[chat_id]['blocked'] = False
        await bot.send_message(chat_id,
                               f"Не удалось выстрелить. Другой корабль был заблокирован.")
        return
    if not is_chat_active(connected_chat_id):
        all_ships[chat_id]['connected_chat'] = 'null'
        all_ships[chat_id]['blocked'] = False
        await bot.send_message(chat_id, f"Не удалось выстрелить. Соединение с другим кораблем прервано.")
        return
    if all_ships[connected_chat_id]['connected_chat'] != f'{chat_id}':
        all_ships[chat_id]['connected_chat'] = 'null'
        all_ships[chat_id]['blocked'] = False
        await bot.send_message(chat_id,
                               f"Не удалось выстрелить. Попробуйте установить связь ещё раз.")
        return

    all_ships[connected_chat_id]['ship_health'] = clamp(
        all_ships[connected_chat_id]['ship_health'] - random.randint(1, 25), 0, 100)

    connected_chat = await bot.get_chat(connected_chat_id)

    if type(connected_chat.title) != NoneType:
        await bot.send_message(chat_id,
                               f"Мы попали в корабль {all_ships[connected_chat_id]['ship_name']} чата {connected_chat.title} 🔫.\nПрочность корабля противника: {all_ships[connected_chat_id]['ship_health']}%")
    else:
        await bot.send_message(chat_id,
                               f"Мы попали в корабль {all_ships[connected_chat_id]['ship_name']} 🔫.\nПрочность корабля противника: {all_ships[connected_chat_id]['ship_health']}%")

    if type(chat.title) != NoneType:
        await bot.send_message(connected_chat_id,
                               f"Корабль {all_ships[chat_id]['ship_name']} чата {chat.title} попал в нас! 💥\nПрочность корабля: {all_ships[connected_chat_id]['ship_health']}%")
    else:
        await bot.send_message(connected_chat_id,
                               f"Корабль {all_ships[chat_id]['ship_name']} попал в нас! 💥\nПрочность корабля: {all_ships[connected_chat_id]['ship_health']}%")

    damage_all_crew(connected_chat_id, 1, 5)
    if await destroy_cannon(connected_chat_id, 0.25):
        await bot.send_message(chat_id, "Орудие противника повреждено.")
    if await destroy_engine(connected_chat_id, 0.25):
        await bot.send_message(chat_id, "Двигатель противника поврежден.")
    if await destroy_fuel_tank(connected_chat_id, 0.25):
        await bot.send_message(chat_id, "Топливный бак противника поврежден.")
    if random.random() < 0.1 and not all_ships[connected_chat_id]["fire"]:
        all_ships[connected_chat_id]["fire"] = True
        await fire_func(connected_chat_id)


# Выстрел
@dp.message(Command("выстрел"))
async def shot_command(message: Message, command: CommandObject):
    chat_id = message.chat.id
    if not await can_proceed(message):
        return
    if all_ships[chat_id]['cannon_overheated']:
        await message.answer("⚠️ Перегрев орудия! Попробуйте через пару секунд.")
        return
    if int(all_ships[chat_id]['bullets']) < 1:
        await message.answer("⚠️ У нас нет снарядов!\nСоздайте их в меню создания (/создание)")
        return
    all_ships[chat_id]['cannon_overheated'] = True
    if command.args == "корабль" or command.args == "Корабль":
        # Симуляция выстрела в корабль
        value = 0.7 if not all_ships[chat_id]['cannon_damaged'] else 0.9
        if random.random() < value:
            await message.answer(f"{random_bad_shot_text()} ⚠️")
        else:
            if all_ships[chat_id]['connected_chat'] == 'null':
                await message.answer("⚠️ Не получилось выстрелить.\nУстановите связь, используя команду /связь")
                return

            await shot(chat_id, message.chat, int(all_ships[chat_id]['connected_chat']))
    else:
        if not all_ships[chat_id]['alien_attack']:
            await message.answer("⚠️ Нельзя стрелять, когда нет опасностей")
            return
        # Симуляция выстрела в пришельцев
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
        return None
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
                if type(random_chat_id) == NoneType:
                    print("Не удалось подключиться, пробую ещё раз")
                    await connect(chat_id, title, args)
                    return
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
                all_ships[chat_id]['blocked'] = True
                connected_chat_id = int(all_ships[chat_id]['connected_chat'])
                if connected_chat_id == chat_id:
                    all_ships[chat_id]['blocked'] = False
                    await bot.send_message(connected_chat_id, f"Не удалось найти ближайший корабль. Попробуйте позже.")
                    return
                if is_chat_banned(connected_chat_id):
                    all_ships[chat_id]['connected_chat'] = 'null'
                    all_ships[chat_id]['blocked'] = False
                    await bot.send_message(chat_id,
                                           f"Не удалось соединиться с кораблём. Выбранный корабль был заблокирован.")
                    return
                if not is_chat_active(connected_chat_id):
                    all_ships[chat_id]['connected_chat'] = 'null'
                    all_ships[chat_id]['blocked'] = False
                    await bot.send_message(chat_id, f"Не удалось соединиться с кораблём. Соединение прервано")
                    return
                if all_ships[connected_chat_id]['connected_chat'] != f'{chat_id}':
                    all_ships[chat_id]['connected_chat'] = 'null'
                    all_ships[chat_id]['blocked'] = False
                    await bot.send_message(chat_id,
                                           f"Не удалось подключиться к выбранному кораблю. Попробуйте установить связь ещё раз.")
                    return
                try:
                    await bot.send_message(connected_chat_id, f"Получено сообщение: {args}")
                    await bot.send_message(chat_id, f"Отправлено сообщение: {args}")
                except TelegramRetryAfter:
                    print("Наверное Too Many Requests. ")
                    all_ships[chat_id]['blocked'] = False

                await asyncio.sleep(2)
                all_ships[chat_id]['blocked'] = False

    except ValueError:
        await bot.send_message(chat_id, "Не удалось связаться с кораблём.\nПри передаче данных связь была потеряна⚠️")


# Команда для связи с другими кораблями
@dp.message(Command("связь", "с"))
async def connect_to_other_ship(message: Message, command: CommandObject):
    chat_id = message.chat.id
    print(f"Чат {chat_id} пытается установить связь")
    if not await can_proceed(message):
        return
    await connect(chat_id, message.chat.title, command.args)


@dp.message(Command("!связь", "!с"))
async def disconnect_from_other_ship(message: Message):
    chat_id = message.chat.id
    if not await can_proceed(message):
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
    stop_game(chat_id)
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


# Функция для повреждения двигателя
async def destroy_engine(chat_id: int, chance: float) -> bool:
    # Если повезет, то ломаем двигатель
    if random.random() < chance and not all_ships[chat_id]["engine_damaged"]:
        all_ships[chat_id]["engine_damaged"] = True
        await bot.send_message(chat_id, "Двигатель поврежден, максимальная скорость снижена! ⚠️")
        return True
    return False


# Функция для повреждения топливного бака
async def destroy_fuel_tank(chat_id: int, chance: float) -> bool:
    # Если повезет, то ломаем бак
    if random.random() < chance and not all_ships[chat_id]["fuel_tank_damaged"]:
        all_ships[chat_id]["fuel_tank_damaged"] = True
        await bot.send_message(chat_id, "Пробит топливный бак! ⚠️")
        return True
    return False


# Функция для повреждения орудия
async def destroy_cannon(chat_id: int, chance: float) -> bool:
    # Если повезет, то ломаем орудие
    if random.random() < chance and not all_ships[chat_id]["cannon_damaged"]:
        all_ships[chat_id]["cannon_damaged"] = True
        await bot.send_message(chat_id, "Орудие повреждено, точность стрельбы снижена! ⚠️")
        return True
    return False


# Механика пожаров
async def fire_func(chat_id: int):
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

    await bot.send_message(chat_id, "🔥")
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
            damage_all_crew(chat_id, 2, 5)
        if random.random() > 0.25:
            all_ships[chat_id]["oxygen"] -= random.randint(2, 5)

        await destroy_engine(chat_id, 0.05)
        await destroy_fuel_tank(chat_id, 0.05)

        check_data(all_ships[chat_id], chat_id)

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
    if not is_chat_active(chat_id):
        print("Игра не активна")
        return
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
    if callback.from_user.id != all_ships[chat_id]['crew'][0]['user_id']:
        await callback.answer("Только капитан может сделать это ⚠️")
        return
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
    state["oxygen"] = clamp(state["oxygen"], 0, 100)
    state["extinguishers"] = clamp(state["extinguishers"], 0, 256)
    state["bullets"] = clamp(state["bullets"], 0, 128)
    all_ships[chat_id] = state


# Функция для сохранения данных
def check_and_save_data(state: dict, chat_id: int):
    check_data(state, chat_id)
    chat_utils.save_chat_state(chat_id, state)


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
        if not all_ships[chat_id]['alien_attack']:
            return
        if int(all_ships[chat_id]['ship_health']) < 1:
            all_ships[chat_id]['alien_attack'] = False
            await bot.send_message(chat_id, "Пришельцы улетели! 👽")
            break
        if random.random() < 0.2:
            all_ships[chat_id]['ship_health'] = clamp(all_ships[chat_id]['ship_health'] - random.randint(1, 10), 0, 100)
            await bot.send_message(chat_id,
                                   f"Пришельцы попали в нас 👽!\nПрочность корабля: {all_ships[chat_id]['ship_health']}%")
            if random.random() < 0.25 and not all_ships[chat_id]["fire"]:
                # Пожар от выстрела противника
                all_ships[chat_id]["fire"] = True
                await fire_func(chat_id)

            await destroy_engine(chat_id, 0.1)
            await destroy_fuel_tank(chat_id, 0.1)
            await destroy_cannon(chat_id, 0.1)

        await asyncio.sleep(5)


# Создание случайных событий на планете или в космосе.
async def game_loop_events(chat_id: int):
    # Небольшая задержка в начале игры
    await asyncio.sleep(5)
    while is_chat_active(chat_id):
        if all_ships[chat_id]["on_planet"]:
            # события на планетах
            if random.random() < 0.15:
                # Ресурсы на планете
                value = random.randint(50, 125)
                all_ships[chat_id]["resources"] += value
                await bot.send_message(chat_id, f"Мы нашли полезные ресурсы!\nПолучено {value} ресурсов")
            if random.random() < 0.05:
                # Аномалия на планете
                if not int(all_ships[chat_id]["ship_health"]) == 0:
                    value = random.randint(1, 3)
                    all_ships[chat_id]["ship_health"] = clamp(all_ships[chat_id]["ship_health"] - value, 0, 100)
                    await bot.send_message(chat_id,
                                           f"Аномалия на планете. Корабль поврежден!\nПрочность корабля: {all_ships[chat_id]["ship_health"]}%")
                    await destroy_engine(chat_id, 0.2)
        else:
            # события в космосе
            if random.random() < 0.02:
                # Космический мусор
                if not int(all_ships[chat_id]["ship_health"]) == 0:
                    value = random.randint(1, 3)
                    all_ships[chat_id]["ship_health"] -= value
                    await bot.send_message(chat_id,
                                           f"Мы столкнулись с космическим мусором!\nПрочность корабля: {all_ships[chat_id]["ship_health"]}%")
                    await destroy_engine(chat_id, 0.2)
            if random.random() < 0.02:
                # Космическая аномалия
                all_ships[chat_id]["distance"] = 0
                all_ships[chat_id]["next_planet_name"] = random.choice(PLANETS)
                await bot.send_message(chat_id, f"Космическая аномалия!\nМы сбились с курса")
        # Здесь могут быть универсальные события
        if random.random() < 0.01 and not all_ships[chat_id]["alien_attack"]:
            # Атака пришельцев
            if not int(all_ships[chat_id]["ship_health"]) == 0:
                await alien_attack(chat_id)

        if random.random() < 0.01 and not all_ships[chat_id]["fire"]:
            # пожар
            all_ships[chat_id]["fire"] = True
            await fire_func(chat_id)

        # Убираем перегрев орудия
        if all_ships[chat_id]['cannon_overheated']:
            all_ships[chat_id]['cannon_overheated'] = False

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
                await bot.send_message(chat_id, "⚠️ Корпус разрушен, утечка воздуха. Требуется ремонт.")
                warned_of_air_leak = True

            damage_all_crew(chat_id, 1, 3)
        else:
            if warned_of_air_leak:
                warned_of_air_leak = False

        # уменьшаем здоровье если нет воздуха
        if all_ships[chat_id]["oxygen"] < 1:
            if not warned_of_empty_air:
                await bot.send_message(chat_id, "⚠️ Закончился воздух. Требуется ремонт.")
                warned_of_empty_air = True

            damage_all_crew(chat_id, 1, 5)
        else:
            if warned_of_empty_air:
                warned_of_empty_air = False

        await check_all_crew(chat_id)
        # завершаем игру если здоровье экипажа на нуле
        if not is_crew_alive(chat_id):
            await bot.send_message(chat_id, "Игра завершена!\nЭкипаж выведен из строя. ⚠️")
            stop_game(chat_id)
            break
        # Проверка данных во избежание проблем
        check_data(all_ships[chat_id], chat_id)
        # Ожидаем 5 секунд перед началом следующей итерации
        await asyncio.sleep(5)


# Если добавляют бота, отправляем приветствие
@dp.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=IS_NOT_MEMBER >> IS_MEMBER))
async def admin_handler(event: ChatMemberUpdated):
    await event.answer(
        f"Привет! Добро пожаловать в открытый космос 💫🪐☄️\nНачать игру можно командой /играть. \nПодробная информация будет здесь: {github_link}\n\n⚠️ Возможно, боту понадобятся права администратора. Проверьте их, иначе он не сможет отвечать на команды")


# Если бота удаляют (по каким-то причинам), то принудительно завершаем игру.
@dp.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=IS_MEMBER >> IS_NOT_MEMBER))
async def not_member_handler(event: ChatMemberUpdated):
    chat_id = event.chat.id
    print(f"Бота удалили из чата {event.chat.id}, по возможности завершаем игру.")
    stop_game(chat_id)


def is_it_admin(user_id: int) -> bool:
    return user_id in ADMINS


# Команда администратора. Блокирует чат
@dp.message(Command("adm:заблокировать"))
async def adm_block(message: Message, command: CommandObject):
    if not is_it_admin(message.from_user.id):
        return
    if type(command.args) == NoneType:
        await message.answer("Вы не указали ID.")
        return
    try:
        chat = int(command.args)
        BLOCKED_CHATS.append(chat)
        CONFIG['blacklist'] = BLOCKED_CHATS
        stop_game(chat)
        save_config(CONFIG)
        await message.answer(f"Чат {chat} заблокирован ✅")
    except ValueError as e:
        print(f"Не удалось заблокировать чат: {e} ")
        await message.answer(f"Не получилось заблокировать чат 🚫\n{e}")


# Команда администратора. Разблокирует чат
@dp.message(Command("adm:разблокировать"))
async def adm_unlock(message: Message, command: CommandObject):
    if not is_it_admin(message.from_user.id):
        return
    if type(command.args) == NoneType:
        await message.answer("Вы не указали ID.")
        return
    try:
        chat = int(command.args)
        BLOCKED_CHATS.remove(chat)
        CONFIG['blacklist'] = BLOCKED_CHATS
        save_config(CONFIG)
        await message.answer(f"Чат {chat} разблокирован ✅")
    except ValueError as e:
        print(f"Не удалось разблокировать чат: {e} ")
        await message.answer(f"Не получилось разблокировать чат 🚫\n{e}")


@dp.message(Command("adm:пожар"))
async def adm_fire(message: Message, command: CommandObject):
    if not is_it_admin(message.from_user.id):
        return
    if type(command.args) == NoneType:
        await message.answer("Вы не указали ID.")
        return
    try:
        chat = int(command.args)
        all_ships[chat]["fire"] = True
        await message.answer(f"Корабль в чате {chat} горит ✅")
        await fire_func(chat)
    except ValueError as e:
        print(f"Не получилось сжечь корабль : {e} ")
        await message.answer(f"Не получилось сжечь корабль 🚫\n{e}")


# Команда администратора. Останавливает игру в чате
@dp.message(Command("adm:стоп"))
async def adm_stop(message: Message, command: CommandObject):
    if not is_it_admin(message.from_user.id):
        return
    if type(command.args) == NoneType:
        await message.answer("Вы не указали ID.")
        return
    try:
        chat = int(command.args)
        if is_chat_active(chat):
            stop_game(chat)
            await message.answer(f"Игра в чате {chat} остановлена ✅")
        else:
            await message.answer(f"Не получилось остановить игру в чате {chat} 🚫\nПроверьте ID.")
    except ValueError as e:
        await message.answer(f"Не получилось остановить игру в чате. 🚫\n{e}")


# Функция, которая вызывается при запуске бота
async def init():
    try:
        dp.include_routers(start_help_info_handler.router)
        await bot(DeleteWebhook(drop_pending_updates=True))
        await dp.start_polling(bot)
    except CancelledError:
        print("Остановка.")
    except TelegramNetworkError as e:
        print(f"Возникли некоторые проблемы. Проверьте подключение к интернету. Это всё, что нам известно: \n{e}")


# Запуск бота
if __name__ == "__main__":
    print(f"Открытый космос бот запущен.")
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(init())
