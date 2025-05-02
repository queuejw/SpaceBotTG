print("Добро пожаловать в открытый космос бот. Подождите немного ...")
# открытый космос бот игра от @queuejw
import asyncio
import logging
import sys
from asyncio import CancelledError

from aiogram.exceptions import TelegramNetworkError
from aiogram.methods import DeleteWebhook

from bot.bot_data import dp, bot
from bot.routers import router_list


async def init():
    try:
        for r in router_list:
            dp.include_router(r)
        await bot(DeleteWebhook(drop_pending_updates=True))
        await dp.start_polling(bot)
    except CancelledError:
        print("Остановка.")
    except TelegramNetworkError as e:
        print(f"Возникли некоторые проблемы. Проверьте подключение к интернету. Это всё, что нам известно: \n{e}")


# Запуск бота
if __name__ == "__main__":
    print(f"открытый космос бот запущен.")
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(init())
