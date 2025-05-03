# Создание предметов
from aiogram import Router, F
from aiogram.types import CallbackQuery

from bot.messages import delete_message, send_message
from bot.save_game import check_data
from bot.shared import is_chat_active, exist_user_by_id, all_ships, get_user_by_id

router = Router()


# Механика создания предметов
@router.callback_query(F.data.startswith("craft_"))
async def craft_callback(callback: CallbackQuery):
    print("Обработка создания предметов")
    chat_id = callback.message.chat.id
    if not is_chat_active(chat_id):
        print("Игра не активна")
        await callback.answer()
        return
    if not exist_user_by_id(chat_id, callback.from_user.id):
        await callback.answer("Вы не член экипажа")
        return
    role = int(get_user_by_id(chat_id, callback.from_user.id)['user_role'])
    if role != 2 and role != 1:
        await callback.answer("⚠️ Только инженер или капитан может создавать предметы")
        return
    if callback.data == "craft_exit":
        print("Отмена создания предметов")
        await callback.answer("Отмена создания предметов")
        await delete_message(callback.message.chat.id, callback.message.message_id)

    elif callback.data == "craft_extinguisher":
        if int(all_ships[chat_id]['resources']) < 100:
            await callback.answer("Недостаточно ресурсов ⚠️")
            return
        all_ships[chat_id]['resources'] -= 100
        all_ships[chat_id]['extinguishers'] += 1
        await callback.answer("Создан огнетушитель")
        await send_message(chat_id, "Создан огнетушитель ✅\n+ 1 огнетушитель")

    elif callback.data == "craft_bullet":
        if int(all_ships[chat_id]['resources']) < 50:
            await callback.answer("Недостаточно ресурсов ⚠️")
            return
        all_ships[chat_id]['resources'] -= 50
        all_ships[chat_id]['bullets'] += 1
        await callback.answer("Создан снаряд")
        await send_message(chat_id, "Создан снаряд ✅\n+ 1 снаряд")

    elif callback.data == "craft_fuel":
        if int(all_ships[chat_id]['resources']) < 75:
            await callback.answer("Недостаточно ресурсов ⚠️")
            return
        if int(all_ships[chat_id]['ship_fuel']) > 99:
            await callback.answer("Корабль не нуждается в топливе ⚠️")
            return
        all_ships[chat_id]['resources'] -= 75
        all_ships[chat_id]['ship_fuel'] += 10
        check_data(all_ships[chat_id], chat_id)
        await callback.answer("Создано топливо.")
        await send_message(chat_id, "Создано топливо ✅\n+ 10% топлива")

    await callback.answer()
