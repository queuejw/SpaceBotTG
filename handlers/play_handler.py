import asyncio

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from bot import chat_utils
from bot.game import game_loop, game_loop_events, game_loop_planet_change, cannon_loop
from bot.messages import send_message
from bot.shared import all_ships, is_chat_banned, is_chat_active
from utils.crew import get_default_crew

router = Router()


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
    loaded_state['blocked'] = False
    all_ships[chat_id] = loaded_state
    chat_utils.save_chat_state(chat_id, all_ships[chat_id])


def create_tasks(chat_id: int):
    asyncio.create_task(game_loop(chat_id))
    asyncio.create_task(game_loop_planet_change(chat_id))
    asyncio.create_task(game_loop_events(chat_id))
    asyncio.create_task(cannon_loop(chat_id))


# Создание корабля для чата
@router.message(Command("играть"))
async def play(message: Message):
    chat_id = message.chat.id
    if is_chat_banned(chat_id):
        await send_message(chat_id,
                           "🪐❌ Ваш чат был заблокирован. \nЕсли вы считаете, что это была ошибка, свяжитесь со мной: @queuejw")
        return
    if is_chat_active(chat_id):
        await send_message(chat_id,
                           "Не удалось запустить корабль в космос:\nИгра активна. ⚠️")
        return
    # Создаем корабль для этого чата
    create_new_ship(message)
    create_tasks(chat_id)
    text = (
        "🚀Игра началась!\n"
        "Введите команду /помощь , чтобы узнать все команды бота.\n"
        "Добавить новых членов экипажа можно командой /добавить . Посмотрите список команд.\n"
    )
    if not all_ships[chat_id]['default']:
        text = text + "ℹ️ Загружено последнее сохранение"
    else:
        text = text + f"\nНазвание Вашего корабля: {all_ships[chat_id]['ship_name']}"
        all_ships[chat_id]['default'] = False

    await send_message(chat_id, text)
