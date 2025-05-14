from types import NoneType

from bot.bot_data import bot
from bot.messages import send_message
from bot.shared import all_ships, is_chat_active


async def send_notification_to_connected_chat(text: str, chat_id: int):
    if all_ships[chat_id]['connected_chat'] != 'null':
        c_chat_id = int(all_ships[chat_id]['connected_chat'])
        if is_chat_active(c_chat_id):
            chat = await bot.get_chat(chat_id)
            if type(chat.title) != NoneType:
                await send_message(c_chat_id,
                                   f"Корабль {all_ships[chat_id]['ship_name']} чата {chat.title} {text}")
            else:
                await send_message(c_chat_id,
                                   f"Корабль {all_ships[chat_id]['ship_name']} {text}")
