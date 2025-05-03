# Тушение пожаров
import asyncio
import random

from aiogram import F, Router
from aiogram.types import CallbackQuery

from bot.messages import send_message
from bot.shared import is_chat_active, all_ships, exist_user_by_id, get_user_by_id

router = Router()


# Механика тушения пожаров
@router.callback_query(F.data == "fire_callback")
async def fire_callback(callback: CallbackQuery):
    print("Обработка тушения пожара")
    chat_id = callback.message.chat.id
    if not is_chat_active(chat_id):
        print("Игра не активна")
        await callback.answer()
        return
    if not exist_user_by_id(chat_id, callback.from_user.id):
        await callback.answer("Вы не член экипажа")
        return
    role = int(get_user_by_id(chat_id, callback.from_user.id)['user_role'])
    if role != 2 or role != 1:
        await callback.answer("⚠️ Только инженер или капитан может тушить пожар")
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
    await send_message(chat_id, "Тушим корабль ... 🧯")
    for _ in range(random.randint(4, 7)):
        await asyncio.sleep(1)
    if not is_chat_active(chat_id):
        print("Игра не активна")
        return
    await send_message(chat_id, "Пожар потушен!🧯✅")
    all_ships[chat_id]['extinguishers'] -= 1
    all_ships[chat_id]["blocked"] = False
    all_ships[chat_id]["fire"] = False
