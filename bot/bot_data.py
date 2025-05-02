from aiogram import Dispatcher, Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

import bot.config as config

if len(config.CONFIG) == 0:
    print("Проверьте файл конфигурации.")
    exit(1)

if config.TOKEN == "":
    print("Невозможно продолжить запуск. Проверьте токен в файле конфигурации")
    exit(1)

dp = Dispatcher()
bot = Bot(token=config.TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
