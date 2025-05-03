# ссылка на наш GitHUb
import random

from aiogram.types import Message

from bot.config import BLOCKED_CHATS
from utils.roles import get_role_name_by_num
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


#  Вернет игрока, если id пользователя есть в списке
def get_user_by_id(chat_id: int, user_id: int) -> dict:
    for i in all_ships[chat_id]['crew']:
        if i['user_id'] == user_id:
            return i
    return {}


#  Вернет игрока, если имя пользователя есть в списке
def get_user_by_name(chat_id: int, user_name: str) -> dict:
    for i in all_ships[chat_id]['crew']:
        if i['user_name'] == user_name:
            return i
    return {}


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


# Если общее здоровье на нуле, то вернет False
def is_crew_alive(chat_id: int) -> bool:
    return get_total_crew_health(chat_id) > 1


# Функция для получения текста сообщения экипажа
def get_crew_text(chat_id) -> str:
    text = f"Экипаж корабля {all_ships[chat_id]['ship_name']}:\n\n"
    for i in all_ships[chat_id]['crew']:
        text = text + f"👤 {i['user_name']} : {get_role_name_by_num(i['user_role'])}\n"
    return text


def get_crew_str(item: dict) -> str:
    return (
        f"👤 {item['user_name']}:\n"
        "=====\n"
        f"⭐ Роль: {get_role_name_by_num(item['user_role'])}\n"
        f"❤️ Здоровье: {item['user_health']}%\n"
    )
