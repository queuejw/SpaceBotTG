# ссылка на наш GitHUb
import random

from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message

from bot.bot_data import send_message, bot
from bot.config import BLOCKED_CHATS
from utils.util import clamp

github_link = "https://github.com/queuejw/SpaceBotTG"

all_ships = {}


# Вернет True, если корабль чата есть в словаре.
def is_chat_active(chat_id: int) -> bool:
    return chat_id in all_ships


# Удаляет чат из all_ships
def remove_chat_from_all_ships(chat_id: int):
    if is_chat_active(chat_id):
        all_ships.pop(chat_id)


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


# Получить роль одного конкретного человека
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


def get_random_crew(data: list, captain: dict) -> dict:
    user: dict = random.choice(data)
    if user == captain:
        # Совпадение, пробуем ещё раз
        return get_random_crew(data, captain)
    return user


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


async def delete_message(chat_id: int, message_id: int):
    try:
        await bot.delete_message(chat_id, message_id)
    except TelegramBadRequest as e:
        print(f"Не получилось удалить сообщение. Это всё, что нам известно: {e}")


# Проверяем здоровье у всех участников. Если на нуле - удаляем. Если погибает капитан, передаем роль случайному участнику
async def check_all_crew(chat_id: int):
    index = 0
    print("проверка игроков")
    print(all_ships[chat_id]['crew'])
    data: list = all_ships[chat_id]['crew']
    for i in data:
        print(i)
        if i['user_health'] < 1:
            if i['user_role'] == 1:
                print("Передаем роль капитана случайному участнику")
                if len(data) > 1:
                    data.remove(i)
                    random_crew = get_random_crew(data, i)
                    print(f"выбран для передачи прав игрок {random_crew}")
                    if random_crew['user_role'] == 1:
                        print("выбранный игрок уже капитан.")

                    data[0] = random_crew
                    data[0]['user_role'] = 1

                    await send_message(chat_id,
                                       f"Капитан {i['user_name']} погиб! 😵\nВстречайте нового капитана: {data[0]['user_name']} 👑")
                else:
                    print("недостаточно участников, чтобы передать роль")
                    data.remove(i)
                    await send_message(chat_id,
                                       f"Капитан {i['user_name']} погиб! 😵")
                print("получилась такая каша")
                print(data)
            else:
                print("Какой-то игрок погиб")
                if len(data) > 1:
                    print(i)
                    data.remove(i)
                    await send_message(chat_id,
                                       f"{get_crew_role_by_num(int(i['user_role']))} {i['user_name']} погиб 😵")
                else:
                    print("недостаточно участников. невозможно удалить участника")
        index += 1
    all_ships[chat_id]['crew'] = data
    print("конец проверки")


# Если общее здоровье на нуле, то вернет False
def is_crew_alive(chat_id: int) -> bool:
    return get_total_crew_health(chat_id) > 1


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
