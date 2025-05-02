# Самоуничтожение

from aiogram import Router, F
from aiogram.types import CallbackQuery

from bot.game_functions import stop_game
from bot.messages import delete_message, send_message
from bot.shared import all_ships, is_chat_active

router = Router()


async def self_destruction_func(chat_id):
    text = (
        "💥💥💥💥💥\n"
        "Игра завершена! Корабль самоуничтожился."
    )
    stop_game(chat_id)
    await send_message(chat_id, text)


@router.callback_query(F.data.startswith("self_destruction_"))
async def self_destruction_callback(callback: CallbackQuery):
    print("Обработка самоуничтожения")
    chat_id = callback.message.chat.id
    if callback.from_user.id != all_ships[chat_id]['crew'][0]['user_id']:
        await callback.answer("Только капитан может сделать это ⚠️")
        return
    if not is_chat_active(chat_id):
        print("Игра не активна")
        await callback.answer("Игра не активна")
        return
    if callback.data == "self_destruction_cancel":
        print("Отмена самоуничтожения")
        await callback.answer("Отмена самоуничтожения")
        await delete_message(callback.message.chat.id, callback.message.message_id)

    elif callback.data == "self_destruction_continue":
        print(f"Начинаем самоуничтожение в чате {chat_id}")
        await callback.answer("САМОУНИЧТОЖЕНИЕ")
        await delete_message(callback.message.chat.id, callback.message.message_id)
        await self_destruction_func(callback.message.chat.id)
    await callback.answer()
