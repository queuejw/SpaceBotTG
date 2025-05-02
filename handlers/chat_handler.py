from aiogram import Router
from aiogram.filters import ChatMemberUpdatedFilter, IS_MEMBER, IS_NOT_MEMBER
from aiogram.types import ChatMemberUpdated

from bot.game_functions import stop_game
from bot.shared import github_link

router = Router()


# Если добавляют бота, отправляем приветствие
@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=IS_NOT_MEMBER >> IS_MEMBER))
async def admin_handler(event: ChatMemberUpdated):
    await event.answer(
        f"Привет! Добро пожаловать в открытый космос 💫🪐☄️\nНачать игру можно командой /играть. \nПодробная информация будет здесь: {github_link}\n\n⚠️ Возможно, боту понадобятся права администратора. Проверьте их, иначе он не сможет отвечать на команды")


# Если бота удаляют (по каким-то причинам), то принудительно завершаем игру.
@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=IS_MEMBER >> IS_NOT_MEMBER))
async def not_member_handler(event: ChatMemberUpdated):
    chat_id = event.chat.id
    print(f"Бота удалили из чата {event.chat.id}, по возможности завершаем игру.")
    stop_game(chat_id)
