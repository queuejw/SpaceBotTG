# открытый космос бот игра от @queuejw
print("Добро пожаловать в открытый космос бот. Подождите немного ...")

import asyncio
import logging
import sys

from bot.launch import init

# Запуск бота
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    print(f"открытый космос бот запущен.")
    asyncio.run(init())
