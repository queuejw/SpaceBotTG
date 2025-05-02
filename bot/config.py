from bot.bot_utils import load_config
from utils.planets import get_planets

CONFIG = load_config()

if len(CONFIG) == 0:
    print("Проверьте файл конфигурации.")
    exit(1)

BLOCKED_CHATS: list = CONFIG['blacklist']
ADMINS: list = CONFIG['administrators']
TOKEN = CONFIG['token']
PLANETS = get_planets()
