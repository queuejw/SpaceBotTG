from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

router = Router()

# ссылка на наш GitHUb
github_link = "https://github.com/queuejw/SpaceBotTG"


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
    await message.answer(text)


# Функция, которая вызывается командой /инфо
@router.message(Command("инфо"))
async def info(message: Message):
    text = (
        "открытый космос - игровой бот для вашего чата.👽\n"
        "находится в разработке, не все функции работают правильно.\n"
        "последнее обновление: 06.04.25\n"
        "сделал @queuejw\n"
        f"исходный код бота: {github_link}"
    )
    await message.answer(text)


# Функция, которая вызывается командой /помощь. Выводит текст со всеми возможными командами и их описанием.
@router.message(Command('помощь'))
async def commands(message: Message):
    text = (
        "Команды бортового компьютера:\n"
        "\n"
        "/компьютер (или /к) - информация о корабле\n"
        "/склад - информация о предметах на корабле\n"
        "/создание - выбор и создание предметов\n"
        "/лететь [планета] - лететь на указанную планету. Если не указать, то будет выбрана следующая планета\n"
        "/покинуть - покинуть планету\n"
        "/ремонт - немного лечит экипаж и немного увеличивает прочность корабля, а также исправляет утечки воздуха. Требуется 50 ресурсов.\n"
        "/выстрел - выстрел из орудий. работает при атаке пришельцев"
        "\n"
        "/самоуничтожение - закончить игру (потребуется подтвердить своё решение).\n"
        "/название [название] - изменить название корабля (не более 18 символов).\n"
        "/связь (или /с) [сообщение/название] - устанавливает связь между кораблями. Оставьте [название] пустым, чтобы подключиться к случайному кораблю. Или напишите [название] корабля, чтобы подключиться к нему. после подключения [название] используется для передачи сообщений.\n"
        "/!связь (или /!с) - отключает связь с другим кораблем\n"
        "\n"
        "Путешествуйте по планетам, чтобы собирать ресурсы. С помощью ресурсов вы сможете ремонтировать корабль, создавать предметы и выполнять многие действия."
    )
    await message.answer(text)
