from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, FSInputFile

from bot.messages import send_message
from bot.shared import github_link

router = Router()


# Функция, которая вызывается командой /start
@router.message(CommandStart())
async def command_start_handler(message: Message):
    text = (
        "Привет! Добро пожаловать на борт!👽\n"
        "Этот бот поможет вам весело провести время в открытом космосе вместе с друзьями!👨‍👨‍👦\n"
        "\n"
        "Путешествуйте по планетам, ищите друзей из других чатов, собирайте ресурсы и попробуйте выжить как можно дольше!💼\n"
        "\n"
        "Введи /играть , чтобы начать путешествие в мир космоса!🚀\n"
        "/инфо для информации о боте."
    )
    image = FSInputFile("img/main.jpg")
    await message.answer_photo(image, caption=text)


# Функция, которая вызывается командой /инфо
@router.message(Command("инфо", "info"))
async def info(message: Message):
    text = (
        "открытый космос - игровой бот для вашего чата.👽\n"
        "находится в разработке, не все функции работают правильно.\n"
        "последнее обновление: 01.05.25\n"
        "сделал @queuejw\n"
        f"подробная информация и исходный код бота: {github_link}"
    )
    image = FSInputFile("img/main.jpg")
    await message.answer_photo(image, caption=text)


# Функция, которая вызывается командой /помощь.
@router.message(Command("помощь", "help"))
async def commands(message: Message):
    text = (
        f"Команды бота будут написаны здесь: {github_link}\n"
        "\n"
        "Путешествуйте по планетам, чтобы собирать ресурсы. С помощью ресурсов вы сможете ремонтировать корабль, создавать предметы и выполнять многие действия.\nИщите новых друзей из других чатов, используя команду /связь"
    )
    await send_message(message.chat.id, text)
