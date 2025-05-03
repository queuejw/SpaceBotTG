import random
from types import NoneType

from aiogram import Router
from aiogram.filters import CommandObject, Command
from aiogram.types import Chat, Message

from bot.bot_data import bot
from bot.game_functions import destroy_cannon, destroy_engine, destroy_fuel_tank, fire_func
from bot.messages import send_message
from bot.shared import all_ships, is_chat_active, can_proceed, is_chat_banned, damage_all_crew, get_user_by_id
from utils.util import clamp

router = Router()

overheated = False


# Случайный текст для неудачного выстрела
def random_bad_shot_text() -> str:
    variants = ["Мимо!", "Промах!", "Не попал!", "Рикошет!", "Не пробил!", "Нет пробития!"]
    return random.choice(variants)


async def shot(chat_id: int, chat: Chat, connected_chat_id: int):
    if is_chat_banned(connected_chat_id):
        all_ships[chat_id]['connected_chat'] = 'null'
        all_ships[chat_id]['blocked'] = False
        await send_message(chat_id,
                           f"Не удалось выстрелить. Другой корабль был заблокирован.")
        return
    if not is_chat_active(connected_chat_id):
        all_ships[chat_id]['connected_chat'] = 'null'
        all_ships[chat_id]['blocked'] = False
        await send_message(chat_id, f"Не удалось выстрелить. Соединение с другим кораблем прервано.")
        return
    if all_ships[connected_chat_id]['connected_chat'] != f'{chat_id}':
        all_ships[chat_id]['connected_chat'] = 'null'
        all_ships[chat_id]['blocked'] = False
        await send_message(chat_id,
                           f"Не удалось выстрелить. Попробуйте установить связь ещё раз.")
        return

    all_ships[connected_chat_id]['ship_health'] = clamp(
        all_ships[connected_chat_id]['ship_health'] - random.randint(1, 25), 0, 100)

    connected_chat = await bot.get_chat(connected_chat_id)

    if type(connected_chat.title) != NoneType:
        await send_message(chat_id,
                           f"Мы попали в корабль {all_ships[connected_chat_id]['ship_name']} чата {connected_chat.title} 🔫.\nПрочность корабля противника: {all_ships[connected_chat_id]['ship_health']}%")
    else:
        await send_message(chat_id,
                           f"Мы попали в корабль {all_ships[connected_chat_id]['ship_name']} 🔫.\nПрочность корабля противника: {all_ships[connected_chat_id]['ship_health']}%")

    if type(chat.title) != NoneType:
        await send_message(connected_chat_id,
                           f"Корабль {all_ships[chat_id]['ship_name']} чата {chat.title} попал в нас! 💥\nПрочность корабля: {all_ships[connected_chat_id]['ship_health']}%")
    else:
        await send_message(connected_chat_id,
                           f"Корабль {all_ships[chat_id]['ship_name']} попал в нас! 💥\nПрочность корабля: {all_ships[connected_chat_id]['ship_health']}%")

    damage_all_crew(connected_chat_id, 1, 5)
    if await destroy_cannon(connected_chat_id, 0.25):
        await send_message(chat_id, "Орудие противника повреждено.")
    if await destroy_engine(connected_chat_id, 0.25):
        await send_message(chat_id, "Двигатель противника поврежден.")
    if await destroy_fuel_tank(connected_chat_id, 0.25):
        await send_message(chat_id, "Топливный бак противника поврежден.")
    if random.random() < 0.1 and not all_ships[connected_chat_id]["fire"]:
        all_ships[connected_chat_id]["fire"] = True
        await fire_func(connected_chat_id)


# Выстрел
@router.message(Command("выстрел", "огонь", ""))
async def shot_command(message: Message, command: CommandObject):
    chat_id = message.chat.id
    if not await can_proceed(message):
        return
    role = int(get_user_by_id(chat_id, message.from_user.id)['user_role'])
    if role != 3 and role != 1:
        await send_message(chat_id, "⚠️ Только стрелок или капитан может стрелять из орудий")
        return
    global overheated
    if all_ships[chat_id]['cannon_overheated']:
        if not overheated:
            await message.answer("⚠️ Перегрев орудия! Попробуйте через пару секунд.")
        overheated = True
        return
    if int(all_ships[chat_id]['bullets']) < 1:
        await message.answer("⚠️ У нас нет снарядов!\nСоздайте их в меню создания (/создание)")
        return
    if command.args == "корабль" or command.args == "Корабль" or command.args == "к":
        # Симуляция выстрела в корабль
        if all_ships[chat_id]['connected_chat'] == 'null':
            await message.answer("⚠️ Не получилось выстрелить.\nУстановите связь, используя команду /связь")
            return
        value = 0.6 if not all_ships[chat_id]['cannon_damaged'] else 0.8
        if role == 1:
            value += 0.1

        all_ships[chat_id]['bullets'] = clamp(int(all_ships[chat_id]['bullets']) - 1, 0, 128)
        all_ships[chat_id]['cannon_overheated'] = True
        overheated = False

        if random.random() < value:
            await message.answer(f"{random_bad_shot_text()} ⚠️")
        else:
            await shot(chat_id, message.chat, int(all_ships[chat_id]['connected_chat']))
    else:
        if not all_ships[chat_id]['alien_attack']:
            await message.answer("⚠️ Нельзя стрелять, когда нет опасностей")
            return
        # Симуляция выстрела в пришельцев
        value = 0.5 if not all_ships[chat_id]['cannon_damaged'] else 0.75
        if role == 1:
            value += 0.1

        all_ships[chat_id]['bullets'] = clamp(int(all_ships[chat_id]['bullets']) - 1, 0, 128)
        all_ships[chat_id]['cannon_overheated'] = True

        if random.random() < value:
            await message.answer(f"{random_bad_shot_text()} ⚠️")
        else:
            all_ships[chat_id]['alien_attack'] = False
            await message.answer("Успешный выстрел! ✅\nПришельцы уничтожены.")
